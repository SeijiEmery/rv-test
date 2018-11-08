
test "cascade addition" {{
    inputs {{ a0 3 a1 4 a2 5 a3 6 }}
    outputs {{ a4 18 }}

    add t1, a0, a1
    add t1, t1, a2
    add a4, t1, a3
}}
