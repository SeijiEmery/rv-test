add s1, a1, zero
    add s2, a2, zero
    add s3, a3, zero
    add s4, a4, zero
    addi t0, zero, 1
    addi t1, zero, -1

    addiw a1, a1, 1
    addi  a2, a2, 1
    addiw a3, a3, -1
    addi a4, a4, -1

    addw s1, s1, t0
    add s2, s2, t0
    addw s3, s3, t1
    add s4, s4, t1
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
ebreak