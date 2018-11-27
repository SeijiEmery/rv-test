addi t1, zero, 200
    sd   a0, 0(t1)
    sw   a0, 8(t1)
    sh   a0, 16(t1)
    sb   a0, 24(t1)

    ld   a1, 0(t1)
    ld   a2, 8(t1)
    ld   a3, 16(t1)
    ld   a4, 24(t1)
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
ebreak
