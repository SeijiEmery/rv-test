addi s0, zero, 0
  loop:
    add  s0, s0, a0
    addi a0, a0, -1
    bgt  a0, zero, loop
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
addi zero, zero, 0
ebreak
