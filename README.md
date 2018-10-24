# rv-test

This is an automated testing program that runs against any implementation of prof miller's risc-v assignment for CMPE 110.

## Installing + running

To install:
	
	git clone https://github.com/SeijiEmery/rv-test.git
	cd rv-test
	chmod +x ./run_tests.py
	
To run:
	
	./run_tests.py <path-to-your-risc-v-executable>
	
To clean:

	./run_tests.py clean
	
To run interactively:

	./run_tests.py -i <path-to-your-risc-v-executable>
	
Note: this last mode means that the program will just use when-changed to re-run itself whenever any of the source files in tests/ are changed. You need to have when-changed - get it here: <https://github.com/joh/when-changed>

Note 2: do not use this command as it currently is extremely broken.

## Test files

Test files are all of the files in tests/ and have a .test.s extension.

The format of these files is fairly simple: they consist of sequences of testcases that consist of risc-v assembly and a small DSL.

	test [optional name] {{
		inputs {{ register-starting-values-here }}
		outputs {{ expected-register-values-here }}
		risc-v assembly code here...
	}}
	
## Contributing

I am taking / would appreciate pull requests to add more testcases so we can reach full compliance. If you want to, feel free to just pull tests from here: <https://github.com/riscv/riscv-compliance/tree/master/riscv-test-suite>

## How this all works:

Tests are loaded from all the source files in `tests/*.test.s` and parsed to extract the assembly code and metadata (ie. register input / output values) for each test function.

Assembly for each test case is written into a separate files in the `generated/` directory, then assembled using `riscv-as`, extracted with `riscv-objcopy -O binary --only-section=.text`, and dumped to hex with `od -t x1`. 

"Script" files are also generated, which are just input commands piped into your riscv executable, and a shell file is generated, `generated/run.sh` that runs + diffs all this stuff, with testrun outputs written to `results/`.

Lastly, the `run_tests.py` script checks all diffs and prints out which test cases passed (no diff) / failed (diff between the output and a generated .expected file). Currently this last part is TBD.

## Dependencies

You must have the risc-v toolchain installed, and the risc-v assembler and objcopy commands aliased / linked to as `riscv-as` and `riscv-objcopy`. Alternatively, use the `--with-as` and `--with-objcopy` flags (TBD).

<https://github.com/riscv/riscv-tools>

If you're on osx install this through brew:

<https://github.com/riscv/homebrew-riscv>

<https://brew.sh>

Also, I would strongly recommend getting <https://github.com/joh/when-changed>

## Credits

Many thanks to Samuel Armold for his help in figuring out how some of the more annoying parts of this should work.
