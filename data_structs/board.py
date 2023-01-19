from copy import copy

from typing import Any, Iterable, Iterator, List, Tuple,  Union
from collections.abc import MutableMapping


class IncorrectIteration(Exception):
    pass


class NegativeValueError(Exception):
    '''
    'Negative amount of Boards'
    '''
    pass


class UnsortedError(Exception):
    pass


class Board():
    """
        (id=1, len=1500, sclad_id=3, min_remain, max_remain)
    """

    def __init__(self, num_id: int, length: int, sclad_id: int, _: Any = 0, min_remain: int = 0, max_remain: int = 0, *unused: Any) -> None:
        self.num_id = num_id
        self.len = length
        self.sclad_id = sclad_id
        self.max_remain = max_remain
        self.min_remain = min_remain

        self._id = id(self)

    def __str__(self) -> str:
        return f'[{self.num_id}, {self.len}, {self.sclad_id}, 0, {self.min_remain}, {self.max_remain}]'

    def str(self, amount: int) -> str:
        return f'[{self.num_id}, {self.len}, {self.sclad_id}, {amount}, {self.min_remain}, {self.max_remain}]'

    def __eq__(self, other: 'Board') -> bool:  # type: ignore[override]
        return self._id == other._id

    def is_same_board(self, other: 'Board'):
        return self.len == other.len and self.num_id == other.num_id and\
             self.sclad_id == other.sclad_id

    def __hash__(self) -> int:
        return self._id


class BSE():
    def __init__(self, b: Board, a: int) -> None:
        self.board = b
        self.amount = a


class BoardStackSet(list[BSE]):
    def __init__(self, seq: list[tuple[Board, int]] = []):
        super().__init__()
        self.fill(seq)

    def fill(self, seq: list[tuple[Board, int]] = []):
        for s in seq:
            finded = False
            for el in self:
                if s[0].is_same_board(el.board):
                    finded = True
                    el.amount += s[1]
                    break
            if not finded:
                self.append(BSE(s[0], s[1]))
        self.res = [(el.board, el.amount) for el in self]


class BoardStack(dict[Board, int]):
    """
        набор стопок досок, каждая с id и количеством в кучке
        {(id=1, len=1500, sclad_id=3): 10", 
        (id=2, len=2500, sclad_id=3): 10"
        ...}
    """

    def __init__(self, seq: list[tuple[Board, int]] = [], remain: int = -1):
        super().__init__()
        [self.__add__(p, inner=True) for p in seq]
        self.remain: int = remain

    @property
    def amount(self):
        '''Все количество палок в стаке'''
        return sum([x for x in self.values()])

    @property
    def total_len(self) -> int:
        '''Вся длина палок в стаке'''
        return sum([b.len * self[b] for b in self])

    def __contains__(self, other: Union['BoardStack', Board],  # type: ignore[override]
                     amount: int = 1) -> bool:
        '''Подмножество other входит в множество self'''
        if isinstance(other, Board):
            try:
                if self[other] < amount:
                    return False
            except KeyError:
                return False

            return True

        for k in other:
            if not self.__contains__(k, other[k]):
                return False
        return True

    def filter(self, idd: int, sclads: list[int] = [0]):
        return BoardStack([(x, self[x]) for x in self if x.num_id == idd and x.sclad_id in sclads])

    def __eq__(self, other: 'BoardStack') -> bool:  # type: ignore[override]
        '''Проверка на то что два стака равны по набору'''
        try:
            if self.remain == other.remain and self.amount == other.amount \
                    and len(self) == len(other) and self.total_len == other.total_len:

                for k in self:
                    other[k]
                return True
            else:
                return False
        except KeyError:
            return False

    def __sub__(self, other: Union['BoardStack', tuple[Board, int]]) -> 'BoardStack':
        s = copy(self)
        s.__add__(other, False, True)
        return s

    def __isub__(self, other: Union['BoardStack', tuple[Board, int]]) -> 'BoardStack':

        self.__add__(other, False, True)
        return self

    def __add__(self, other: Union['BoardStack', tuple[Board, int]],
                add: bool = True, inner: bool = False):
        if not inner:
            self = copy(self)
        if isinstance(other, tuple):
            if other[1] == 0:
                return self

            if not self.get(other[0], None):
                self[other[0]] = 0
            self[other[0]] += other[1] * (1 if add else -1)
            self.remain = -1

            if self[other[0]] < 0:
                raise NegativeValueError(
                    'Отрицательное значение количества доски при вычитании')
            if self[other[0]] == 0:
                del self[other[0]]

        if isinstance(other, BoardStack):
            [self.__add__((x, other[x]),  add, True) for x in other]

        return self

    def __str__(self) -> str:
        return '[ ' + ','.join([el.str(self[el]) for el in self]) + ']'

    def __copy__(self):
        return BoardStack(list(self.items()), self.remain)


