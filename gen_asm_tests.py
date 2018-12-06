#!/usr/bin/env python3
''' functions for parsing a .test.s file '''
import os
import subprocess
from pathlib import Path
import re
from registers import REGISTER_MAPPINGS
from multiprocessing import Pool

VM_BINARY_START_HW_ADDR = 1 * 1024 * 1024
VM_BINARY_START_SW_ADDR = 1 * 1024 * 1024
DEFAULT_ITERATIONS = 100000
DEFAULT_ENTRYPOINT = 0

test_begin_regex = re.compile(r'test\s*(?:"([^"]*)")?\s*{{\s*\n')
test_stmt_regex = re.compile(r'\s*(?:(inputs|outputs|steps|nold)\s*{{([^}]+)}}|(}}))\s*')
register_assignment_expr_regex = re.compile(r'([a-z][a-z0-9]*)\s+(\-?(?:0x[0-9a-fA-F]+|[0-9]+))')

def parse_register_assignment (statements, register_dict):
    def parse_and_execute_assignment (match):
        name, value = match.group(1, 2)
        if name not in REGISTER_MAPPINGS:
            raise Except 
            ion("Invalid register name: '%s'"%name)

        value = int(value, 0)
        if name in register_dict:
            raise Exception("Already defined '%s' = %d; attempting to override with %d!"%(
                name, register_dict[name], value))
        register_dict[name] = value
        return ''
    rest = re.sub(
        register_assignment_expr_regex, 
        parse_and_execute_assignment, 
        statements
    ).strip()
    if rest:
        raise Exception("Failed to parse all of '%s': '%s'"%(statements, rest))

def count_lines (s):
    return len(list(re.finditer(r'\n', s)))

def parse_test_file (filepath):
    path = Path(filepath)
    if not path.is_file():
        raise Exception("Cannot load '%s' (file does not exist)"%filepath)
    with open(path, 'r') as f:
        lines = f.read()
    filename = os.path.basename(filepath).split('.test.s')[0]

    def parse_testcases (lines, line_num = 0):
        # Try matching all statements:
        matches = list(re.finditer(test_begin_regex, lines))
        testcases = [
            (matches[i].group(1), matches[i].start(),
                lines [
                    matches[i].end() : 
                    (matches[i+1].start() if i + 1 < len(matches) else -1)
                ],
                matches[i].end())
            for i in range(len(matches))
        ]
        eols = [ match.start() for match in re.finditer(r'\n', lines) ]
        def find_line_num (offset):
            for i, n in enumerate(eols):
                if n >= offset:
                    return i + 1
            return eols[-1] + 1

        for i, (name, offset, body, start_index) in enumerate(testcases):
            inputs = {}
            outputs = {}
            steps = DEFAULT_ITERATIONS
            nold = False
            def parse_stmt (match):
                # print(match)
                if match.group(1) == 'inputs':
                    parse_register_assignment(match.group(2), inputs)
                elif match.group(1) == 'outputs':
                    parse_register_assignment(match.group(2), outputs)
                elif match.group(1) == 'steps':
                    m = re.match(r'(\d+)', match.group(2).strip())
                    if m is None:
                        raise Exception("Invalid value for 'steps': '%s'"%m.group(2))
                    nonlocal steps
                    steps = int(m.group(1), 0)
                elif match.group(1) == 'nold':
                    nonlocal nold
                    nold = True
                    # print("set steps to %s"%steps)
                return ''
            body = re.sub(test_stmt_regex, parse_stmt, body)
            testname = '%s.%i'%(filename, i)
            if name:
                testname = '%s.%s'%(testname, re.sub(r'\s+', '-', name))
            yield {
                'name': testname,
                'asm':  body,
                'inputs': inputs,
                'outputs': outputs,
                'steps': steps,
                'nold': nold,
                'entrypoint': inputs['pc'] if 'pc' in inputs else DEFAULT_ENTRYPOINT,
                'srcpath': '%s:%d'%(filepath, find_line_num(offset))
            }
    try:
        tests = list(parse_testcases(lines))
        return True, filename, [], tests
    except Exception as err:
        return False, filename, ["failed to parse '%s':\n\t%s"%(filepath,
            str(err).replace('\n', '\n\t')
        )], None

def gen_test_asm (asm):
    return '%s\n%s\n%s\n'%(
        asm,
        '\n'.join(['addi zero, zero, 0'] * 5),
        'ebreak'
    )

