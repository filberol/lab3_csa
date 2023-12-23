from interpreter.entities import opcode_to_instruction, OperandMode

REGISTER_COUNT = 8


class Machine:
    class DataPath:
        def __init__(self):
            self.code_seg: dict[int, str] | None = None
            self.data_seg: dict[int, int] | None = None
            self.instr_to_exec: list[int] | None = None

            self.regs = [0] * REGISTER_COUNT

            self.l_bus = 0
            self.r_bus = 0

            self.l_const = 0
            self.r_const = 0

            self.l_alu = 0
            self.r_alu = 0
            self.zero = 0
            self.neg = 0
            self.alu = 0

        def sel_l_bus(self, reg):
            """Select the left input value on bus"""
            assert 0 <= reg < 6, f"Only {REGISTER_COUNT} present"
            self.l_bus = self.regs[reg]

        def sel_r_bus(self, reg):
            """Select the right value on bus"""
            assert 0 <= reg < 6, f"Only {REGISTER_COUNT} present"
            self.r_bus = self.regs[reg]

        def sel_l_inp(self, inp_type):
            """Select the left input on ALU"""
            if inp_type:
                self.l_alu = self.l_const
            else:
                self.l_alu = self.l_bus

        def sel_r_inp(self, inp_type):
            """Select the right input on ALU"""
            if inp_type:
                self.r_alu = self.r_const
            else:
                self.r_alu = self.r_bus

        def is_zero(self):
            """Check zero flag"""
            return self.zero == 1

        def is_neg(self):
            """Check negative flag"""
            return self.neg == 1

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


