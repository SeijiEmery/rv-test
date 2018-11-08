add a0, s0, zero
call fib
add s0, a0, zero

add a0, s1, zero
call fib
add s1, a0, zero

add a0, s2, zero
call fib
add s2, a0, zero

add a0, s3, zero
call fib
add s3, a0, zero

add a0, s4, zero
call fib
add s4, a0, zero

add a0, s5, zero
call fib
add s5, a0, zero

beq zero, zero, end
fib:
addi t0, zero, 0
addi t1, zero, 1
bge zero, a0, fib_end
loop:
add t2, t1, t0
add t0, t1, zero
add t1, t2, zero
addi a0, a0, -1
bgt a0, zero, loop
fib_end:
add a0, t0, zero
ret
end:
nop
nop
nop
nop
nop
ebreak