def gen_test_script (inputs, outputs, entrypoint, iterations, hex_file, version, vm_entrypoint=None, vm_file=None):
    if version == 'pa4':
        script = unindent('''
            load /x {vm_entrypoint} {vm_file}
            load /x {entrypoint} {hex_file}
            setptbr {vm_entrypoint}
            setpc {entrypoint}
            {register_writes}
            run {iterations}
            getcycles
            memorystats
            {register_reads}
        ''')
    elif version in ('pa3','pa1'):
        script = unindent('''
            load /x {entrypoint} {hex_file}
            setpc {entrypoint}
            {register_writes}
            run {iterations}
            {register_reads}
        ''')
    else:
        script = unindent('''
            load /x {entrypoint} {hex_file}
            {register_writes}
            run {entrypoint} {iterations}
            {register_reads}
        ''')
    return script.format(
        entrypoint=entrypoint,
        hex_file=hex_file,
        vm_entrypoint=vm_entrypoint,
        vm_file=vm_file,
        iterations=iterations,
        register_writes='\n'.join([
            'writereg %d %d'%(REGISTER_MAPPINGS[reg], value)
            for reg, value in inputs.items()
        ]),
        register_reads='\n'.join([
            'readreg %d'%(REGISTER_MAPPINGS[reg])
            for reg, _ in outputs.items()
        ])
    )

def unindent (s):
    return '\n'.join([ 
        line.strip() 
        for line in s.strip().split('\n')
    ])

def gen_test_output (outputs, srcpath):
    if 'pc' in outputs:
        pc_value = 'pc = %d\n'%outputs['pc']
        del outputs['pc']
    else:
        pc_value = ''

    return '%s\n'%srcpath + pc_value + '\n'.join([
        'R%d = %d'%(REGISTER_MAPPINGS[reg], value)
        for reg, value in outputs.items()
    ]) + '\n'

def assemble_file (
        paths, 
        riscv_as='riscv-as', arch='rv64im',
        riscv_ld='riscv-ld',
        riscv_objcopy='riscv-objcopy',
        od='od',
        ld_script='riscv_sim.ld',
        nold=False,
        version=None,
        **kwargs):

    ok, messages = True, []
    # assemble file
    subprocess.call([
        riscv_as,
        '-march=%s'%arch,
        paths['s'],
        '-o',
        paths['asm.o']
    ])
    if nold:
        paths['ld.o'] = paths['asm.o']
        print("linker disabled")
    else:
        # run linker w/ custom script to fixup offsets
        subprocess.call([
            riscv_ld,
            '--script=%s'%os.path.join(paths['.'], ld_script),
            paths['asm.o'],
            '-o',
            paths['ld.o'],
        ])
    # extract binary
    subprocess.call([
        riscv_objcopy,
        '-O', 'binary',
        '--only-section=.text',
        paths['ld.o'],
        paths['bin']
    ])
    # dump to hex file
    with open(paths['hex'], 'w') as f:
        subprocess.call([od, '-t', 'x1', paths['bin']], stdout=f)
        messages.append("generated '%s'"%paths['hex'])
    return ok, messages

def generate_files_for_test (args):
    test, basepath, kwargs = args
    make_path = lambda suffix: os.path.join(basepath, '{filename}.{suffix}'.format(
            filename=test['name'],
            suffix=suffix))
    filepaths = {
        suffix: make_path(suffix)
        for suffix in (
            'test', 's',
            'asm.o', 'ld.o', 'bin', 'hex',
            'script.pa4', 'script.pa3', 'script.pa1',
            'expected.txt',
            'lastrun.txt'
        )
    }
    filepaths['.'] = os.path.abspath(os.path.join(basepath, '..'))

    results = {}
    ok, log_messages = True, []

    def write_file (filepath, contents):
        with open(filepath, 'w') as f:
            f.write(contents)
        log_messages.append("generated '%s'"%filepath)

    results[filepaths['s']] = gen_test_asm(
        asm=test['asm'])
    write_file(filepaths['s'], results[filepaths['s']])

    if ok:
        ok, msgs = assemble_file(filepaths, nold=test['nold'], **kwargs)
        log_messages += msgs

    results[filepaths['script.pa4']] = gen_test_script(
        version='pa4',
        inputs=test['inputs'],
        outputs=test['outputs'],
        entrypoint=test['entrypoint'] + kwargs['pc_real_address_0'],
        iterations=test['steps'] + 4,
        vm_entrypoint=kwargs['vm_entrypoint'],
        vm_file=kwargs['vm_file'],
        hex_file=filepaths['hex'])

    results[filepaths['script.pa3']] = gen_test_script(
        version='pa3',
        inputs=test['inputs'],
        outputs=test['outputs'],
        entrypoint=test['entrypoint'],
        iterations=test['steps'] + 4,
        hex_file=filepaths['hex'])

    results[filepaths['script.pa1']] = gen_test_script(
        version='pa1',
        inputs=test['inputs'],
        outputs=test['outputs'],
        entrypoint=test['entrypoint'],
        iterations=test['steps'],
        hex_file=filepaths['hex'])

    write_file(filepaths['script.pa4'], results[filepaths['script.pa4']])
    write_file(filepaths['script.pa3'], results[filepaths['script.pa3']])
    write_file(filepaths['script.pa1'], results[filepaths['script.pa1']])

    results[filepaths['expected.txt']] = gen_test_output(
        outputs=test['outputs'],
        srcpath=test['srcpath'])
    write_file(filepaths['expected.txt'], results[filepaths['expected.txt']])
    return True, test['name'], log_messages

