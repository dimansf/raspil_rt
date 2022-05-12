from typing import Any
from raspil_rt.data_structs.board import *
import unittest
from copy import copy

# id len sclad amount
boards = [
    [1, 100, 3, 10],
    [1, 100, 3, 20],
    [2, 200, 4, 10],
    [2, 200, 5, 10]
]

board1 = [[1, 100, 20]]
b11 = [
    [1, 100, 20],
    [1, 100, 20]
]
sb = [1, 5000, 1, 210, 4, 2]

b0 = Board(*boards[0])
b1 = Board(*boards[1])
b2 = Board(*boards[2])
b3 = Board(*boards[3])

stack_element1 = StackElement(b1, boards[1][3])
stack_element0 = StackElement(b0, boards[0][3])
stack_element3 = StackElement(b3, boards[3][3])      




class BoardTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass



    def test_equality(self):

        self.assertEqual(b1, b0)

    def test_sstr(self):
        print(b1)
        self.assertNotIn('object at', str(b1))


class StackElementTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

 

    def test_copy(self):
        se0 = copy(stack_element0)
        self.assertEqual(se0, stack_element0)
        self.assertIsNot(se0, stack_element0)

    def test_addition(self):
   
        se_sum = stack_element0 + stack_element1
        self.assertEqual(se_sum.amount, stack_element0.amount + stack_element1.amount)
    

    def test_sub(self):
        se_sub = stack_element0 - stack_element0
        self.assertEqual(se_sub.amount, 0)

    def test_eq(self):
        self.assertEqual(stack_element0, stack_element0)
        self.assertNotEqual(stack_element0, stack_element1)

    def test_len(self):
        self.assertEqual(len(stack_element1), boards[1][1]* boards[1][3])

    def test_sstr(self):
        print(stack_element0)
        self.assertNotIn('object at', str(stack_element0))


class BoardStackTests(unittest.TestCase):
    def setUp(self):
        pass
        

    def tearDown(self):
        pass

    def test_stack(self):
        self.stack1 = BoardStack([stack_element0, stack_element1])


    def test_eq(self):
       pass
    
    def test_wrap(self):
        class A():
            def print_helo(self, f:Any):
                return f('hello')
        class B:
            name = 'B.class'
            def build_hello(self):
                def hello(s):
                    return self.name + s
                return hello

        a = A()
        b = B()
        x = a.print_helo(b.build_hello())
        print(X)

class ElementCutsawTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
if __name__ == '__main__':
    unittest.main()
