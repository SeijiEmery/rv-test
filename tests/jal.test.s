test {{
    inputs  {{ pc 0x100500 x1 0 }}
    outputs {{ pc 0x100600 x1 0x100504 }}
    steps {{ 1 }}
    nold {{ }}
    
    jal x1 +0x100
}}
test {{
    inputs  {{ pc 0x100500 x1 0 }}
    outputs {{ pc 0x100400 x1 0x100504}}
    steps {{ 1 }}
    nold {{ }}

    jal x1 -0x100
}}
