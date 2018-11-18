#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import getopt
from gen_asm_tests import generate_asm_tests
from clean import clean_generated_files
from registers import REGISTER_TO_STR
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

def run_test (risc_v_executable, dir = 'generated', results_dir = 'results', verbose_test_output = False, using_old_framework=False, **kwargs):
    def run (test):
        print("\033[36mRunning test: '%s'\033[0m"%test)
        if using_old_framework:
            script_path = os.path.join(dir, test+'.script.old')
        else:
            script_path = os.path.join(dir, test+'.script')
        with open(script_path, 'rb') as input_file:
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
            with open(os.path.join(dir, test + '.last_debug.txt'), 'w') as f:
                f.write(err)
        except TypeError: # python < 3.7
            infile = open(script_path, 'rb')
            outfile = open(os.path.join(dir, test + '.lastrun.txt'), 'w+')
            errfile = open(os.path.join(dir, test + '.last_debug.txt'), 'w+')
            p = subprocess.Popen(
                risc_v_executable,
                stdin=infile,
                stdout=outfile,
                stderr=errfile)
            p.wait()
            returncode = p.returncode
            err = ''
            infile.close()
            outfile.close()
            errfile.close()
            with open(os.path.join(dir, test + '.lastrun.txt'), 'r') as outfile:
                output = outfile.read()
            with open(os.path.join(dir, test + '.last_debug.txt'), 'r') as errfile:
                err = errfile.read()

        if returncode != 0:
            print("\033[31mTest Failed: returned %s\033[0m"%returncode)
            print(err)
            return False

        output = re.sub(r'RISCV[^>]*>\s*', '', output)
        with open(os.path.join(dir, test + '.expected.txt'), 'r') as f:
            expected = f.read()

        expected_values = {}
        for match in re.finditer(r'R(\d+)\s*=\s*(-?\d+[xX]?\d*)', expected):
            reg, value = match.group(1, 2)
            expected_values[REGISTER_TO_STR[int(reg)]] = int(value)

        test_ok = True
        for match in re.finditer(r'R(\d+)\s*=\s*(-?\d+[xX]?\d*)', output):
            reg, value = match.group(1, 2)
            reg = REGISTER_TO_STR[int(reg)]
            value = int(value)
            v2    = -((abs(value) ^ ((1 << 64) - 1)) + 1)
            if reg in expected_values:
                if value != expected_values[reg] and v2 != expected_values[reg]:
                    print("\033[31m%s: expected '%s',\033[0m got '%s' (%s)"%(
                        reg, expected_values[reg], value, v2))
                    test_ok = False
                elif verbose_test_output:
                    print("\033[35m%s: got '%s' (%s)\033[0m"%(
                        reg, value, v2))
                del expected_values[reg]
            else:
                print("\033[31m%s: unexpected value\033[0m '%s' (%s)"%(
                    reg, value, v2))
                test_ok = False

        for reg, value in expected_values.items():
            v2 = -((abs(value) ^ ((1 << 64) - 1)) + 1)
            print("\033[31m%s: missing, expected value\033[0m '%s' (%s)"%(
                reg, value, v2))
            test_ok = False

        if test_ok:
            print("\033[32mTest Passed!\033[0m")
            if verbose_test_output:
                print("\033[36moutput:\033[0m")
                print(err)
            return True
        else:
            print("\033[36moutput:\033[0m")
            print(err)
            print("\033[31mTest Failed\033[0m")
            return False
    return run


def run_tests (risc_v_executable, dir = 'generated', results_dir = 'results', stop_after_failing_tests = False, **kwargs):
    if not os.path.isdir(dir):
        os.mkdir(dir)
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)

    tests_passed, tests_failed = 0, 0
    tests = [ 
        "%s.%s"%match.group(1, 2)
        for match in [ 
            re.match(r'([^\.]+)\.(\d+(?:\.[^\.]+)?)\.hex', filename) 
            for filename in os.listdir(dir)
        ]
        if match is not None
    ]
    tests.sort()
    print("Found tests: '%s'"%tests)
    for test_result in map(run_test(risc_v_executable, **kwargs), tests):
        if test_result == True:
            tests_passed += 1
        else:
            tests_failed += 1
            if stop_after_failing_tests:
                return

    if tests_failed == 0:
        print("\033[32mAll tests passed!\033[0m")
    else:
        print("\033[31m%d / %d tests passed\033[0m"%(tests_passed, tests_passed + tests_failed))


def run (risc_v_exe, generate=True, rebuild = True, **kwargs):
    if generate:
        generate_asm_tests(
            src_dir='tests', 
            gen_dir='generated',
            **kwargs)
    else:
        print("Test generation disabled – reusing exising tests (if present)")
    if risc_v_exe:
        run_tests(risc_v_exe, **kwargs)
    else:
        print("no risc-v executable provided, skipping test execution")

def display_cli_help():
    print('\n'.join("""
        rv-test: Automated testing for CMPE 110

        usage: 
            python3 run_tests.py [options] <path-to-your-riscv-executable> <riscv args>
        
        options: 
            –h, --help      display this message
            -v, --verbose   turns on extra verbosity in test output

            --nogen         turns off test generation
                            (so you can still run the tests even if you don't have 
                             a riscv toolchain installed)
    
            --clean         cleans all generated test files
    
            --strict        turns on strict mode: test execution will stop at the first
                            failing test. useful if you're trying to focus on a few
                            failing tests
            
            -A, --as        set the risc-v assembler (set with --as=<your-riscv-as>)
            -L, --ld        set the risc-v linker    (set with --as=<your-riscv-ld>)
            -O, --objcopy   set the risc-v objcopy   (set with --as=<your-riscv-objcopy>)
            -j, --parallel  sets the # of work threads (processes) used in part of rv-test
                            usage: -j=1  (disable multiprocessing)
                                   -j=32 (run w/ 32 workers) 
    
            --old           runs with .old.script input files instead of .script files
                            this is just so you can run the original version of miller's framework
                            since some of the commands changed
    """.split('\n        ')))

def main (**kwargs):
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hjiA:OLv', ['help', 'old', 'nogen', 'clean', 'strict', 'interactive=', 'as=', 'objcopy=', 'ld=', 'verbose=', 'parallel='])
        for opt, arg in opts:
            if opt in ('-i', '--interactive'):
                run_interactively(sys.argv[0], args[0], 'tests')
                sys.exit(0)
            elif opt in ('-A', '--as'):
                kwargs['riscv_as'] = arg
            elif opt in ('-O', '--objcopy'):
                kwargs['riscv_objcopy'] = arg
            elif opt in ('-L', '--ld'):
                kwargs['riscv_ld'] = arg
            elif opt in ('-v', '--verbose'):
                kwargs['verbose_test_output'] = True
                kwargs['verbose'] = True
            elif opt in ('-j', '--parallel'):
                kwargs['nthreads'] = int(arg)
            elif opt in ('--old',):
                kwargs['using_old_framework'] = True
            elif opt in ('--strict',):
                kwargs['stop_after_failing_tests'] = True
            elif opt in ('--nogen',):
                kwargs['generate'] = False
            elif opt in ('-h', '--help'):
                display_cli_help()
                sys.exit(0)
            elif opt in ('--clean',):
                clean_generated_files()
        run(args if len(args) > 0 else None, **kwargs)
        sys.exit(0)
    except getopt.GetoptError:
        print('usage: %s [opts] <path-to-your-riscv-executable>')
        sys.exit(-1)

if __name__ == '__main__':
    main()
