test "sll test" {{ 
	inputs {{ x1 1 x2 2 x3 0 x4 31 }}
	outputs {{ x1 1 x2 4 x3 0 x4 62 }}

	sll x2, x2, x1
	sll x3, x3, x1
	sll x4, x4, x1

}}

test "sll test 2" {{ 
	inputs {{ x3 124 x4 1 x5 1 x6 63 }}
	outputs {{ x3 124 x4 1152921504606846976 x5 9223372036854775808 x6 63  }}

	sll x4, x4, x3
	sll x5, x5, x6
}}
