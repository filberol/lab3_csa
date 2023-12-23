import logging
from interpreter.entities import opcode_to_instruction, OperandMode

REGISTER_COUNT = 8


class Machine:
    def __init__(self):
        self.data_path = self.DataPath()

    class DataPath:
        def __init__(self):
            self.code_seg: dict[int, str] | None = None     # Instructions stored separately
            self.data_seg: dict[int, int] | None = None     # Data stored separately
            self.instr_to_exec: list[int] | None = None     # List of remaining instruction pointers to execute
            self.instr_addr = None      # Current instruction address, fetched
            self.data_addr = None       # Current data address, fetched
            self.data_address = None    # Mem data pointer, set manually

            self.regs: list[int] = [0] * REGISTER_COUNT     # Set of registers, index defined by enum

            self.l_bus: int = 0     # Left bus node
            self.r_bus: int = 0     # Right bus node

            self.l_const: int = 0   # Left const
            self.r_const: int = 0   # Right const

            self.l_alu: int = 0     # Left alu input
            self.r_alu = 0          # Right alu input
            self.zero = 0   # Zero flag
            self.neg = 0    # Negative flag
            self.alu = 0    # Alu output value

            self.input_buffer: list[str] = []
            self.output_buffer = []

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

        def set_zero(self):
            """Set zero flag of operation"""
            if self.alu == 0:
                self.zero = 1
            else:
                self.zero = 0

        def set_neg(self):
            """Set negative flag of operation"""
            if self.alu < 0:
                self.neg = 1
            else:
                self.neg = 0

        def sel_reg(self, reg, src):
            """Write selected register from alu, mem or input"""
            match src:
                case 0:
                    self.regs[reg] = self.data_seg[self.data_address]
                case 1:
                    self.regs[reg] = self.alu
                case 2:
                    self.input(reg)

        def sel_addr_src(self, src):
            """Set selected addr_pointer from """
            match src:
                case 0:
                    self.data_address = self.instr_addr
                case 1:
                    self.data_address = self.data_addr
                case 2:
                    self.data_address = self.alu

        def write(self):
            """Write data by selected memory address"""
            self.data_seg[self.data_address] = self.alu

        def input(self, reg):
            """Read from input buffer, interruptions executed separately"""
            if len(self.input_buffer) == 0:
                raise EOFError()
            symbol = self.input_buffer.pop(0)
            symbol_code = ord(symbol)
            assert -128 <= symbol_code <= 127, f'Input token invalid: {symbol_code}'
            self.regs[reg] = symbol_code
            logging.debug(f'Input: {repr(symbol)}')

        def output(self, out_type):
            """Write symbol from alu to output buffer"""
            if out_type:
                symbol = self.alu
                logging.debug(f'Output: {repr("".join(self.output_buffer))} << {repr(str(symbol))}')
                self.output_buffer.append(str(symbol))
            else:
                symbol = chr(self.alu)
                if symbol != "\0":
                    logging.debug(f'Output: {repr("".join(self.output_buffer))} << {repr(symbol)}')
                    self.output_buffer.append(symbol)

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


