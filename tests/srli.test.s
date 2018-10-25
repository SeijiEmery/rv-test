test "srli test" {{
	inputs {{ x1 1 x2 0 x3 31 x4 64 x5 62 }}
	outputs {{ x1 0 x2 0 x3 15 x4 32 x5 31 }}

	srli x1, x1, 1
	srli x2, x2, 1
	srli x3, x3, 1
	srli x4, x4, 1
	srli x5, x5, 1

}}

