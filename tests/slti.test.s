test "slti" {{ 
	inputs {{ x2 1 x3 0 x4 12 x5 -20 x6 -1 x7 -200 }}
	outputs {{ x2 0 x3 0 x4 1 x5 1 x6 1 x7 0 }}

	slti x2, x2, 0
	slti x3, x3, -10
	slti x4, x4, 18
	slti x5, x5, -1
	slti x6, x6, 1000
	slti x7, x7, -400

}}
