import json
import os
from  raspil_rt.convertation import convertation_for_program

from raspil_rt.main import Program


def main_test(name:str):
    big_input = os.path.join(os.path.dirname(__file__), f'resources/{name}.json')
    data = json.loads(open(big_input).read())
    boards, store_boards, optimize = \
            convertation_for_program(
    data['orders'], data['store'], data['optimize'])
    program = Program(boards, store_boards, optimize,
                          data['store_order'], data['width_saw'])
    program.main(3)
    
if __name__ == "__main__":
    from sys import argv
    main_test(argv[1])