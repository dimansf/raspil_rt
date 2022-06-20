# import os
import json
import os
# import time
from convertation import convertation_for_program

# from raspil_rt.main import Program

import unittest

from main import Program

boards = [
    [1, 2000, 0, 10],
    [1, 200, 0, 10]
]
store_boards = [
    [1, 6000, 3, 10, 200, 5]
]

input0 = os.path.join(os.path.dirname(__file__), 'resources/input.json')
input1 = os.path.join(os.path.dirname(__file__), 'resources/json1.txt')
out1 = os.path.join(os.path.dirname(__file__), 'out.json')
class MainTests(unittest.TestCase):
    
    def setUp(self):
        self.data_path = input0
        self.out = out1
    def tearDown(self):
        pass


        

    def test_main(self):
        data = json.loads(open(self.data_path).read())
        boards, store_boards, optimize = \
            convertation_for_program(data['orders'], data['store'], data['optimize'])
        program = Program(boards, store_boards, optimize,
                          data['store_order'], data['width_saw'])
        program.main()
        with open(self.out, 'w') as f:
            f.write(str(program.resulted_cutsaw))

class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.path = input1
       

    def tearDown(self):
        pass

    def test_main(self):
        data = json.loads(open(self.path).read())
        b, s, opt = convertation_for_program(data['orders'], data['store'], data['optimize'])
        self.assertEqual(len(opt), 5)
        self.assertIsInstance(b, list)
        self.assertIsInstance(b.pop(), list)
        self.assertIsInstance(s, list)
        self.assertIsInstance(s.pop(), list)
        