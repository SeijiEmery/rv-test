#!/usr/bin/env python3
''' functions for parsing a .test.s file '''
import os
import subprocess
from pathlib import Path
import re
from registers import REGISTER_MAPPINGS
from multiprocessing import Pool

test_begin_regex = re.compile(r'test\s*(?:"([^"]*)")?\s*{{\s*\n')
test_stmt_regex = re.compile(r'\s*(?:(inputs|outputs)\s*{{([^}]+)}}|(}}))\s*')
register_assignment_expr_regex = re.compile(r'([a-z][a-z0-9]*)\s+(\-?(?:0x[0-9a-fA-F]+|[0-9]+))')

def parse_register_assignment (statements, register_dict):
    def parse_and_execute_assignment (match):
        name, value = match.group(1, 2)
        if name not in REGISTER_MAPPINGS:
            raise Exception("Invalid register name: '%s'"%name)

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
            (matches[i].group(1), 
                lines [
                    matches[i].end() : 
                    (matches[i+1].start() if i + 1 < len(matches) else -1)
                ],
                matches[i].end())
            for i in range(len(matches))
        ]
        for i, (name, body, start_index) in enumerate(testcases):
            inputs = {}
            outputs = {}
            def parse_stmt (match):
                # print(match)
                if match.group(1) == 'inputs':
                    parse_register_assignment(match.group(2), inputs)
                elif match.group(1) == 'outputs':
                    parse_register_assignment(match.group(2), outputs)
                return ''
            body = re.sub(test_stmt_regex, parse_stmt, body)

            testname = '%s.%i'%(filename, i)
            if name:
                testname = '%s.%s'%(testname, re.sub(r'\s+', '-', name))
            yield {
                'name': testname,
                'asm':  body,
                'inputs': inputs,
                'outputs': outputs
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
        '\n'.join(['nop'] * 5),
        'ebreak'
    )

def gen_test_script (inputs, outputs, hex_file, run_cmd = 'run {iterations}', iterations=1000, entrypoint_address=0):
    return unindent('''
        load /x {entrypoint} {hex_file}
        {register_writes}
        {run_cmd}
        {register_reads}
    '''.format(
        entrypoint = entrypoint_address,
        hex_file  = hex_file,
        run_cmd   = run_cmd.format(
            entrypoint=entrypoint_address,
            iterations=iterations
        ),
        register_writes = '\n'.join([
            'writereg %d %d'%(REGISTER_MAPPINGS[reg], value)
            for reg, value in inputs.items()
        ]),
        register_reads = '\n'.join([
            'readreg %d'%(REGISTER_MAPPINGS[reg])
            for reg, _ in outputs.items()
        ])
    ))

def unindent (s):
    return '\n'.join([ 
        line.strip() 
        for line in s.strip().split('\n')
    ])

def gen_test_output (outputs):
    return '\n'.join([
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
        messages.append(["generated '%s'"%paths['hex']])
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
            'script', 'script.old',
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
        ok, msgs = assemble_file(filepaths, **kwargs)
        log_messages += msgs

    results[filepaths['script']] = gen_test_script(
        inputs=test['inputs'],
        outputs=test['outputs'],
        hex_file=filepaths['hex'],
        run_cmd='setpc {entrypoint}\nrun {iterations}')
    write_file(filepaths['script'], results[filepaths['script']])

    results[filepaths['script.old']] = gen_test_script(
        inputs=test['inputs'],
        outputs=test['outputs'],
        hex_file=filepaths['hex'],
        run_cmd='run {entrypoint} {iterations}')
    write_file(filepaths['script.old'], results[filepaths['script.old']])

    results[filepaths['expected.txt']] = gen_test_output(
        outputs=test['outputs'])
    write_file(filepaths['expected.txt'], results[filepaths['expected.txt']])
    return True, test['name'], log_messages

def generate_asm_tests (src_dir='tests', gen_dir='generated', verbose = False, nthreads=1, **kwargs):
    if not os.path.exists(gen_dir):
        os.mkdir(gen_dir)

    files = [
        os.path.join(src_dir, file)
        for file in os.listdir(src_dir)
        if os.path.isfile(os.path.join(src_dir, file))
        and re.search(r'\.test\.s$', os.path.join(src_dir, file))
    ]
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

if __name__ == '__main__':
    generate_asm_tests(nthreads=32)
