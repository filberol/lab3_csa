from enum import Enum


class Operation:
    def __init__(self, instr, ops):
        self.instr: Instruction = instr
        self.op_mode: OperandMode = OperandMode.NONE
        if len(ops) == 1:
            if isinstance(ops[0], Register):
                self.op_mode = OperandMode.REG
            else:
                self.op_mode = OperandMode.MEM
        if len(ops) == 2:
            if isinstance(ops[0], Register):
                if isinstance(ops[1], Register):
                    self.op_mode = OperandMode.REG_REG
                else:
                    self.op_mode = OperandMode.REG_MEM
            else:
                if isinstance(ops[1], Register):
                    self.op_mode = OperandMode.MEM_REG
                else:
                    self.op_mode = OperandMode.MEM_MEM

        self.ops: list[Register | AddressPointer] = [] + ops

    def to_binary(self):
        return f"{self.instr.to_binary()}{self.op_mode.to_binary()}" \
               f"{''.join(map(lambda x: x.to_binary(), self.ops))}{'0' * operand_mode_to_bit_addition[self.op_mode]}"

    def __str__(self):
        return str(self.instr)


class Instruction(str, Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    MOV = "mov"
    DEFV = "defv"
    JMP = "jmp"
    JMPR = "jmpr"
    HLT = "hlt"
    JNE = "jne"
    JE = "je"
    CMP = "cmp"
    PRINT = "print"
    NOP = "nop"
    READ = "read"
    PRINTSTR = "printstr"
    JLE = "jle"
    JGE = "jge"
    PRINTC = "printc"

    def to_binary(self):
        return format(instruction_to_opcode[self], '08b')


instruction_to_opcode = {
    Instruction.ADD: 0x01,  # Add
    Instruction.SUB: 0x28,  # Subtraction
    Instruction.MUL: 0x69,  # Multiply
    Instruction.DIV: 0xF7,  # Divide
    Instruction.MOD: 0xF8,  # Remainder
    Instruction.MOV: 0x89,  # Move
    Instruction.CMP: 0x38,  # Compare
    Instruction.DEFV: 0x52,  #
    Instruction.JMP: 0xE9,  # Absolute jump
    Instruction.JMPR: 0xEA,  #
    Instruction.HLT: 0xF4,  # Halt
    Instruction.JNE: 0x7F,  # Jump not equal
    Instruction.JE: 0x7E,  # Jump equal
    Instruction.PRINT: 0xE6,  # Print
    Instruction.NOP: 0x90,  # No operation
    Instruction.READ: 0xE4,  # Input
    Instruction.PRINTSTR: 0xE7,  # Print till 0
    Instruction.JLE: 0x7A,  # Jump lesser equal
    Instruction.JGE: 0x7B,  # Jump greater equal
    Instruction.PRINTC: 0xE8  # Print char
}

opcode_to_instruction = {v: k for k, v in instruction_to_opcode.items()}


class Register(str, Enum):
    AX = 'ax'
    BX = 'bx'
    CX = 'cx'
    DX = 'dx'
    SX = 'sx'
    IP = 'ip'
    SI = 'si'
    DI = 'di'

    def to_binary(self):
        return format(register_to_code[self], '04b')


register_to_code = {
    Register.AX: 0x0,  # Accumulator register
    Register.BX: 0x1,  # Base register
    Register.CX: 0x2,  # Counter register
    Register.DX: 0x3,  # Data register
    Register.IP: 0x4,  # Stack pointer
    Register.SX: 0x5,  # Base pointer
    Register.SI: 0x6,  # Source index
    Register.DI: 0x7  # Destination index
}

code_to_register = {v: k for k, v in register_to_code.items()}


class AddressMode(int, Enum):
    ABSOLUTE = 1
    RELATIVE = 2
    RELATIVE_IP = 3

    def to_binary(self):
        return format(self.value, '02b')


class AddressPointer:
    def __init__(self, addressing: str = None, addr_mode: AddressMode = None, addr: int = None):
        if addr_mode is not None and addr is not None:
            self.mode = addr_mode
            self.address = addr
            return
        self.label: str | None = None
        self.address: int | None = None
        try:  # check addressing type and make operand
            self.mode = AddressMode.ABSOLUTE
            self.address = int(addressing, 16)
        except ValueError:
            if 'ip' in addressing:
                self.mode = AddressMode.RELATIVE_IP
                parts = addressing.split('+')
                self.address = int(parts[1], 16)
            if '[' in addressing:
                self.mode = AddressMode.ABSOLUTE
                self.label = addressing.split('[')[1][:-1]
                # address placed in compilation stage

    def to_binary(self):
        return f"{self.mode.to_binary()}{format(self.address, '08b') if self.address else None}"

    def __str__(self):
        return f'{hex(self.address) if self.address else None} {self.mode}'


class OperandMode(int, Enum):
    NONE = 1,
    REG = 2,
    MEM = 3,
    REG_REG = 4,
    REG_MEM = 5,
    MEM_REG = 6,
    MEM_MEM = 7

    def to_binary(self):
        return format(self.value, '03b')


operand_mode_to_bit_addition = {
    OperandMode.NONE: 21,
    OperandMode.REG: 17,
    OperandMode.REG_REG: 13,
    OperandMode.MEM: 11,
    OperandMode.REG_MEM: 7,
    OperandMode.MEM_REG: 7,
    OperandMode.MEM_MEM: 1
}
