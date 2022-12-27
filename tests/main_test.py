
import json
import os.path

from raspil_rt.convertation import TimeCounter, convertation_for_program


import unittest

from raspil_rt.main import Program

boards = [
    [1, 2000, 0, 10],
    [1, 200, 0, 10]
]
store_boards = [
    [1, 6000, 3, 10, 200, 5]
]



big_input = os.path.join(os.path.dirname(__file__), 'resources/big.json')
small1_input = os.path.join(os.path.dirname(__file__), 'resources/small.json')

out1 = os.path.join(os.path.dirname(__file__), 'out/out.json')

time_log = os.path.join(os.path.dirname(__file__), 'out/time.txt')


class MainTests(unittest.TestCase):

    def setUp(self):
        self.data_path = big_input
        self.out = out1
        self.t = TimeCounter(str(time_log))

    def tearDown(self):
        pass

    def test_main(self):
        self.t.mark('prog')
        data = json.loads(open(self.data_path).read())
        boards, store_boards, optimize = \
            convertation_for_program(
                data['orders'], data['store'], data['optimize'])
        program = Program(boards, store_boards, optimize,
                          data['store_order'], data['width_saw'])
        program.main()
        self.t.mark('prog')
        self.t.write()
        with open(self.out, 'w') as f:
            f.write(str(program.resulted_cutsaw))


class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.path = big_input

    def tearDown(self):
        pass

    def test_main(self):
        data = json.loads(open(self.path).read())
        b, s, opt = convertation_for_program(
            data['orders'], data['store'], data['optimize'])
        self.assertEqual(len(opt), 5)
        self.assertIsInstance(b, list)
        self.assertIsInstance(b.pop(), list)
        self.assertIsInstance(s, list)
        self.assertIsInstance(s.pop(), list)
