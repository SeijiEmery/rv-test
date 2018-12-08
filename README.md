# rv-test

This is an automated testing program that runs against any implementation of prof miller's risc-v assignment for CMPE 110.

## Installing + running

To install:
	
	git clone https://github.com/SeijiEmery/rv-test.git
	cd rv-test
	chmod +x ./run_tests.py
	chmod +x ./clean.py
	
To run:
	
	./run_tests.py <args...> [<path-to-your-risc-v-executable>]
	
To clean:

	./run_tests.py clean
	
or

	./clean.py

### Commandline arguments:
	
	--help 			(prints CLI argument options)
	-v, --verbose 	(prints more stuff)
	-j, --parallel 	(sets # threads used for generation phase)
	-old 			(runs against the framework version from PA1)
	--strict 		(stops after first failing test)
	--nogen 		(disables generation - use if you don't have the riscv toolchain installed)
	--filter <name> (generates / runs only tests whose name matches a simple substring filter)
					eg. --filter mul
	--rebuild 		(cleans and rebuilds all generated files)
	--clean 		(removes all generated files)

	-A, --as		(sets the risc-v assembler (default: `riscv-as`))
	-L, --ld 		(sets the risc-v linker (default: `riscv-ld`))
	-O, --objcopy 	(sets the risc-v objcopy (default: `riscv-objcopy`))

### What this does:

run_tests.py will by default rebuild all the testcases (tests/\*.test.s) that are out of date, and will run said tests if a risc-v executable is provided. To rebuild all tests, use `--rebuild`. To NOT rebuild any tests, use `--nogen`.

Test generation will ONLY work if you have the risc-v toolchain installed.

If you do not, you can use the `prebuilt` branch, which should work by default unless you modify any of the tests/\*.test.s files. If you do, use `git reset --hard`.

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

Diffs are then checked and passing / failing tests are then summarized.

## Dependencies

You must have the risc-v toolchain installed, and the risc-v assembler and objcopy commands aliased / linked to as `riscv-as` and `riscv-objcopy`. Alternatively, use the `--with-as` and `--with-objcopy` flags (TBD).

<https://github.com/riscv/riscv-tools>

If you're on osx install this through brew:

<https://github.com/riscv/homebrew-riscv>

<https://brew.sh>

Also, I would strongly recommend getting <https://github.com/joh/when-changed>

## Credits

Many thanks to Samuel Armold for his help in figuring out how some of the more annoying parts of this should work.
