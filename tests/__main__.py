import json
import os
from raspil_rt.convertation import TimeCounter
from  raspil_rt.convertation import convertation_for_program
from raspil_rt.tests.main_test import input_dict
from raspil_rt.main import Program

from datetime import datetime




out = os.path.join(os.path.dirname(__file__),
                   'out/out_' + datetime.now().strftime("%Y%m%d%H%M") + '.json')

time_log = os.path.join(os.path.dirname(__file__), 'out/time.txt')

def main_test():
    data_path = input_dict['small']
    
    t = TimeCounter(str(time_log))
    data = json.loads(open(data_path).read())
    boards, store_boards, optimize = \
        convertation_for_program(
            data['orders'], data['store'], data['optimize'])
    store_order = data['store_order']
    width_saw = data['width_saw']

    program = Program(boards, store_boards, optimize,
                            store_order, width_saw)
    t.mark('prog')
    boards, s_boards = program.to_order_boards_by_id([1])
    program.current_sclad_id = [1]

    sub_result = program.calculate_per_id(boards, s_boards)
    t.mark('prog')
    t.write()
    with open(out, 'w') as f:
        f.write(str(program.resulted_cutsaw))
if __name__ == "__main__":
   
    main_test()