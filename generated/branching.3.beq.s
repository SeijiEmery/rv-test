beq a0, a1, l1
    addi t1, zero, 11
l1:
    beq a0, a2, l2
    addi t2, zero, 22
l2:
    beq a0, a2, l3
    addi t3, zero, 33
l3:
    beq a0, a2, l4
    addi t4, zero, 44
l4:
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
ebreak
