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
        return self.len == other.len and self.num_id == other.num_id and self.sclad_id == other.sclad_id

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

    def __init__(self, store_board: Board, seq: Iterable[BoardStack] = []):
        super().__init__()
        self.store_board = store_board
        self.extend(seq)
        self.sorted: List[BoardStack] | None = None
        self.last_best: BoardStack | None = None
        self.best1 = BoardStack()
        self.best2 = BoardStack()

    def __copy__(self):
        return CutsawElement(self.store_board, [copy(x) for x in self])

    @property
    def length(self):
        return sum([el.total_len for el in self])

    @property
    def total_amount(self):
        return sum([el.amount for el in self])

    def __eq__(self, other: 'CutsawElement') -> bool:  # type: ignore[override]
        if self.store_board == other.store_board and \
                len(self) == len(other) and \
                self.length == other.length and \
                self.total_amount == other.total_amount:
            if len(self) > 100:
                return True
            for el in self:
                eq = False
                for el2 in other:
                    if el == el2:
                        eq = True
                        break
                if not eq:
                    return False

            return True
        return False

    def sort_stacks(self):
        self.sorted = sorted(self, key=lambda bs: bs.remain)

    def add_best(self, el: BoardStack):
        if el.remain == -1:
            return
        if self.best1.remain == -1:
            self.best1 = el
            return
        if self.best2.remain == -1:
            self.best2 = el
            return
        if max(self.best2.remain, self.best1.remain) > el.remain:
            if self.best2.remain > self.best1.remain:
                self.best2 = el
            else:
                self.best1 = el

    def get_best_stack(self, condition: BoardStack = BoardStack()):

        b1 = self.best1 if self.best1.remain != -1 else None
        b2 = self.best2 if self.best2.remain != -1 else None

        if b1 and b2:
            br1 = b1 in condition
            br2 = b2 in condition
            if br1 and br2:
                self.last_best = b1 if b1.remain < b2.remain and br1 else b2
                return self
            if br1 or br2:
                self.last_best = b1 if br1 else b2
                return self
        if b1 or b2:
            b = b1 if b1 else b2
            self.last_best = b if b and b in condition else None
            if self.last_best: return self
        return None

    def __iadd__(self, __x: 'CutsawElement'):  # type: ignore[override]

        super().__iadd__(__x)

        return self

    def str(self: 'CutsawElement', amount: int) -> str:

        return '\n { " store_board":' + f' {self.store_board.str(amount)},' \
            + f'"amount":{amount},' + \
            '"boards":[' + ','.join([str(el) for el in self]) + ']}'


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

    def get_best_cutsaw_elements(self,  boards:  BoardStack, store_boards: BoardStack):
        """
            Из всех досок с их картами распилов выбираем лучшую по кпд и оставляем ее

            Должен остаться один вариант доски с одним вариантом распила
             {
                 *remain: 98
                 [board: [BoardStack]] : 1
             }
        """
        best = None
        stores = [el for el in self if el.store_board in store_boards]
        for el in stores:
            res = el.get_best_stack(boards)
            if res and not best:
                best = res
            if res and best and best.last_best and res.last_best and res.last_best.remain < best.last_best.remain:
                best = res
        return best
