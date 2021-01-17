from raspil_rt.main import Program
from raspil_rt.data_structs.boards import _BoardDict

import json
import unittest


boards = [[1, 1000, 6], [1, 700, 4], [1, 200, 5], [1, 5000, 3]]
store_boards = [[1, 5000, 5, 500, 5, 5]]

class MainTests(unittest.TestCase):
    def setUp(self):

        self.program = Program(boards, store_boards)
        
    def preSet(self):
        p = r"C:\Users\dimansf\Documents\projects\raspil_rt\raspil_rt\tests\resources\json1.txt"

        with open(p) as f:
            result = json.loads(f.read())
            print(len(result['store']))
            self.pp = Program(result['orders'], result['store'],
                              result['optimize'], result['scladMax'], result['widthSaw'])

    def tearDown(self):
        pass

    def test_main(self):
        res = self.program._combinate(_BoardDict(), self.program.boards, self.program.store_boards.popitem()[0])
        self.assertFalse(res)


