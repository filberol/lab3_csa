__all__ = ['start_machine']

from typing import TextIO


def start_machine(code_file: TextIO, input_file: TextIO):
    from machine.interpreter import Machine
    machine = Machine()
    machine.load_machine_from_file(code_file)
    machine.load_input_buffer_from_file(input_file)
    machine.init_start_state()
    try:
        while True:
            machine.control_unit.decode_and_execute_instruction()
    except StopIteration:
        print("Finished operating by HALT")
