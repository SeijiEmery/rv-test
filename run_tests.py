#!/usr/bin/env python3
import os
import subprocess
import sys
import getopt
from generate import generate_files_from_directory

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
