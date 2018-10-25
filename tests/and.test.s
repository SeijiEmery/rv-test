test "and test" {{ 
    inputs {{ x1 0 x2 2 x3 4 x4 4294967297 x5 -1 x6 2147483648 }}
    outputs {{ x1 0 x2 0 x3 0 x4 0 x5 0 x6 0 }}

    and x2, x1, x2
    and x3, x1, x3
    and x4, x1, x4
    and x5, x1, x5
    and x6, x1, x6

}}
