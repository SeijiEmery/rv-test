
test {{
    inputs  {{ a0 16045690984833335023 }}
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
    add t0, a0, zero
    addi t1, zero, 32
    sll a0, a0, t0
    or  a0, a0, t0

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

test {{
    inputs  {{ a0 -7 }}
    outputs {{ a1 -7 a2 4294967289 a3 65529 a4 249 a5 18446744073709551609 a6 18446744073709551609 a7 18446744073709551609 }}
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
