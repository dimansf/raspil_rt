from typing import List, Union
from raspil_rt.data_structs.boards import Board


class StackElement(List):
    def __init__(self):
        pass
    def __add__(self, other:Union[Board, 'StackElement']):
        if isinstance(other, Board):
            pass
        if isinstance(other, StackElement):
            pass

class BoardStack(List):
    def __init__(self):
        pass