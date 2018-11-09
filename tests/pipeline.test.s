test "alu-dependency-1" {{
	inputs {{ s0 0 s1 50 s2 0 }}
	outputs {{ s0 10 s1 50 s2 40 }}

	addi s0, s0, 10
	sub s2, s1, s0

}}

test "alu-dependency-2" {{
	inputs {{ s0 0 s1 10 s2 20 s3 30 s4 40 s5 50 }}
	outputs {{ s0 0 s1 10 s2 30 s3 60 s4 100 s5 150 }}

	add s1, s1, s0
	add s2, s2, s1
	add s3, s3, s2
	add s4, s4, s3
	add s5, s5, s4

}}

test "mem-dependency-1" {{ 
	inputs {{ s0 1000 s1 2048 s2 0 s3 0 }}
	outputs {{ s0 1000 s1 2048 s2 1000 s3 2000 }}

	sd s0, 0(s1)
	ld s2, 0(s1)
	add s3, s0, s2

}}

test "mem-dependency-2" {{ 
	inputs {{ s0 2048 s1 2048 s2 0 s3 69 s4 0 }}
	outputs {{ s0 2048 s1 2048 s2 2048 s3 69 s4 69 }}

	sd s0, 0(s1)
	ld s2, 0(s1)
	sd s3, 0(s2)
	ld s4, 0(s2)

}}

test "alu-mem-dependency-1" {{ 
	inputs {{ s0 420 s1 3072 s2 0 s3 69  s4 0 }}
	outputs {{ s0 420 s1 3072 s2 420 s3 69 s4 489 }}

	sd s0, 0(s1)
	ld s2, 0(s1)
	add s4, s3, s2

}}
