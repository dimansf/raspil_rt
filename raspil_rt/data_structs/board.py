from shutil import copy
from typing import Callable, Iterable, List, Union


class NegativeSubtraction(Exception):
    '''
    'Negative amount of Boards'
    '''
    pass


class Board:
    """
        (id=1, len=1500, sclad_id=3)
    """
    def __init__(self, id, len, sclad_id) -> None:
        self.id = id
        self.len = len
        self.sclad_id = sclad_id

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self) -> str:
        return (f'{({self.id}, {self.len}, {self.sclad_id})}')

    def __eq__(self, other: 'Board') -> bool:
        return (self.id, self.len, self.sclad_id) == \
            (other.id, other.len,  other.sclad_id)


class StackElement:
    """
        одна стопка - доска и ее количество 
        (id=1, len=1500, sclad_id=3): 10 штук
    """
    def __init__(self: 'StackElement', board: Board, amount: int):
        self.board = board
        self.amount = amount

    def __eq__(self, other):
        return self.board == other.board

    def __str__(self) -> str:
        return (f'{self.board}: {self.amount}')

    def __len__(self):
        return self.board.len * self.amount

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

    def __copy__(self):
        return StackElement(self.board, self.amount)


class BoardStack(List[StackElement]):
    """
        набор стопок досок, каждая с id и количеством в кучке
        [(id=1, len=1500, sclad_id=3):10, ...]
    """
    def __init__(self: 'BoardStack', seq: List[Board] = [], src: List = []):
        super().__init__()
        self.src = src
        self.extend(seq)

    def boards_in_stack(self: 'BoardStack')-> int:
        return sum([x.amount for x in self])

    def __len__(self: 'BoardStack')-> int:
        return sum([len(x) for x in self])

    def __sub__(self: 'BoardStack', other: 'BoardStack') ->'BoardStack':
        other = copy(other)
        for el in other:
            el.amount = -el.amount

        return self + other

    def __add__(self: 'BoardStack', other: Union[StackElement, 'BoardStack'])-> 'BoardStack':
        self = copy(self)
        if isinstance(other, StackElement):
            self.append(other)

        if isinstance(other, BoardStack):
            [self.append(x) for x in other]
        func: Callable[[StackElement], bool] = lambda x: x.amount > 0
        res = list(filter(func, self))
        if len(self) != len(res):
            self.clear()
            self.extend(res)
        return self

    def append(self: 'BoardStack', stack_element: StackElement) -> None:
        try:
            self[self.index(stack_element)] += stack_element
        except ValueError:
            super().append(copy(stack_element))

    def __str__(self: 'BoardStack') -> str:
        s = '[ \n'
        for el in self:
            s += f'{el}, '
        return s + '\n ] '

    def __copy__(self: 'BoardStack'):
        return BoardStack([StackElement(x.board, x.amount) for x in self], src=self.src)


class ElementCutsaw(List[BoardStack]):
    """
    board - доска
    boards_combinations - набор кучек досок
    """
    def __init__(self, board:'ElementCutsaw', seq: Iterable[BoardStack] = []):
        self.board = board
        self.board_stack.extend(seq)

    def __copy__(self):
        raise Exception('is not defined')

    def __add__(self, other):
        pass


class Cutsaw(List[ElementCutsaw]):
    def __init__(self, board, seq: List[BoardStack] = []):
        pass

    def __copy__(self):
        raise Exception('__copy__ is not defined')
