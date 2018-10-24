
# Note that 
test "addition test" {{
    inputs  {{ x1 1 x2 2 x3 99 }}
    outputs {{ x1 3 x2 2 x3 3 }}

    add x3, x1, x2
    add x1, x1, x2
}}

test "test 2" {{
    inputs{{ x1 10 }}
    addi x1, x0, 10
}}
