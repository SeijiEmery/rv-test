call fib
j end
fib:
addi t0, zero, 1
ble a0, t0, return
addi sp, sp, -8
addi t0, a0, -1
sd t0, 0(sp)
addi a0, a0, -2
call fib

ld t0, 0(sp)
sd a0, 0(sp)
add a0, zero, t0
call fib

ld t0, 0(sp)
add a0, a0, t0
return:
ret
end:
ebreak
