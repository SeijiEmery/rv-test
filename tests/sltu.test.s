test "sltu" {{ 
	inputs {{ x2 1 x3 0 x4 12 x5 -20 x6 -1 x7 -200 x8 0 x9 -10 x10 18 x11 -1 x12 1000 x13 -400 }}
	outputs {{ x2 0 x3 1 x4 1 x5 1 x6 0 x7 0 }}

	sltu x2, x2, x8
	sltu x3, x3, x9
	sltu x4, x4, x10
	sltu x5, x5, x11
	sltu x6, x6, x12
	sltu x7, x7, x13

}}
