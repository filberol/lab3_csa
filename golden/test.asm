code:
mov ax [null]
mov cx [max]
loop:
mov bx [three]
add ax bx
mov bx [two]
add ax bx
mov bx [one]
add ax bx
mov bx [three]
add ax bx
mov bx [one]
add ax bx
mov bx [two]
add ax bx
mov bx [three]
add ax bx
print bx
hlt
data:
three: 3
two: 2
one: 1
null: 0
max: 1000
