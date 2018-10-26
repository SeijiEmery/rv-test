#!/usr/bin/env python3
""" registers.py: basic definition of risc-v integer registers """

# Register mappings + stringification
registers = [
    [('x%d'%i, i) for i in range(0, 31+1) ] +
    [('zero', 0), ('ra', 1), ('sp', 2), ('gp', 3), ('tp', 4)] +
    [('a%d'%i, i + 10) for i in range(0, 7+1)] +
    [('s%d'%i, i+8) for i in range(0, 1+1)] +
    [('s%d'%i, i+16) for i in range(2, 11+1)] +
    [('t%d'%i, i+5) for i in range(0, 2+1)] +
    [('t%d'%i, i+25) for i in range(3, 6+1)]
][0]
REGISTER_MAPPINGS = dict(registers)
REGISTER_TO_STR = dict([ (v, k) for k, v in registers ])

assert(REGISTER_MAPPINGS['x0'] == 0)
assert(REGISTER_MAPPINGS['x31'] == 31)
assert('x32' not in REGISTER_MAPPINGS)
assert(REGISTER_MAPPINGS['zero'] == 0)
assert(REGISTER_MAPPINGS['ra'] == 1)
assert(REGISTER_MAPPINGS['sp'] == 2)
assert(REGISTER_MAPPINGS['gp'] == 3)
assert(REGISTER_MAPPINGS['tp'] == 4)
assert(REGISTER_MAPPINGS['a0'] == 10)
assert(REGISTER_MAPPINGS['a7'] == 17)
assert(REGISTER_MAPPINGS['s0'] == 8)
assert(REGISTER_MAPPINGS['s1'] == 9)
assert(REGISTER_MAPPINGS['s2'] == 18)
assert(REGISTER_MAPPINGS['s11'] == 27)
assert(REGISTER_MAPPINGS['t0'] == 5)
assert(REGISTER_MAPPINGS['t2'] == 7)
assert(REGISTER_MAPPINGS['t3'] == 28)
assert(REGISTER_MAPPINGS['t6'] == 31)
assert([ REGISTER_TO_STR[reg] for reg in range(32) ] == [

    # 0     1     2     3      4     5     6     7      
    'zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 
    # 8     9     10    11     12    13    14    15
    's0',  's1', 'a0', 'a1',  'a2', 'a3', 'a4', 'a5', 
    # 16    17    18    19     20    21    22    23
    'a6',  'a7', 's2', 's3',  's4', 's5', 's6', 's7',
    # 24    25    26    27     28    29    30    31 
    's8', 's9', 's10', 's11', 't3', 't4', 't5', 't6' 
])