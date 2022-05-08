from copy import copy, deepcopy
from typing import Callable, Iterable, List, NamedTuple, Tuple, Union


class NegativeSubtraction(Exception):
    '''
    'Negative amount of Boards'
    '''
    pass


class Board:
    """
        (id=1, len=1500, sclad_id=3)
    """

    def __init__(self:'Board', id:int, len:int, sclad_id:int, *_) -> None:
        self.id = id
        self.len = len
        self.sclad_id = sclad_id

    def __len__(self:'Board'):
        return self.len

    def __str__(self:'Board') -> str:
        return f'"({self.id}, {self.len}, {self.sclad_id})"'

    def __eq__(self:'Board', other: 'Board') -> bool: #type:ignore
        return (self.id, self.len, self.sclad_id) == \
            (other.id, other.len,  other.sclad_id)


class StackElement:
    """
        одна стопка - доска и ее количество 
        (id=1, len=1500, sclad_id=3): 10 
    """

    def __init__(self: 'StackElement', board: Board, amount: int):
        self.board = board
        self.amount = amount

    @property
    def id(self):
        return self.board.id

    @property
    def len(self):
        """
        Не тоже самое что и __Len__
        возвращает длину материнской доски
        """
        return self.board.len

    @property
    def sclad_id(self):
        return self.board.sclad_id

    def __eq__(self, other:'StackElement'): #type:ignore
        return self.board == other.board and self.amount == other.amount

    def __str__(self) -> str:
        return (f'({self.board}: {self.amount})')

    def __len__(self):
        """
            Общая длина всех досок в стек элементе
            amount * len mother board
        """
        return self.len * self.amount

    def __add__(self: 'StackElement', other: Union['StackElement', Board]) -> 'StackElement':
        self = copy(self)
        if isinstance(other, StackElement):
            if other.board == self.board:
                self.amount += other.amount
                if self.amount < 0:
                    raise Exception(
                        'Failed to add two StackElements self.amount < 0')
                return self
        if isinstance(other, Board):
            if other == self.board:
                self.amount += 1
                return self

        raise Exception('Failed to add two StackElements')
    def __sub__(self: 'StackElement', other: Union['StackElement', Board]) -> 'StackElement':
        self = copy(other)
        other.amount = - other.amount
        return self + other
    def __copy__(self):
        return StackElement(self.board, self.amount)


class BoardStack(List[StackElement]):
    """
        набор стопок досок, каждая с id и количеством в кучке
        [(id=1, len=1500, sclad_id=3):10, ...]
    """
    def __init__(self: 'BoardStack', seq: List[StackElement] = []):
        super().__init__()
        
        self.extend(seq)

    def boards_in_stack(self: 'BoardStack') -> int:
        return sum([x.amount for x in self])

    def __len__(self: 'BoardStack') -> int:
        return sum([len(x) for x in self])

    def __sub__(self: 'BoardStack', other: 'BoardStack') -> 'BoardStack':
        other = copy(other)
        for el in other:
            el.amount = -el.amount

        return self + other

    def __eq__(self, other:'BoardStack') -> bool: #type:ignore
        try:
            return len(self) == len(other) and \
                bool([self.index(x) for x in other]) or True
        except ValueError:
            return False

    
    def __add__(self: 'BoardStack', other: Union[StackElement, 'BoardStack']) -> 'BoardStack': #type:ignore
        self = copy(self)
        if isinstance(other, StackElement):
            self.append(other)

        if isinstance(other, BoardStack):
            [self.append(x) for x in other]
        func: Callable[[StackElement], bool] = lambda x: x.amount > 0
        res = list(filter(func, self))
        
        self.clear()
        self.extend(res)
        return self

    def append(self: 'BoardStack', stack_element: StackElement) -> None:
        try:
            self[self.index(stack_element)] += stack_element
        except ValueError:
            super().append(copy(stack_element))

    def __str__(self: 'BoardStack') -> str:
        s = '\n [ '
        for el in self:
            s += f'{el}, '
        return s + '] '

    def __copy__(self: 'BoardStack'):
        return BoardStack([copy(x) for x in self])


class ElementCutsaw(List[BoardStack]):
    """
    board - доска
    boards_combinations - набор кучек досок
    """

    def __init__(self:'ElementCutsaw', board: Board, seq: Iterable[BoardStack] = []):
        super().__init__()
        self.board = board
        self.boards_combinations = seq

    def __copy__(self:'ElementCutsaw'):
        return ElementCutsaw([copy(x) for x in self]) #type:ignore

   
        
    def __eq__(self:'ElementCutsaw', other: 'ElementCutsaw') -> bool: #type:ignore
        try:
            len(self) == len(other)  and  [self.index(x) for x in other] #type:ignore
        except ValueError:
            return False
    def __str__(self: 'ElementCutsaw') -> str:
        s = '\n [' + f' {self.board}: '
        for el in self:
            s += f'{el}, '
        return s + ' ] '

class Cutsaw(List[ElementCutsaw]):
    def __init__(self, seq: List[BoardStack] = []):
        super().__init__()
        pass
    
    def __add__(self, other: 'ElementCutsaw'):  #type:ignore
        self = copy(self)
        # [self.append(x) for x in other]

        return self
    def append(self, other:'ElementCutsaw') -> None:  #type:ignore
        try:
            self[self.index(other)] += other
        except ValueError:
            super().append(copy(other))
    def __copy__(self):
        raise Exception('__copy__ is not defined')
