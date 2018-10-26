test "xori test" {{ 
	inputs {{ x3 0 x4 0 x5 1 x7 1050 x9 0 }}
	outputs {{ x3 0 x4 0 x5 1 x7 1050 x9 1 }}

	xori    x4, x3, 0
    xori    x5, x3, 1

    xori    x7, x3, 1050
	xori 	x8, x3, 1050
	xori	x9, x5, 0

}}
