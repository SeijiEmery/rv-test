
test "addition test" {{
    inputs  {{ x1 1 x2 2 x3 99 }}
    outputs {{ x1 3 x2 2 x3 3 }}

    add x3, x1, x2
    add x1, x1, x2
}}