class BoardsWrapper:
    def __init__(self, target: BoardStack) -> None:
        self.i = 0
        self.len = len(target)
        self.items = list(target.items())

    def pop(self) -> tuple[Board, int]:

        if self.i == self.len:
            raise IndexError
        else:
            res = self.items[self.i]
            self.i += 1

            return res

    def shift(self):
        self.i -= 1


class CutsawElement(List[BoardStack]):
    """
    board - доска
    boards_combinations - набор досок комбинаций
    """
    array_size = 2

    def __init__(self, store_board: Board, seq: Iterable[BoardStack] = [],
                 lb: BoardStack | None = None):
        super().__init__()
        self.store_board = store_board
        self.extend(seq)

        self.last_best: BoardStack | None = lb

    def __copy__(self):
        return CutsawElement(self.store_board, [copy(x) for x in self],
                             lb=self.last_best)

    def __eq__(self, other: 'CutsawElement') -> bool:  # type: ignore[override]
        if self.store_board == other.store_board :

            return self.last_best == other.last_best

        return False

    def add_best(self, other: BoardStack):
        if len(self) == CutsawElement.array_size:

            smallest = sorted(
                self, key=lambda el: el.remain - other.remain)[-1]
            self[self.index(smallest)] = other
            return
        self.append(other)

    def get_best_stack(self, condition: BoardStack = BoardStack()):

        res = sorted([el for el in self if el in condition],
                     key=lambda el: el.remain)
        try:
            self.last_best = res[0]
            return self
        except IndexError:
            self.last_best = None
            return self

    def __iadd__(self, __x: 'CutsawElement'):  # type: ignore[override]

        super().__iadd__(__x)

        return self

    def str(self: 'CutsawElement', amount: int) -> str:

        return '\n { " store_board":' + f' {self.store_board.str(amount)},' \
            + f'"amount":{amount},' + \
            '"boards":' + f'{self.last_best}' \
            if self.last_best else '' + '}'
    def __str__(self) -> str:   # type: ignore[override]
        
        raise NotImplemented()


class Cutsaw(MutableMapping[CutsawElement, int]):
    """
       { board: [BoardStack, ...] : 1...n, 
            .... }
    """

    def __init__(self, seq: List[Tuple[CutsawElement, int]] = []):
        super().__init__()
        self.elements: dict[int, CutsawElement] = {}
        self.vals: dict[int, int] = {}
        self.update(seq)

    def __getitem__(self, el: CutsawElement) -> int:
        for i in self.elements:
            if self.elements[i] == el:
                return self.vals[i]
        raise KeyError

    def __setitem__(self, el: CutsawElement, val: int) -> None:
        finded = False
        for i in self.elements:
            if self.elements[i] == el:
                self.vals[i] = val
                finded = True
                break
        if not finded:
            new_index = len(self.elements) + 1
            self.elements[new_index] = el
            self.vals[new_index] = val

    def __delitem__(self, key: CutsawElement) -> None:
        for i in self.elements:
            if self.elements[i] == key:
                del self.elements[i]
                del self.vals[i]
                return
        raise KeyError

    def __iter__(self) -> Iterator[CutsawElement]:
        s = self

        class InnerIterator:

            def __init__(self, source: Cutsaw) -> None:
                super().__init__()
                self.s = source
                self.keys = list(source.elements.values())
                self.i = -1

            def __next__(self) -> CutsawElement:
                try:
                    self.i += 1
                    return self.keys[self.i]
                except IndexError:
                    if self.i < len(self.s.elements):
                        raise IncorrectIteration
                    raise StopIteration

            def __iter__(self):
                return s.__iter__()

        return InnerIterator(self)

    def __copy__(self):

        return Cutsaw([(copy(key), self[key]) for key in self])

    def __add__(self, other: Union['Cutsaw', CutsawElement],
                amount: int = 1, inner: bool = False) -> 'Cutsaw':
        if not inner:
            self = copy(self)

        if isinstance(other, CutsawElement):
            try:
                self[other] += amount
            except KeyError:
                self.setdefault(other, amount)
        if isinstance(other, Cutsaw):
            [self.__add__(x, y, True) for (x, y) in other.items()]
        return self

    def __len__(self) -> int:
        return len(self.elements)

    def __str__(self):
        return '[' + ','.join([f'{x.str(self[x])}' for x in self]) + ']'


class CutsawList(list[CutsawElement]):
    def get_best_cutsaw_elements(self,  boards:  BoardStack, store_boards: BoardStack):
        """
            Возращаем  CutsawElement с минимальным остатком
        """
        remain_max = -1

        stores = [el for el in self if el.store_board in store_boards]
        bests = sorted([el.get_best_stack(boards) for el in stores],
                       key=lambda el: el.last_best.remain 
                       if el and el.last_best else remain_max)
        try:
            return next(x for x in bests if x.last_best and\
                 x.last_best.remain != -1)
           
        except (AttributeError , IndexError , StopIteration):
            return None
