__all__ = ['compile_asm', 'entities']

from typing import TextIO


def compile_asm(source_f: TextIO, dest_f: TextIO):
    from interpreter.compiler import compile_code
    compile_code(source_f, dest_f)
