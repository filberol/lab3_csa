__all__ = ['compile_asm', 'entities', 'compiler']

from typing import TextIO


def compile_asm(source_f: str, dest_f: str):
    from interpreter.compiler import compile_code
    compile_code(source_f, dest_f)
