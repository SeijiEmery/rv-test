#!/usr/bin/env python3
from pathlib import Path
import os
import re
import subprocess
import itertools
import sys
import getopt
from registers import *

test_begin_regex = re.compile(r'test\s*(?:"([^"]*)")?\s*{{\s*\n')
test_stmt_regex = re.compile(r'\s*(?:(inputs|outputs)\s*{{([^}]+)}}|(}}))\s*')
register_assignment_expr_regex = re.compile(r'([a-z][a-z0-9]*)\s+(\-?[0-9]+)')

def parse_register_assignment (statements, register_dict):
    def parse_and_execute_assignment (match):
        name, value = match.group(1, 2)
        if name not in REGISTER_MAPPINGS:
            raise Exception("Invalid register name: '%s'"%name)

        value = int(value)
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

            # strip indentation
            body = '\n'.join([
                line.strip()
                for line in body.split('\n')
            ]) + '\nebreak\n'

            yield i, name, body, inputs, outputs, 100
    return parse_testcases(lines)

def write_file (path, contents):
    with open(path, 'w') as f:
        f.write(contents)

def unindent (s):
    return '\n'.join([ 
        line.strip() 
        for line in s.strip().split('\n')
    ])

def generate_files (target_dir, results_dir, riscv_as = 'riscv-as', riscv_objcopy = 'riscv-objcopy', od = 'od'):
    def generate (src_file_path):
        testcases = parse_test_file(src_file_path)
        base_name = os.path.basename(src_file_path).strip('.test.s')
        base_path = os.path.join(target_dir, base_name)
        for i, name, body, inputs, outputs, iterations in testcases:
            path = lambda fmt: '%s.%d.%s'%(base_path, i, fmt)
            input_script = unindent('''
                %s
                %s
                %s
                %s
            '''%(
                'load /x 0 %s'%(path('hex')),
                '\n'.join([
                    'writereg %d %d'%(REGISTER_MAPPINGS[reg], value)
                    for reg, value in inputs.items()
                ]),
                'run 0 %d'%iterations,
                '\n'.join([
                    'readreg %d'%(REGISTER_MAPPINGS[reg])
                    for reg, _ in outputs.items()
                ])
            ))
            expected_output = '\n'.join([
                'R%d = %d'%(REGISTER_MAPPINGS[reg], value)
                for reg, value in outputs.items()
            ]) + '\n'

            # Write generated files
            write_file(path('s'), body)
            write_file(path('script'), input_script)
            write_file(path('expected.txt'), expected_output)

            # Run assembler + od to generate binary + .hex files
            subprocess.call('%s %s -o %s'%(
                riscv_as, path('s'), path('elf')), shell=True)
            subprocess.call('%s -O binary --only-section=.text %s %s'%(
                riscv_objcopy, path('elf'), path('bin')), shell=True)
            subprocess.call('%s -t x1 %s > %s'%(
                od, path('bin'), path('hex')), shell=True)
            yield map(os.path.abspath, (
                path('script'), 
                path('lastrun.txt'), 
                path('expected.txt'), 
                os.path.join(results_dir, '%s.%d.diff'%(base_name, i))
            ))
    return generate

def generate_files_from_directory (dir_path, target_dir, results_dir, risc_v_exe):
    files = [
        os.path.join(dir_path, filepath)
        for filepath in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, filepath))
    ]
    # Generate target directory if it doesn't exist
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)

    # Generate files for all tests
    tests = itertools.chain.from_iterable(
        map(
            generate_files(target_dir, results_dir), 
            files
        ))

    shell_code = ''.join([
        "rm -f %s && cat %s | %s | sed 's/^\(RISCV[^>]*> \)*//' > %s && diff %s %s > %s && cat %s\n"%(
            out,
            script, risc_v_exe, out,
            out, expected, diff,
            diff)
        for script, out, expected, diff in tests
    ])
    run_path = os.path.join(target_dir, 'run.sh')
    write_file(run_path, shell_code)
    return map(os.path.abspath, (run_path, results_dir))

def clean_directories (*args):
    import shutil
    for path in args:
        if os.path.isdir(path):
            shutil.rmtree(path)

def run_interactively (program_name, risc_v_exe, src_dir_path):
    cmd = 'when-changed %s %s -c clear; python3 %s %s'%(
        program_name,
        ' '.join([
            os.path.join(src_dir_path, filepath)
            for filepath in os.listdir(src_dir_path)
            if os.path.isfile(os.path.join(src_dir_path, filepath))
        ]), program_name, risc_v_exe)
    print(cmd)
    subprocess.call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def run (risc_v_exe):
    clean_directories('./generated', './results')
    shell_file, results_dir = generate_files_from_directory(
        './tests', './generated', './results', risc_v_exe)
    print(shell_file)
    print(results_dir)
    subprocess.call([ 'bash', shell_file ])

    # for file in os.listdir('results'):
    #     subprocess.call([ 'echo', file ])
    #     subprocess.call([ 'cat', os.path.join('results', file) ])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s clean | [-i] <path-to-your-riscv-executable>'%sys.argv[0])
        sys.exit(-1)
    if len(sys.argv) == 2 and sys.argv[1] == 'clean':
        clean_directories('generated', 'results')
        sys.exit(0)
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i', ['interactive='])
        # print(opts)
        # print(args)
        for opt, arg in opts:
            if opt in ('-i', 'interactive'):
                run_interactively(sys.argv[0], args[0], 'tests')
                sys.exit(0)
        
        run(args[0])
        sys.exit(0)

    except getopt.GetoptError:
        print('usage: %s clean | [-i] <path-to-your-riscv-executable>')
        sys.exit(-1)
