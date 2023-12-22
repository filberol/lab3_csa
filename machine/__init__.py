__all__ = ['start_machine']

from typing import TextIO


def start_machine(code_file: TextIO, input_file: TextIO):
    from machine.interpreter import Machine
    machine = Machine()
    machine.load_machine_from_file(code_file)
    machine.append_input(input_file)
    # TODO
    machine.execute_instruction()
