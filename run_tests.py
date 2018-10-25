#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import getopt
from generate import generate_files_from_directory
from clean import clean_generated_files

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

def run (risc_v_exe, riscv_as=None, riscv_objcopy=None):
    clean_generated_files()
    shell_file, results_dir = generate_files_from_directory(
        './tests', './generated', './results', risc_v_exe, riscv_as=riscv_as, riscv_objcopy=riscv_objcopy)
    print(shell_file)
    print(results_dir)
    subprocess.call([ 'bash', shell_file ])

def summarize (tests_dir = 'tests', results_dir = 'results'):
    tests_passed, tests_failed = 0, 0
    for filename in os.listdir(results_dir):
        match = re.match(r'([^\.]+)\.(\d+)\.diff', filename)
        if not match:
            print("Skipping '%s'"%filename)
            continue
        testname, testnum = match.group(1, 2)
        with open(os.path.join(results_dir, filename), 'r') as f:
            contents = f.read()
        if len(contents.strip()) == 0:
            print("\033[32mTest passed:\033[0m %s.%s"%(testname, testnum))
            tests_passed += 1
        else:
            print("\033[31mTest failed:\033[0m %s.%s"%(testname, testnum))
            # with open(os.path.join(tests_dir, '%s.test.s'%testname)) as f:
            #     print(f.read())
            print('\t'+'\n\t'.join(contents.strip().split('\n')))
            tests_failed += 1

    if tests_failed == 0:
        print("\033[32mAll tests passed!\033[0m")
    else:
        print("\033[31m%d / %d tests passed\033[0m"%(tests_passed, tests_passed + tests_failed))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s clean | [-i] <path-to-your-riscv-executable>'%sys.argv[0])
        sys.exit(-1)
    if len(sys.argv) == 2 and sys.argv[1] == 'clean':
        clean_generated_files()
        sys.exit(0)
    try:
        generate_options = {}
        opts, args = getopt.getopt(sys.argv[1:], 'iA:O:', ['interactive=', 'as=', 'objcopy='])
        for opt, arg in opts:
            if opt in ('-i', '--interactive'):
                run_interactively(sys.argv[0], args[0], 'tests')
                sys.exit(0)
            elif opt in ('-A', '--as'):
                generate_options['riscv_as'] = arg
            elif opt in ('-O', '--objcopy'):
                generate_options['riscv_objcopy'] = arg
        
        run(args[0], **generate_options)
        summarize()
        sys.exit(0)

    except getopt.GetoptError:
        print('usage: %s clean | [-i] <path-to-your-riscv-executable>')
        sys.exit(-1)