def generate_asm_tests (src_dir='tests', gen_dir='generated', verbose = False, nthreads=16, test_filters=None, **kwargs):
    if not os.path.exists(gen_dir):
        os.mkdir(gen_dir)

    files = [
        os.path.join(src_dir, file)
        for file in os.listdir(src_dir)
        if os.path.isfile(os.path.join(src_dir, file))
        and re.search(r'\.test\.s$', os.path.join(src_dir, file))
    ]
    if test_filters:
        print("filtering tests to match '%s'"%', '.join(test_filters))
        matching_files = set()
        for test_filter in test_filters:
            for file in files:
                if test_filter in file:
                    matching_files.add(file)
        files = list(matching_files)
        files.sort()

    if nthreads > 1:
        pool = Pool(nthreads)
        process = lambda f, v: pool.map(f, v)
    else:
        process = map

    test_statuses = {}
    test_testcases = {}
    testcase_statuses = {}

    def parse_testcases ():
        for ok, filename, messages, testcases in process(parse_test_file, files):
            test_statuses[filename] = ok
            if ok:
                test_testcases[filename] = []
                for test in testcases:
                    # check if source file exists and is up to date
                    src_file = os.path.join(src_dir, filename+'.test.s')
                    gen_file = os.path.join(gen_dir, test['name']+'.hex')
                    test_testcases[filename].append(test['name'])
                    testcase_statuses[test['name']] = True
                    if os.path.exists(gen_file) and os.path.getmtime(gen_file) >= os.path.getmtime(src_file):
                        # print(src_file, os.path.getmtime(src_file))
                        # print(gen_file, os.path.getmtime(gen_file))
                        print("skipping generation for '%s' => '%s'"%(src_file, gen_file))
                    else:
                        yield (test, gen_dir, kwargs)
            else:
                print("Failed to parse '%s'"%(filename))
                print('\t' + '\n\t'.join(messages))

    def generate_testcases ():
        tasks = process(generate_files_for_test, parse_testcases())
        passed_tests = 0
        for ok, filename, messages in tasks:
            testcase_statuses[filename] = testcase_statuses[filename] and ok
            if ok:
                print("generated '%s'"%filename)
                if verbose and len(messages) != 0:
                    print('\t' + '\n\t'.join(messages))
                passed_tests += 1
            else:
                print("Failed to generate '%s'"%filename)
                if len(messages) != 0:
                    print('\t' + '\n\t'.join(messages))
        print("generated %d / %d testcases"%(passed_tests, len(testcase_statuses.keys())))


    try:
        generate_testcases()
    except FileNotFoundError as err:
        # check: user may not have the risc-v toolchain installed
        # (this would be catching an error from subprocess.call()
        #  if the binary / command we're referencing doesn't exist)
        required_tools = [ 
            'riscv_as',
            'riscv_ld',
            'riscv_objcopy',
            'od',
        ]
        def has_tool(tool):
            if tool is None:
                return False
            try:
                subprocess.call([ tool, '--help' ])
                return True
            except FileNotFoundError:
                return False
        missing_tools = [
            tool
            for tool in required_tools
            if tool not in kwargs or not has_tool(kwargs[tool])
        ]
        if len(missing_tools) > 0:
            print("Terminating test generation: user environment is missing the following tools:\n\t"+"\n\t".join([
                '%s: %s'%(tool, kwargs[tool] if tool in kwargs else None)
                for tool in missing_tools
            ]))
            return
        else:
            raise err

if __name__ == '__main__':
    generate_asm_tests(nthreads=32, vm_entrypoint=0, vm_file='vm_pages.hex')
