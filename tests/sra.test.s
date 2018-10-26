test "sra test 1" {{ 
	inputs {{ x1 1 x2 63 }}
	outputs {{ x1 18446744073709551615 x2 63 }}

	sll x1, x1, x2
	sra x1, x1, x2
}}


test "srai test 1" {{
	inputs {{ x1 1 x2 15 x3 16 x4 31 x5 30 x6 44 x7 5 }}
	outputs {{  x1 0 x2 7 x3 8 x4 15 x5 15 x6 22 x7 2 }}

	srai x1, x1, 1
	srai x2, x2, 1
	srai x3, x3, 1
	srai x4, x4, 1
	srai x5, x5, 1
	srai x6, x6, 1
	srai x7, x7, 1

}}

# This is bugged in Miller's framework as of 10/25/18
test "srai test 2" {{ 
	inputs {{ x1 9223372036854775808 }}
	outputs {{ x1 13835058055282163712 }}

	srai x1, x1, 1

}}

test "srai test 3" {{ 
	inputs {{ x1 1 x2 2 x3 3 x4 4 x5 5 x6 6 x7 7 x8 8 x9 9 x10 10 }}
	outputs {{ x1 0 x2 1 x3 1 x4 2 x5 2 x6 3 x7 3 x8 4 x9 4 x10 5 }}

	srai x1, x1, 1
	srai x2, x2, 1
	srai x3, x3, 1
	srai x4, x4, 1
	srai x5, x5, 1
	srai x6, x6, 1
	srai x7, x7, 1
	srai x8, x8, 1
	srai x9, x9, 1
	srai x10, x10, 1

}}

test "srai test 4" {{
	inputs {{ x1 1 x2 63 }}
	outputs {{ x1 13835058055282163712 x2 63 }}

	sll 	x1, x1, x2
	srai 	x1, x1, 1
