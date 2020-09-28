
from ..data_structs.store_boards import *
import unittest

# store_boards = [
#     [2732, 2164, 1, 210, 4, 2], 
#     [2732, 2164, 10, 210, 4, 2], 
#     [66, 2827, 1, 1500, 4, 2], 
#     [ 66, 264, 1, 1500, 4, 1], 
#     [ 66, 264, 11, 1500, 4, 1], 
#     [10946, 272, 19, 1000, 4, 1]
sb = [
    [1, 1000, 1, 200, 4, 2],
    [1, 1000, 5, 200, 4, 2],
]


class StoreBoardTests(unittest.TestCase):
    def setUp(self):
        self.b1 = StoreBoard(*sb[0])
        self.b2 = StoreBoard(*sb[1])

    def tearDown(self):
        pass

    def test_equal(self):
        b =StoreBoard(*sb[0])
        b.amount = 10
        self.assertEqual(self.b1, b)
    
    def test_isub(self):
        b =StoreBoard(*sb[0])
        b -= self.b1
        self.assertEqual(b.amount, 0)
        with self.assertRaises(NegativeSubtraction):
            b -= self.b1
    def test_sub(self):
        b =StoreBoard(*sb[0])
        b += self.b1
        self.assertEqual(b.amount, 2)


class StoreBoardCollectionTests(unittest.TestCase):
    def setUp(self):
        self.sb = StoreBoardCollection([StoreBoard(*x) for x in sb])  
      

    def tearDown(self):
        pass

    def test_isub(self):
       ss = StoreBoardCollection([StoreBoard(*x) for x in sb]) 
       ss -= self.sb
       self.assertEqual(len(ss), 0)
    def test_append(self):
        ss = StoreBoardCollection([StoreBoard(*x) for x in sb])
        ss.append(self.sb[0])
        self.assertEqual(sum([x.amount for x in ss]), 12) 
        