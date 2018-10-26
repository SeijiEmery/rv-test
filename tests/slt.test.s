test "slt" {{ 
	inputs {{ x2 1 x3 0 x4 12 x5 -20 x6 -1 x7 -200 x8 0 x9 -10 x10 18 x11 -1 x12 1000 x13 -400 }}
	outputs {{ x2 0 x3 0 x4 1 x5 1 x6 1 x7 0 }}

	slt x2, x2, x8
	slt x3, x3, x9
	slt x4, x4, x10
	slt x5, x5, x11
	slt x6, x6, x12
	slt x7, x7, x13

}}
