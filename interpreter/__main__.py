import sys
from interpreter import compile_asm

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: python -m interpreter <input_file> <target_file>"
    _, source, target = sys.argv
    compile_asm(source, target)

