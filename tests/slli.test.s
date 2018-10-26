test "slli test" {{ 
	inputs {{ x1 1 x2 2 x3 0 x4 31 }}
	outputs {{ x1 1 x2 4 x3 0 x4 62 }}

	slli x2, x2, 1
	slli x3, x3, 1
	slli x4, x4, 1

}}

test "slli test 2" {{ 
	inputs {{ x1 7 x2 1 x3 1024 }}
	outputs {{ x1 1792 x2 256 x3 262144 }}

	slli x1, x1, 8
	slli x2, x2, 8
	slli x3, x3, 8

}}
