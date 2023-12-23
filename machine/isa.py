import json
from enum import Enum


class Opcode(str, Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DEV = "dev"
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


def write_code_and_data(filename, code):
    """Записать машинный код в файл."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, indent=4))


def read_code_and_data(filename):
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())
    return code
