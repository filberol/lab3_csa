import sys
from machine.interpreter import Machine


if __name__ == '__main__':
    assert len(sys.argv) == 2, "Wrong arguments: python -m machine <compiled_code>"
    _, source = sys.argv

