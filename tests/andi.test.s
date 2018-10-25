
test "andi test" {{
	inputs {{ x3 0 x4 0 x5 0 x6 0 x7 0 }}
	outputs {{ x3 0 x4 0 x5 0 x6 0 x7 0 }}

	andi    x4, x3, 1
    andi    x5, x3, 0x7FF
    andi    x6, x3, 0xFF
    andi    x7, x3, 0
}}
