import sys
from machine import start_machine

if __name__ == '__main__':
    assert len(sys.argv) == 3, "Wrong arguments: python -m machine <compiled_code> <input_file>"
    _, source, target = sys.argv
    start_machine(source, target)

