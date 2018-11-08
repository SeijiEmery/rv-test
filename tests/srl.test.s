test "srl test" {{
	inputs {{ x1 1 x2 0 x3 31 x4 64 x5 62 x6 1152921504606846976 }}
	outputs {{ x1 0 x2 0 x3 15 x4 32 x5 62 x6 0 }}

	srl x2, x2, x1
	srl x3, x3, x1
	srl x4, x4, x1

	srl x6, x6, x5
	srl x1, x1, x1

}}
