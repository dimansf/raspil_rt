

import json
import os.path
from pathlib import Path
from raspil_rt.data_structs.board import Board, Cutsaw, BoardStack, BoardsWrapper, CutsawElement

from raspil_rt.convertation import TimeCounter, convertation_for_program


import unittest

from raspil_rt.main import Program

from datetime import datetime


input_dict = {
    'big':  os.path.join(os.path.dirname(__file__), 'resources/big.json'),
    'small': os.path.join(os.path.dirname(__file__), 'resources/small.json')
}


out = os.path.join(os.path.dirname(__file__),
                   f'out/temp/out_{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}.txt')

time_log = os.path.join(os.path.dirname(__file__), 'out/time.txt')

def ff():
    def prnt(ct: Cutsaw):
        print(ct)
    return prnt


class MainTests(unittest.TestCase):

    def setUp(self):
        self.data_path = input_dict['big']
        self.out = out
        self.t = TimeCounter(Path(time_log))
        self.data = json.loads(open(self.data_path).read())
        self.boards, self.store_boards, self.optimize = \
            convertation_for_program(
                self.data['orders'], self.data['store'], self.data['optimize'])
        self.store_order = self.data['store_order']
        self.width_saw = self.data['width_saw']

        self.program = Program(self.boards, self.store_boards, self.optimize,
                               self.store_order, self.width_saw)

    def tearDown(self):
        pass

    def test_main(self):

        
        self.t.mark('test_main')
        self.program.main()
        self.t.mark('test_main')
        self.t.write()
        with open(self.out, 'w') as f:
            f.write(str(self.program.resulted_cutsaw))

    def test___init__(self):
        pass

    def test_iteration(self):
        self.t.mark('test_iteration')
        self.program.iteration([1])
        self.t.mark('test_iteration')
        self.t.write()
        with open(self.out, 'w') as f:
            f.write(str(self.program.resulted_cutsaw))

    def test_calculate(self):
        store_boards = BoardStack([
            (Board(1, 2000, 3, 1, 200, 600), 3),
            (Board(1, 3000, 3, 1, 200, 600), 3),
            (Board(2, 3000, 4, 1, 200, 600), 3),
        ])
        boards = BoardStack([
            (Board(1, 100, 0, ), 30),
            (Board(1, 300, 0, ), 41),
            (Board(2, 300, 0, ), 41),
            (Board(3, 300, 0, ), 41),
        ])
        self.program.boards = boards
        self.program.store_boards = store_boards
        res = self.program.calculate([3], 1)
        self.assertIsNot(res, None)

    def test_select_and_subtract(self):

        store_boards = BoardStack([
            (Board(1, 2000, 3, 1, 200, 600), 3),
            (Board(1, 3000, 3, 1, 200, 600), 3),
        ])
        boards = BoardStack([
            (Board(1, 100, 0, ), 30),
            (Board(1, 300, 0, ), 41),
        ])
        self.program.boards = boards
        self.program.store_boards = store_boards
        res = self.program.calculate_per_boards(boards, store_boards)
        cut = self.program.select_and_subtract(res)

        self.assertIsNot(list(cut.keys())[0].last_best, None)

    def test_calculate_per_boards(self):
        store_boards = BoardStack([
            (Board(1, 2000, 3, 1, 200, 600), 3),
            (Board(1, 3000, 3, 1, 200, 600), 3),
        ])
        boards = BoardStack([
            (Board(1, 100, 0, ), 10),
            (Board(1, 300, 0, ), 11),
        ])
        res = self.program.calculate_per_boards(boards, store_boards)
        self.assertEqual(len(res), 2)

    def test_combinate(self):
        store_board = Board(1, 2000, 3, 1, 200, 600)
        boards = BoardStack([
            (Board(1, 100, 0, ), 10),
            (Board(1, 300, 0, ), 11),
        ])
        res = self.program.combinate(BoardsWrapper(
            boards), store_board, CutsawElement(store_board))
        self.assertIs(res.last_best, None)
        res.get_best_stack(boards)
        self.assertIsNot(res.last_best, None)

    def test_cutsaw_condition(self):
        self.program.optimize_map[3] = True

        store_board = Board(1, 2000, 3, 1, 200, 600)
        board = Board(1, 200, 0, )
        bs = BoardStack([(
            Board(1, 996, 0, ), 2
        )])
        bs2 = BoardStack([(
            Board(1, 500, 0, ), 2
        )])
        res1 = self.program.cutsaw_condition(bs, board, 0, store_board)
        res2 = self.program.cutsaw_condition(bs2, board, 2, store_board)

        self.assertEqual(res1, 2003 - 2*996 - 0*200 - 2*3)
        self.assertEqual(res2, -1)


class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.path = input_dict['small']

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
