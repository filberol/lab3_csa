code:
mov
mov ax
mov 0xfb
mov ax bx
regmemlabel:
mov ax 0xfb
mov 0xfb bx
mov 0xfb 0xfa
mov 0xbf [label0]
data:
label0: Hello,_world!
label1: 0x12