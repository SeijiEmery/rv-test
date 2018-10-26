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
ebreak
