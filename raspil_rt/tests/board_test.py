from ..data_structs.Board import *
import unittest


b2 = [
    [1, 100, 5],
    [1, 100, 10],
    [2, 200, 10],
    [2, 200, 20]
]

b1 = [[1, 100, 20]]
b11 = [
    [1, 100, 20],
    [1, 100, 20]
]
sb = [1, 5000, 1, 210, 4, 2]


class BoardTests(unittest.TestCase):

    def setUp(self):
        self.b1 = Board(*b2[0])
        self.b2 = Board(*b2[1])

    def tearDown(self):
        pass

    def test_copy(self):
        b = Board.copy(self.b1)
        # self.assertNotEqual(b, self.b1)
        self.assertEqual(b, self.b1)
        self.assertIsNot(b, self.b1)

    def test_sub(self):
        with self.assertRaises(NegativeSubtraction):
            b = Board.copy(self.b1)
            b -= self.b2

    def test_len(self):
        self.assertEqual(len(self.b1), 500)

    def test_add(self):
        b = Board.copy(self.b1, 1)
        b += self.b2
        self.assertEqual(b.amount, 11)

    def test_eq(self):
        b =Board.copy(self.b2) 
        b -= self.b2
        self.assertEqual(self.b1, b)

    def test_hash(self):

        self.assertEqual(self.b1, self.b2)
        self.assertNotEqual(hash(self.b1), hash(self.b2))

    def test_sstr(self):
        print(self.b1)
        self.assertNotIn('object at', str(self.b1))


class BoardCollectionTests(unittest.TestCase):
    def setUp(self):
        self.boards = BoardCollection([Board(*x) for x in b2])
        

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(len(self.boards), 2)
    
    def test_copy(self):
        b = BoardCollection.copy(self.boards)
        self.assertEqual(hash(b), hash(self.boards))
        self.assertEqual(b, self.boards)
        self.assertIsNot(b, self.boards)

    def test_append(self):
        self.assertEqual(self.boards.amount, 45)

    def test_amount(self):
        self.assertEqual(self.boards.amount, sum([x[2] for x in b2]))

    def test_sub(self):
        b = BoardCollection([Board(*x) for x in b2])
        b -= self.boards
        self.assertEqual(b.amount, 0)
    def test_eq(self):
        b1 = [[2, 100, 20], [1, 100, 20]]
        b2 = [[1, 100, 20], [2, 100, 20]]
        bb1 = BoardCollection([Board(*x) for x in b1])
        bb2 = BoardCollection([Board(*x) for x in b2])
        self.assertEqual(bb1, bb2)

    # def test_amount(self):
    #     self.assertEqual(self.boards.amount, 4)
    def test_len(self):
        self.assertEqual(self.boards.len, sum([x[1]*x[2] for x in b2]))

    def test_sstr(self):
        print(self.boards)
        self.assertNotIn('object at', str(self.boards))


class BoardCombinationsTests(unittest.TestCase):
    def setUp(self):

        self.bcc1 = BoardCollection([Board(*x) for x in b1])
        self.bcc2 = BoardCollection([Board(*x) for x in b11])
        self.sb = StoreBoard(*sb)

        self.bc1 = BoardCombinations(self.sb)
        self.bc1.append(self.bcc1)
        self.bc1.append(self.bcc2)

        bcc1 = BoardCollection([Board(*x) for x in b1])
        bcc2 = BoardCollection([Board(*x) for x in b11])
        s = StoreBoard(*sb)

        self.bc2 = BoardCombinations(self.sb)
        self.bc2.append(bcc1)
        self.bc2.append(bcc2)



    def tearDown(self):
        pass

    def test_calc_best_combination(self):
        res1 = self.bc1.calc_best_combination()
        self.assertEqual(res1[0], self.bcc2)
        
        
    def test_eq(self):
        res2 = self.bc1.calc_best_combination()
        res1 = self.bc2.calc_best_combination()
        self.assertEqual(self.bc1, self.bc2)
        


if __name__ == '__main__':
    unittest.main()
