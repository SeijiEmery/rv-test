import sys
from run_tests import run

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s <path-to-your-riscv-executable>'%sys.argv[0])
        sys.exit(-1)
    run(sys.argv[1], rebuild=False)
