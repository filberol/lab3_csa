import sys

from interpreter.entities import opcode_to_instruction, OperandMode


class Machine:
    code_seg: dict[int, str] = None
    data_seg: dict[int, int] = None
    instr_to_exec: list[int] = None

    def __init__(self):
        self.ax: int = 0
        self.bx: int = 0
        self.cx: int = 0
        self.dx: int = 0
        self.sx: int = 0
        self.ip: int = 0
        self.si: int = 0
        self.di: int = 0

    def load_machine_from_file(self, compiled_file):
        code, data = compiled_file.split('-\n')
        self.load_code(code)
        self.load_data(data)

    def load_code(self, string_data):
        instructions = string_data.split('\n')
        for line in instructions:
            addr, instr = line.split(' ')
            self.code_seg[int(addr)] = instr

    def load_data(self, string_data):
        datalines = string_data.split('\n')
        for line in datalines:
            addr, value = line.split(' ')
            self.data_seg[int(addr)] = int(value)

    def append_input(self, input_data):
        pass

    def init_start_state(self):
        self.sx = 0xFF
        self.ip = 0
        self.instr_to_exec = sorted(self.code_seg.keys())

    def execute_instruction(self):
        code_line = self.code_seg[self.ip]
        self.ip += 1
        instr_opcode, op_mode_code = int(code_line[0:8]), int(code_line[9:12])
        instruction = opcode_to_instruction[instr_opcode]
        op_mode = OperandMode(op_mode_code)
        print(instruction, op_mode)
