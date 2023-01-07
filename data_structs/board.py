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

    def __eq__(self, other: 'Board') -> bool:  # type:ignore
        return self._id == other._id

    def __hash__(self) -> int:
        return self._id


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

    def __contains__(self, other: Union['BoardStack', Board],  # type:ignore
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

    def __eq__(self, other: 'BoardStack') -> bool:  # type:ignore
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
        return '\n[ ' + ','.join([str(el) for el in sorted(self, key=lambda el: hash(el))]) + '] '

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
        self.last_best: CutsawElement | None = None

    def __copy__(self):
        return CutsawElement(self.store_board, [copy(x) for x in self])

    @property
    def length(self):
        return sum([el.total_len for el in self])

    def __eq__(self, other: 'CutsawElement') -> bool:  # type:ignore
        if self.store_board == other.store_board and \
                len(self) == len(other) and \
                self.length == other.length:

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

    def get_best_stack(self, condition: BoardStack = BoardStack()):
        if self.last_best and self.last_best[0] in condition:
            return self.last_best
        best = None
        if not self.sorted:
            self.sort_stacks()
        for el in self.sorted:  # type:ignore
            if el in condition:
                if best and el.remain < best.remain:
                    best = el
                if best is None:
                    best = el
        if best:
            self.last_best = CutsawElement(self.store_board, [best])
            return self.last_best
        return CutsawElement(self.store_board)

    def __iadd__(self, __x: 'CutsawElement'):  # type:ignore

        super().__iadd__(__x)

        return self

    def __str__(self: 'CutsawElement') -> str:

        return '\n {' + f' {self.store_board}: [' \
            + ','.join([str(el) for el in self]) + ']}'


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
                self.keys = list(source.elements.keys())
                self.i = -1

            def __next__(self) -> CutsawElement:
                try:
                    self.i += 1
                    return self.s.elements[self.keys[self.i]]
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
        return '{' + ','.join([f'{x}: {self[x]}' for x in self]) + '}'

    def get_best_cutsaw_elements(self,  boards:  BoardStack, store_boards: BoardStack):
        """
            Из всех досок с их картами распилов выбираем лучшую по кпд и оставляем ее

            Должен остаться один вариант доски с одним вариантом распила
             {
                 *remain: 98
                 [board: [BoardStack]] : 1
             }
        """
        if len(self) == 0:
            return None
        
        from multiprocessing import cpu_count
        
        sub_args = [(self, el, boards, store_boards) for el in self]
        from multiprocessing.pool import Pool
        with Pool(processes=cpu_count()) as pool:
            results = pool.starmap(Cutsaw.sub_get_best, sub_args)
            return min([x for x in results if x], key=lambda el: el[0].remain)
            
    def sub_get_best(self, el: CutsawElement, boards:BoardStack, store_boards:BoardStack):
        if el.store_board in store_boards:
            res = el.get_best_stack(boards)
            if len(res) == 0:
                return
            else:
                return res
