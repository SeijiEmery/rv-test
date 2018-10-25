test "xor test" {{ 
	inputs {{ x3 0 x4 0 x5 1 x7 2147483647 x8 2147483648 x9 0 }}
	outputs {{ x3 0 x4 0 x5 1 x7 2147483647 x8 2147483648 x9 0 }}

	xor     x4, x3, x4
    xor     x5, x3, x5

    xor     x7, x3, x7
	xor 	x8, x3, x8
	xor		x9, x5, x5

}}
