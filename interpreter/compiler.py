import re
import sys
from interpreter.entities import Instruction, Register, Operation, AddressPointer


def parse_command(line: str) -> Operation:
    split_words = re.sub(r'\s+', ' ', line.strip()).split(' ')
    inst_op = Instruction(split_words[0])
    operands = []
    for operand_ind in range(1, len(split_words)):
        try:
            op = Register(split_words[operand_ind])
        except ValueError:
            op = AddressPointer(split_words[operand_ind])
        operands.append(op)

    node = Operation(instr=inst_op, ops=operands)
    return node


def compile_code(source_f, target_f):
    with open(source_f, encoding="utf-8") as f:
        source_t = f.read()

    # init line dependent variables and code maps
    instructions: dict[int, Operation] = {}
    data_seg: dict[int, int] = {}
    label_addresses: dict[str, int] = {}
    data_labels: dict[str, int] = {}
    c_address = 10
    d_address = 1

    # compiling the source code with stubs for labels
    source_lines = source_t.split('\n')  # split code into lines
    code_segment = True
    for source_line in source_lines:
        # track source code segments
        if source_line == '':
            continue
        if source_line == 'code:':
            code_segment = True
            continue
        if source_line == 'data:':
            code_segment = False
            continue
        # compile code segments into machine words
        if code_segment:
            if source_line.strip().endswith(":"):  # if label then add label pointer
                label = re.sub(r'\W+', '', source_line)
                label_addresses[label] = c_address
            else:
                operation = parse_command(source_line)
                instructions[c_address] = operation
                c_address += 1
        # else split strings to cells or write numbers
        else:
            parts = source_line.split(' ')
            label = re.sub(r'\W+', '', parts[0])
            word = parts[1].strip()
            try:
                word = int(word, 16)
                data_labels[label] = d_address
                data_seg[d_address] = word
                d_address += 1
            except ValueError:
                data_labels[label] = d_address
                for char in word:
                    data_seg[d_address] = ord(char)
                    d_address += 1
                data_seg[d_address] = ord('0')
                d_address += 1

    # fill label addresses from dictionary
    for instruction in instructions.values():
        for pointer in instruction.ops:
            if isinstance(pointer, AddressPointer):
                if pointer.label is not None:
                    print(pointer.label)
                    pointer.address = data_labels[pointer.label]

    print_debug_instructions(instructions)
    print_debug_data_seg(data_seg)
    print(label_addresses)
    print(data_labels)


def print_debug_instructions(instructions: dict[int, Operation]):
    print("Code section")
    for key in instructions.keys():
        print(f"0x{format(key, f'04x')} - {instructions[key].to_binary()}", end=' - ')
        print(f"{instructions[key].instr} - ops: {list(map(lambda x: str(x), instructions[key].ops))}")


def print_debug_data_seg(instructions: dict[int, int]):
    print("Data section")
    for key in instructions.keys():
        print(f"0x{format(key, f'02x')} - {format(instructions[key], '08b')}", end=' - ')
        print(f"{chr(instructions[key]) if 32 <= instructions[key] <= 126 else instructions[key]}")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    compile_code(source, target)
