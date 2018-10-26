test "sra test 1" {{ 
	inputs {{ x1 1 x2 63 }}
	outputs {{ x1 18446744073709551615 x2 63 }}

	sll x1, x1, x2
	sra x1, x1, x2
}}


test "srai test 1" {{
	inputs {{ x1 1 x2 15 x3 16 }}
	outputs {{  x1 0 x2 7 x3 8 }}

	srai x1, x1, 1
	srai x2, x2, 1
	srai x3, x3, 1

}}


test "srai test 2" {{ 
	inputs {{ x1 9223372036854775808 }}
	outputs {{ x1 13835058055282163712 }}

	srai x1, x1, 3

}}
