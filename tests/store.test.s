
test {{
    inputs  {{ a0 16045690984833335023 }}
    outputs {{ 
        a0 16045690984833335023 
        a1 16045690984833335023
        a2 3735928559
        a3 48879
        a4 239
    }}
    addi t1, zero, 200
    sd   a0, 0(t1)
    sw   a0, 8(t1)
    sh   a0, 16(t1)
    sb   a0, 24(t1)

    ld   a1, 0(t1)
    ld   a2, 8(t1)
    ld   a3, 16(t1)
    ld   a4, 24(t1)
}}

test {{
    inputs  {{ a0 255 }}
    outputs {{ 
        a0 255 
        a1 255
        a2 255
        a3 255
        a4 255
    }}
    addi t1, zero, 200
    sd   a0, 0(t1)
    sw   a0, 8(t1)
    sh   a0, 16(t1)
    sb   a0, 24(t1)

    ld   a1, 0(t1)
    ld   a2, 8(t1)
    ld   a3, 16(t1)
    ld   a4, 24(t1)
}}

test {{
    inputs  {{ a0 4099 }}
    outputs {{ 
        a0 4099 
        a1 4099
        a2 4099
        a3 4099
        a4 3
    }}
    addi t1, zero, 200
    sd   a0, 0(t1)
    sw   a0, 8(t1)
    sh   a0, 16(t1)
    sb   a0, 24(t1)

    ld   a1, 0(t1)
    ld   a2, 8(t1)
    ld   a3, 16(t1)
    ld   a4, 24(t1)
}}
