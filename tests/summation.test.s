
test {{
    inputs {{ a0 1000 }}
    outputs {{ a0 0 s0 500500 }}

    addi s0, zero, 0
  loop:
    add  s0, s0, a0
    addi a0, a0, -1
    bgt  a0, zero, loop
}}
