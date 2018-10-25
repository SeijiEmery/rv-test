
test "addition test" {{
    inputs  {{ x1 1 x2 2 x3 99 }}
    outputs {{ x1 3 x2 2 x3 3 }}

    add x3, x1, x2
    add x1, x1, x2
}}

test "test 2" {{
    inputs {{ x1 10 x2 10 }}

    addi x1, x0, 10
    addi x2, x1, 10

    outputs {{ x1 10 x2 20 }}
}}

# Note that test names are optional (and currently unused)
test {{
    outputs {{ x0 0 }}
    addi x0, x0, 22
}}
