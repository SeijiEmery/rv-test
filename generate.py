#!/usr/bin/env python3
import os
import itertools
import subprocess
from registers import REGISTER_MAPPINGS
from parse_file import parse_test_file
import re

def write_file (path, contents):
    with open(path, 'w') as f:
        f.write(contents)

def unindent (s):
    return '\n'.join([ 
        line.strip() 
        for line in s.strip().split('\n')
    ])

def generate_files (target_dir, results_dir, riscv_as = 'riscv-as', riscv_ld = 'riscv-ld', riscv_objcopy = 'riscv-objcopy', od = 'od', do_link=False):
    def generate (src_file_path):
        testcases = parse_test_file(src_file_path)
        base_name = os.path.basename(src_file_path).strip('.test.s')
        base_path = os.path.join(target_dir, base_name)
        for i, name, body, inputs, outputs, iterations in testcases:
            testpathname = '%s.%d%s'%(base_path, i, 
                ('.' + re.sub(r'\s+', '-', name) if name else ''))
            print(testpathname)
            path = lambda fmt: '%s.%s'%(testpathname, fmt)
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

            def twos_complement (value, n=64):
                if value >= 0:
                    return value
                mask = 2 ** (n - 1)
                return -(value & mask) + (value & ~mask)

            def to_unsigned (value, n=64):
                return abs(twos_complement(value, n))

            expected_output = '\n'.join([
                'R%d = %d'%(REGISTER_MAPPINGS[reg], to_unsigned(value))
                for reg, value in outputs.items()
            ]) + '\n'

            # Write generated files
            write_file(path('s'), body)
            write_file(path('script'), input_script)
            write_file(path('expected.txt'), expected_output)

            # Run assembler + od to generate binary + .hex files
            subprocess.call('%s "%s" -o "%s"'%(
                riscv_as, path('s'), path('as.o')), shell=True)
            objfile = path('as.o')

            if do_link:
                subprocess.call('%s --script="%s" -o "%s" "%s"'%(
                    riscv_ld, os.path.abspath(os.path.join(target_dir, '..', 'riscv_sim.ld')), 
                    path('ld.o'), objfile), shell=True)
                objfile = path('ld.o')

            subprocess.call('%s -O binary --only-section=.text "%s" "%s"'%(
                riscv_objcopy, objfile, path('bin')), shell=True)
            subprocess.call('%s -t x1 "%s" > "%s"'%(
                od, path('bin'), path('hex')), shell=True)
            yield map(os.path.abspath, (
                path('script'), 
                path('lastrun.txt'), 
                path('expected.txt'), 
                os.path.join(results_dir, '%s.diff'%(testpathname))
            ))
    return generate


def generate_files_from_directory (dir_path, target_dir, results_dir, risc_v_exe, **kwargs):
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
    tests = list(itertools.chain.from_iterable(
        map(
            generate_files(target_dir, results_dir, **kwargs),
            files
        )))
