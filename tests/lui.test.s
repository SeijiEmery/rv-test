test {{
    outputs {{ a1 0x7F51A000 }}
    steps {{ 1 }}

    lui a1, 0x7F51A
}}
test {{
    outputs {{ a1 0x7F51A000 a2 0x7F51A468 }}
    steps {{ 2 }}

    lui a1, 0x7F51A
    xori a2, a1, 0x468
}}
test {{ 
    inputs  {{ pc 0xffa4 a1 0 }}
    outputs {{ pc 0xffb8 a1 0xFFFFFFFFEF51A000 }}

    lui a1, 0xEF51A
    nop
    nop
    nop
    nop
    ebreak
}}
test {{ 
    inputs  {{ pc 0xffa4 a1 0 }}
    outputs {{ pc 0xffb8 a1 0xFFFFFFFFEF51A000 }}

    lui a1, 0xEF51A
    nop
    nop
    nop
    nop
    ebreak
}}
test {{
    inputs  {{ pc 72 a1 0 }}
    outputs {{ pc 96 a1 0xFFFFFFFFEF51A000 a2 0xFFFFFFFFEF51A468 }}

    lui a1, 0xEF51A
    xori a2, a1, 0x468
    nop
    nop
    nop
    nop
    ebreak
}}
test {{
    inputs  {{ pc 72 a1 0 }}
    outputs {{ pc 96 a1 0xFFFFFFFFFFFFF000 a2 0xFFFFFFFFFFFFF7FF }}

    lui a1, 0xFFFFF
    xori a2, a1, 0x7FF # can't actually store 12 bit value cuz signed! argh....
    nop
    nop
    nop
    nop
    ebreak
}}
