code:
mov ax [text_label]
mov bx [buffer_label]
mov cx [buffer_label]
print_loop:
printc ax
cmp
jne [print_loop]
read_loop:
read bx
cmp
jne [read_loop]
output_loop:
printc cx
cmp
jne [output_loop]
hlt
data:
text_label: Hello,_
buffer_label: buffer_word
