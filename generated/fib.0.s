jal     ra, fib
j       end
fib:
li      t0, 1
ble     a0, t0, return

addi    sp, sp, -16
sd      ra, 8(sp)

addi    t0, a0, -1
sd      t0, 0(sp)
addi    a0, a0, -2
jal     ra, fib

ld      t0, 0(sp)
sd      a0, 0(sp)
addi    a0, t0, 0
jal     ra, fib

ld      t0, 0(sp)
add     a0, a0, t0

ld      ra, 8(sp)
addi    sp, sp, 16
return:
jalr    x0, 0(ra)

end:
ebreak
nop
nop
nop
nop
nop
ebreak
