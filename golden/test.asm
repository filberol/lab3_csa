code:
mov ax [text_label]
loop:
printc ax
cmp
jne [loop]
hlt
data:
text_label: Hello,_world!
