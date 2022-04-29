from typing import List, Union, Iterable
# from collections.abc import Iterable
from raspil_rt.data_structs.boards import Board


class StackElement(List):
    def __init__(self, board:Board, amount:int=1):
        super()
        self.board = board
        self.amount = amount 
    def __add__(self, other:Union[Board, 'StackElement']):
        if isinstance(other, Board):
            pass
        if isinstance(other, StackElement):
            pass

class BoardStack(List):
    def __init__(self, elements:Iterable[StackElement]):
        super()
        self.extend(elements)
        pass