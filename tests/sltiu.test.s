test "slti" {{ 
	inputs {{ x2 1 x3 0 x4 12 x5 -20 x6 -1 x7 -200 }}
	outputs {{ x2 0 x3 1 x4 1 x5 1 x6 0 x7 0 }}

	sltiu x2, x2, 0
	sltiu x3, x3, -10
	sltiu x4, x4, 18
	sltiu x5, x5, -1
	sltiu x6, x6, 1000
	sltiu x7, x7, -400

}}
