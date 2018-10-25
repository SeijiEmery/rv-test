#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import getopt
from generate import generate_files_from_directory
from clean import clean_generated_files
import difflib

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

def run_test (risc_v_executable, dir = 'generated', results_dir = 'results'):
    def run (test):
        print("\033[36mRunning test: '%s'\033[0m"%test)
        with open(os.path.join(dir, test + '.script'), 'rb') as input_file:
            input_script = input_file.read()
        try:
            result = subprocess.run(
                risc_v_executable, 
                input=input_script,
                capture_output = True
            )
            output = result.stdout.decode('utf-8')
            err = result.stderr.decode('utf-8')
            returncode = result.returncode
            with open(os.path.join(dir, test + '.lastrun.txt'), 'w') as f:
                f.write(output)
        except TypeError: # python < 3.7
            infile = open(os.path.join(dir, test + '.script'), 'rb')
            outfile = open(os.path.join(dir, test + '.lastrun.txt'), 'w+')
            p = subprocess.Popen(
                risc_v_executable,
                stdin=infile,
                stdout=outfile,
                stderr=sys.stderr)
            p.wait()
            returncode = p.returncode
            err = ''
            infile.close()
            outfile.close()
            with open(os.path.join(dir, test + '.lastrun.txt'), 'r') as outfile:
                output = outfile.read()

        if returncode != 0:
            print("\033[31mTest Failed: returned %s\033[0m"%returncode)
            print(err)
            return False

        output = re.sub(r'RISCV[^>]*>\s*', '', output)
        with open(os.path.join(dir, test + '.expected.txt'), 'r') as f:
            expected = f.read()
        diff = '\n'.join([
            line for line in
                difflib.ndiff(expected.split('\n'), output.split('\n'))
            if line[0] not in (' ', '?')
        ])
        with open(os.path.join(results_dir, test + '.diff'), 'w') as f:
            f.write(diff)
        if len(diff.strip()) != 0:
            print("\033[31mTest Failed (output diff):\033[0m")
            print(diff)
            return False

        print("\033[32mTest Passed!\033[0m")
        return True
    return run


def run_tests (risc_v_executable, dir = 'generated', results_dir = 'results'):
    if not os.path.isdir(dir):
        os.mkdir(dir)
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)

    tests_passed, tests_failed = 0, 0
    tests = [ 
        "%s.%s"%match.group(1, 2)
        for match in [ 
            re.match(r'([^\.]+)\.(\d+)\.script', filename) 
            for filename in os.listdir(dir)
        ]
        if match is not None
    ]
    print("Found tests: '%s'"%tests)
    for test_result in map(run_test(risc_v_executable), tests):
        if test_result == True:
            tests_passed += 1
        else:
            tests_failed += 1

    if tests_failed == 0:
        print("\033[32mAll tests passed!\033[0m")
    else:
        print("\033[31m%d / %d tests passed\033[0m"%(tests_passed, tests_passed + tests_failed))

def run (risc_v_exe, rebuild = True):
    if rebuild:
        clean_generated_files()
        generate_files_from_directory(
            'tests', 'generated', 'results', risc_v_exe)
    run_tests(risc_v_exe)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s clean | [-i] <path-to-your-riscv-executable>'%sys.argv[0])
        sys.exit(-1)
    if len(sys.argv) == 2 and sys.argv[1] == 'clean':
        clean_generated_files()
        sys.exit(0)
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i', ['interactive='])
        for opt, arg in opts:
            if opt in ('-i', 'interactive'):
                run_interactively(sys.argv[0], args[0], 'tests')
                sys.exit(0)
        
        run(args[0])
        sys.exit(0)

    except getopt.GetoptError:
        print('usage: %s clean | [-i] <path-to-your-riscv-executable>')
        sys.exit(-1)
