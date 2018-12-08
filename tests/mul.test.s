
test "mul mulh" {{
    inputs {{
        a0  1 a1 -1 a2 0x7decafdeadbeef a3 -0x7decafdeadbeef a4 0xffffffffffffffff
        s0 -1 s1 -1 s2 0x7decafdeadbeef s3 -0x7decafdeadbeef s4 0xffffffffffffffff
    }}
    outputs {{
        t0 -1 t1 1 t2 0xab7fd4216da321 t3 0xab7fd4216da321 t4 1
        s0 0  s1 0 s2 0x3df0fe94310f   s3 0x3df0fe94310f   s4 0
    }}
    mul  t0, a0, s0
    mulh s0, a0, s0
    mul  t1, a1, s1
    mulh s1, a1, s1
    mul  t2, a2, s2
    mulh s2, a2, s2
    mul  t3, a3, s3
    mulh s3, a3, s3
    mul  t4, a4, s4
    mulh s4, a4, s4
}}

test "mulw" {{
    inputs {{
        a0  1 a1 -1 a2 0x7decafdeadbeef a3 -0x7decafdeadbeef
        s0 -1 s1 -1 s2 0x7decafdeadbeef s3 -0x7decafdeadbeef
    }}
    outputs {{
        t0 -1 t1 1 t2 0xab7fd4216da321 t3 0xab7fd4216da321
    }}
    mul  t0, a0, s0
    mulh s0, a0, s0
    mul  t1, a1, s1
    mulh s1, a1, s1
    mul  t2, a2, s2
    mulh s2, a2, s2
    mul  t3, a3, s3
    mulh s3, a3, s3
}}

test "mulhsu" {{

}}

test "mulhu" {{

}}

test "div rem" {{
    inputs {{
        a0  1 a1 -1 a2 -35444612188192495 a3 -35444612188192495 a4 18446744073709551615 a5 102984
        s0 -1 s1 -1 s2 1010013            s3 -1010013           s4 12090182091          s5 0
    }}
    outputs {{
        t0 -1  t1 1 t2  -35093223738      t3 35093223738        t4 0           t5 -1
        s0  0  s1 0 s2  -903901            s3 -903901             s4 -1           s5 102984
    }}
    div t0, a0, s0
    rem s0, a0, s0
    div t1, a1, s1
    rem s1, a1, s1
    div t2, a2, s2
    rem s2, a2, s2
    div t3, a3, s3
    rem s3, a3, s3
    div t4, a4, s4
    rem s4, a4, s4
    div t5, a5, s5
    rem s5, a5, s5
}}

test "divu remu" {{

}}

test "divw remw" {{

}}

test "divuw remuw" {{

}}
