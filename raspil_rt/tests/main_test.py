# import os
from raspil_rt.data_structs.board import Board, BoardStack, StackElement
# from raspil_rt.main import Program

import unittest

boards = [
    [1, 2000, 0, 10],
    [1, 200, 0, 10]
]
store_boards = [
    [1, 6000, 3, 10, 200, 5]
]


class MainTests(unittest.TestCase):
    
    def setUp(self):
        self.board = Board(*store_boards[0])
        self.other_boards = BoardStack(
            [StackElement(Board(*x), x[3])for x in boards])
        pass
        # p = r"C:\Users\dimansf\Documents\projects\raspil_rt\raspil_rt\tests\resources\json1.txt"

        # with open(p) as f:
        #     result = json.loads(f.read())
        #     print(len(result['store']))
        #     self.pp = Program(result['orders'], result['store'],
        #                       result['optimize'], result['scladMax'], result['widthSaw'])

    def tearDown(self):
        pass

    def test_main(self):
        pass

    # def test_combinate(self):
    #     program = Program()
    #     res = Program.combinate(program, self.board, self.other_boards)
    #     open(os.path.dirname(__file__)+'/stdout.json', 'w').write(str(res))
