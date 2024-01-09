__all__ = ['start_machine']

def start_machine(code_file: str, input_file: str):
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
