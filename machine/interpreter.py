import logging
from interpreter.entities import opcode_to_instruction, code_to_register, \
    Instruction, OperandMode, Register, AddressPointer, AddressMode, \
    register_to_code

REGISTER_COUNT = 8


class Machine:
    """Machine has all the simulation logic, divided into data path and control unit"""

    def __init__(self):
        self.data_path = self.DataPath()
        self.control_unit = self.ControlUnit(self.data_path)

    class DataPath:
        """DataPath contains all the buses and registers inside the machine"""
        def __init__(self):
            self.code_seg: dict[int, str] = {}  # Instructions stored separately
            self.data_seg: dict[int, int] = {}  # Data stored separately
            self.instr_addr = None  # Current instruction address, fetched
            self.data_addr = None  # Current data address, fetched
            self.data_address = None  # Mem data pointer, set manually

            self.regs: list[int] = [0] * REGISTER_COUNT  # Set of registers, index defined by enum

            self.l_bus: int = 0  # Left bus node
            self.r_bus: int = 0  # Right bus node

            self.l_const: int = 0  # Left const
            self.r_const: int = 0  # Right const

            self.l_alu: int = 0  # Left alu input
            self.r_alu = 0  # Right alu input
            self.zero = 0  # Zero flag
            self.neg = 0  # Negative flag
            self.alu = 0  # Alu output value

            self.input_buffer: list[int] = []
            self.output_buffer = []

        def sel_l_bus(self, reg):
            """Select the left input value on bus"""
            assert 0 <= reg < 6, f"Only {REGISTER_COUNT} present"
            self.l_bus = self.regs[reg]
            # print(f"New l bus value {self.l_bus}")

        def sel_r_bus(self, reg):
            """Select the right value on bus"""
            assert 0 <= reg < 6, f"Only {REGISTER_COUNT} present"
            self.r_bus = self.regs[reg]

        def sel_l_inp(self, inp_type):
            """Select the left input on ALU
               True - const
               False - bus
            """
            if inp_type:
                self.l_alu = self.l_const
            else:
                self.l_alu = self.l_bus

        def sel_r_inp(self, inp_type):
            """Select the right input on ALU
               True - const
               False - bus
            """
            if inp_type:
                self.r_alu = self.r_const
            else:
                self.r_alu = self.r_bus

        def calc_alu(self, operation):
            """Hardwired Alu math operations"""
            match operation:
                case 0:
                    self.alu = self.l_alu + self.r_alu
                case 1:
                    self.alu = self.l_alu - self.r_alu
                case 2:
                    self.alu = self.l_alu * self.r_alu
                case 3:
                    self.alu = self.l_alu // self.r_alu
                case 4:
                    self.alu = self.l_alu % self.r_alu
                case 5:
                    self.alu = self.l_alu

        def is_zero(self):
            """Check zero flag"""
            return self.zero == 1

        def is_neg(self):
            """Check negative flag"""
            return self.neg == 1

        def set_zero(self):
            """Set zero flag of operation"""
            # print(f"Value on alu is {self.alu} {repr(self.alu)} {chr(self.alu)}")
            if self.alu == 0 or chr(self.alu) == "0" or repr(self.alu) == '0':
                self.zero = 1
                # print("Set zero")
            else:
                self.zero = 0
                # print("Reset zero")

        def set_neg(self):
            """Set negative flag of operation"""
            if self.alu < 0:
                self.neg = 1
            else:
                self.neg = 0

        def sel_reg(self, reg, src):
            """Write selected register from alu, mem or input
               0: from mem by data_address
               1: from alu
               2: from input buffer
            """
            match src:
                case 0:
                    self.regs[reg] = self.data_seg[self.data_address]
                case 1:
                    self.regs[reg] = self.alu
                case 2:
                    self.input(reg)

        def sel_addr_src(self, src):
            """Set selected addr_pointer from
               0: fetched instr_addr
               1: written data_addr
               2: calculated from alu
            """
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
            # print("Reading from port")
            if len(self.input_buffer) == 0:
                raise EOFError()
            symbol = self.input_buffer.pop(0)
            symbol_code = symbol
            assert -128 <= symbol_code <= 127, f'Input token invalid: {symbol_code}'
            addr = self.regs[register_to_code[reg]]
            self.data_seg[addr] = symbol_code
            logging.debug(f'Input: {chr(symbol)} to addr {hex(addr)}')
            print(f'INPUT <<< {chr(symbol)} to addr {hex(addr)}')

        def output(self, out_type):
            """Write symbol from alu to output buffer"""
            if out_type:
                symbol = self.alu
                logging.debug(f'Output: {repr("".join(self.output_buffer))} << {repr(str(symbol))}')
                self.output_buffer.append(str(symbol)) if str(symbol) != '0' else str(symbol)
                print(f"PRINT >>> {str(symbol)} with code {symbol}")
            else:
                symbol = chr(self.alu)
                if symbol != "\0":
                    logging.debug(f'Output: {repr("".join(self.output_buffer))} << {repr(symbol)}')
                    self.output_buffer.append(symbol)
                    print(f"PRINT >>> {symbol} with code {self.alu}")

    class ControlUnit:
        def __init__(self, data_path: 'Machine.DataPath'):
            self.program_counter: int = 0  # Program count is separate and synchronized with data path
            self.data_path: Machine.DataPath = data_path  # DataPath link
            self._tick: int = 0  # Tick simulation counter on instruction level
            self._instr: int = 0

        def tick(self):
            """Simulate ticks for operations"""
            self._tick += 1

        def current_tick(self):
            return self._tick

        def next_instr(self):
            self._instr += 1

        def current_instr(self):
            return self._instr

        def latch_program_counter(self, sel_next: bool):
            if sel_next:
                self.program_counter += 1
            else:
                arg1, _ = self.fetch_operands_from_command()
                self.program_counter = arg1.address
            self.data_path.instr_addr = self.program_counter
            self.next_instr()
            self.tick()

        def fetch_operands_from_command(self):
            instr = self.data_path.code_seg[self.data_path.data_address]
            op_mode: OperandMode = OperandMode(int(instr[8:11], 2))
            # Fetch arguments from the binary
            arg1 = None
            arg2 = None
            match op_mode:
                # first reg
                case OperandMode.REG | OperandMode.REG_REG | OperandMode.REG_MEM:
                    arg1 = Register(code_to_register[int(instr[11:15], 2)])
                    # second reg
                    if op_mode == OperandMode.REG_REG:
                        arg2 = Register(code_to_register[int(instr[15:19], 2)])
                    # second mem
                    elif op_mode == OperandMode.REG_MEM:
                        addr_mode = AddressMode(int(instr[15:17], 2))
                        addr = int(instr[17:25], 2)
                        arg2 = AddressPointer(addr_mode=addr_mode, addr=addr)
                # first mem
                case OperandMode.MEM | OperandMode.MEM_REG | OperandMode.MEM_MEM:
                    addr_mode = AddressMode(int(instr[11:13], 2))
                    addr = int(instr[13:21], 2)
                    arg1 = AddressPointer(addr_mode=addr_mode, addr=addr)
                    if op_mode == OperandMode.MEM_REG:
                        arg2 = Register(code_to_register[int(instr[21:25], 2)])
                    elif op_mode == OperandMode.MEM_MEM:
                        addr_mode = AddressMode(int(instr[21:23], 2))
                        addr = int(instr[23:31], 2)
                        arg2 = AddressPointer(addr_mode=addr_mode, addr=addr)
            return arg1, arg2

        def select_data_from_memory(self, addr_p: AddressPointer):
            match addr_p.mode:
                case AddressMode.ABSOLUTE:
                    return self.data_path.data_seg[addr_p.address]
            self.tick()
            return 0

        def decode_and_execute_instruction(self):
            # First fetch the instruction, decode operand mode, registers, and addresses
            instr = self.data_path.code_seg[self.data_path.data_address]
            opcode: Instruction = opcode_to_instruction[int(instr[0:8], 2)]
            op_mode: OperandMode = OperandMode(int(instr[8:11], 2))
            arg1, arg2 = self.fetch_operands_from_command()
            logging.debug(f"Instr: {self.current_instr()}, Tick: {self.current_tick()}, Instruction {opcode} "
                          f"with operands {op_mode}: {arg1} and {arg2}")
            # print(f"Instr: {self.current_instr()}, Tick: {self.current_tick()}, Instruction {opcode} with operands {op_mode}: {arg1} and {arg2}")
            # print(f"Instruction {opcode} with operands {op_mode}: {arg1} and {arg2}")

            match opcode:
                # Working, tested
                case Instruction.HLT:
                    raise StopIteration()

                case Instruction.JMP:
                    self.latch_program_counter(sel_next=False)
                    self.data_path.sel_addr_src(0)
                    self.tick()

                case Instruction.JE:
                    if self.data_path.is_zero():
                        self.latch_program_counter(sel_next=False)
                    else:
                        self.latch_program_counter(sel_next=True)
                    self.data_path.sel_addr_src(0)
                    self.tick()

                case Instruction.JNE:
                    if self.data_path.is_zero():
                        # print("Not jumping")
                        self.latch_program_counter(sel_next=True)
                    else:
                        # print("Really jumping")
                        self.latch_program_counter(sel_next=False)
                    self.data_path.sel_addr_src(0)
                    self.tick()

                case Instruction.JLE:
                    if self.data_path.is_neg() or self.data_path.is_zero():
                        self.latch_program_counter(sel_next=False)
                    else:
                        self.latch_program_counter(sel_next=True)
                    self.data_path.sel_addr_src(0)
                    self.tick()

                case Instruction.JGE:
                    if not self.data_path.is_neg() or self.data_path.is_zero():
                        self.latch_program_counter(sel_next=False)
                    else:
                        self.latch_program_counter(sel_next=True)
                    self.data_path.sel_addr_src(0)
                    self.tick()

                case Instruction.ADD | Instruction.SUB | Instruction.MUL | Instruction.DIV | Instruction.MOD \
                     | Instruction.CMP:
                    arg1, arg2 = self.fetch_operands_from_command()

                    if isinstance(arg1, Register):
                        self.data_path.sel_l_bus(register_to_code[arg1])
                        self.data_path.sel_l_inp(False)
                    if isinstance(arg1, AddressPointer):
                        self.data_path.l_const = self.select_data_from_memory(arg1)
                        self.data_path.sel_l_inp(True)
                    if isinstance(arg2, Register):
                        self.data_path.sel_r_bus(register_to_code[arg2])
                        self.data_path.sel_r_inp(False)
                    if isinstance(arg2, AddressPointer):
                        self.data_path.r_const = self.select_data_from_memory(arg2)
                        self.data_path.sel_r_inp(True)

                    match opcode:
                        case Instruction.ADD:
                            self.data_path.calc_alu(0)
                        case Instruction.SUB:
                            self.data_path.calc_alu(1)
                        case Instruction.MUL:
                            self.data_path.calc_alu(2)
                        case Instruction.DIV:
                            self.data_path.calc_alu(3)
                        case Instruction.MOD:
                            self.data_path.calc_alu(4)
                        case Instruction.CMP:
                            self.data_path.calc_alu(1)
                            self.data_path.set_zero()
                            self.data_path.set_neg()
                    self.tick()

                    if isinstance(arg1, Register):
                        self.data_path.sel_reg(register_to_code[arg1], 1)

                    # print(f"New ax value = {self.data_path.regs[0]}")
                    self.latch_program_counter(True)
                    self.data_path.sel_addr_src(0)
                    self.tick()

                case Instruction.MOV:
                    arg1, arg2 = self.fetch_operands_from_command()

                    if isinstance(arg1, Register) and isinstance(arg2, AddressPointer):
                        # print("Loading address into register")
                        self.data_path.l_const = arg2.address
                        self.data_path.sel_l_inp(True)
                        self.data_path.r_const = 0
                        self.data_path.sel_r_inp(True)
                        self.data_path.calc_alu(0)

                    self.data_path.sel_reg(register_to_code[arg1], 1)
                    # print(f"Loaded {arg1} to value {self.data_path.alu}")
                    self.tick()

                    self.latch_program_counter(True)
                    self.data_path.sel_addr_src(0)
                    self.tick()

                case Instruction.PRINT | Instruction.PRINTC:
                    arg1, _ = self.fetch_operands_from_command()
                    if isinstance(arg1, Register):
                        # print(f"Fetching from register address")
                        self.data_path.l_const = self.data_path.data_seg[self.data_path.regs[register_to_code[arg1]]]
                        self.data_path.regs[register_to_code[arg1]] += 1
                        self.data_path.sel_l_inp(True)
                        self.data_path.calc_alu(5)
                    else:
                        self.data_path.l_const = self.select_data_from_memory(arg1)
                        self.data_path.sel_l_inp(True)
                        self.data_path.calc_alu(5)
                    self.tick()

                    if opcode == Instruction.PRINT:
                        self.data_path.output(True)
                    else:
                        self.data_path.output(False)
                    self.tick()

                    self.latch_program_counter(True)
                    self.data_path.sel_addr_src(0)
                    self.tick()

                case Instruction.PRINTSTR:
                    arg1, _ = self.fetch_operands_from_command()

                    if isinstance(arg1, Register):
                        return

                    const = self.select_data_from_memory(arg1)
                    while int(const) != ord('0'):
                        self.data_path.l_const = const
                        self.data_path.sel_l_inp(True)
                        self.data_path.calc_alu(5)
                        self.data_path.output(False)
                        arg1.address += 1
                        self.tick()

                    self.latch_program_counter(True)
                    self.data_path.sel_addr_src(0)
                    self.tick()

                case Instruction.READ:
                    arg1, _ = self.fetch_operands_from_command()
                    # print("Trying to read from port")
                    if isinstance(arg1, Register):
                        self.data_path.input(arg1)
                        self.data_path.l_const = self.data_path.data_seg[self.data_path.regs[register_to_code[arg1]]]
                        self.data_path.sel_l_inp(True)
                        self.data_path.calc_alu(5)
                        self.data_path.regs[register_to_code[arg1]] += 1
                    self.tick()

                    self.latch_program_counter(sel_next=True)
                    self.data_path.sel_addr_src(0)
                    self.tick()

    def load_machine_from_file(self, compiled_file):
        with open(compiled_file, encoding="utf-8") as f:
            source_str = f.read()
        code, data = source_str.split('-\n')
        self.load_code(code)
        self.load_data(data)

    def load_code(self, string_data):
        instructions = string_data.strip().split('\n')
        for line in instructions:
            addr, instr = line.split(' ')
            self.data_path.code_seg[int(addr, 16)] = instr

    def load_data(self, string_data):
        datalines = string_data.strip().split('\n')
        for line in datalines:
            addr, value = line.split(' ')
            self.data_path.data_seg[int(addr, 16)] = int(value, 2)

    def load_input_buffer_from_file(self, source_f):
        with open(source_f, encoding="utf-8") as f:
            source_str = f.read()
            self.data_path.input_buffer = [ord(char) for char in source_str]
        pass

    def init_start_state(self):
        self.data_path.sx = 0xFF
        self.data_path.ip = 0
        self.data_path.data_address = sorted(self.data_path.code_seg.keys())[0]
        self.control_unit.program_counter = self.data_path.data_address
