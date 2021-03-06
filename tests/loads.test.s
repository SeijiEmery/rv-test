
test {{
    inputs  {{ a0 16045690984833335023 gp 0x600000 }}
    outputs {{ 
        a0 16045690984833335023 
        a1 16045690984833335023
        a2 3735928559
        a3 48879
        a4 239
        a5 18446744073150512879
        a6 18446744073709534959
        a7 18446744073709551599
    }}
    sd a0,  0(gp)
    ld a1,  0(gp)
    lwu a2, 0(gp)
    lhu a3, 0(gp)
    lbu a4, 0(gp)
    lw a5,  0(gp)
    lh a6,  0(gp)
    lb a7,  0(gp)
}}

test {{
    inputs  {{ a0 10 gp 0x600000 }}
    outputs {{ a1 10 a2 10 a3 10 a4 10 a5 10 a6 10 a7 10 }}
    sd a0,  0(gp)
    ld a1,  0(gp)
    lwu a2, 0(gp)
    lhu a3, 0(gp)
    lbu a4, 0(gp)
    lw a5,  0(gp)
    lh a6,  0(gp)
    lb a7,  0(gp)
}}

test {{
    inputs  {{ a0 -7 gp 0x600000 }}
    outputs {{ a1 -7 a2 4294967289 a3 65529 a4 249 a5 18446744073709551609 a6 18446744073709551609 a7 18446744073709551609 }}
    sd a0,  0(gp)
    ld a1,  0(gp)
    lwu a2, 0(gp)
    lhu a3, 0(gp)
    lbu a4, 0(gp)
    lw a5,  0(gp)
    lh a6,  0(gp)
    lb a7,  0(gp)
}}
