import re
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
        source_str = f.read()

    # init line dependent variables and code maps
    instructions: dict[int, Operation] = {}
    data_seg: dict[int, int] = {}
    code_labels: dict[str, int] = {}
    data_labels: dict[str, int] = {}
    c_address = 10
    d_address = 1

    # compiling the source code with stubs for labels
    source_lines = source_str.split('\n')  # split code into lines
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
                code_labels[label] = c_address
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
                word = int(word)
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
                    if pointer.label in data_labels:
                        pointer.address = data_labels[pointer.label]
                    if pointer.label in code_labels:
                        pointer.address = code_labels[pointer.label]

    print_debug_instructions(instructions)
    print_debug_data_seg(data_seg)

    # write compiled data to destination
    with open(target_f, 'w', encoding="utf-8") as f:
        for key in instructions.keys():
            f.write(f"0x{format(key, '04x')} {instructions[key].to_binary()}\n")
        f.write('-\n')
        for key in data_seg.keys():
            f.write(f"0x{format(key, '02x')} {format(data_seg[key], '08b')}\n")


def print_debug_instructions(instructions: dict[int, Operation]):
    print("Code section")
    for key in instructions.keys():
        print(f"0x{format(key, '04x')} - {instructions[key].to_binary()}", end=' - ')
        print(f"{instructions[key].instr} - {instructions[key].op_mode} - ops:"
              f" {list(map(lambda x: str(x), instructions[key].ops))}")


def print_debug_data_seg(data_cells: dict[int, int]):
    print("Data section")
    for key in data_cells.keys():
        print(f"0x{format(key, '02x')} - {format(data_cells[key], '08b')}", end=' - ')
        print(f"{chr(data_cells[key]) if 32 <= data_cells[key] <= 126 else data_cells[key]}")
