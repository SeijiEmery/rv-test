
test {{
    inputs  {{ a0 16045690984833335023 }}
    outputs {{ 
        a0 16045690984833335023 
        a1 1
        a2 2
        a3 3 
        a4 4 
        a5 0
        a6 0 
        a7 0
    }}

    add gp, zero, zero
    sd a0,  100(zero)
    ld a1,  100(zero)
    lwu a2, 100(zero)
    lhu a3, 100(zero)
    lbu a4, 100(zero)
    lw a5,  100(zero)
    lh a6,  100(zero)
    lb a7,  100(zero)
}}

test {{
    inputs  {{ a0 10 }}
    outputs {{ a1 10 a2 10 a3 10 a4 10 a5 10 a6 10 a7 10 }}
    add gp, zero, zero
    sd a0,  0(gp)
    ld a1,  0(gp)
    lwu a2, 0(gp)
    lhu a3, 0(gp)
    lbu a4, 0(gp)
    lw a5,  0(gp)
    lh a6,  0(gp)
    lb a7,  0(gp)
}}


