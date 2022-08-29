from copy import copy
# import json
from typing import Any, Iterable, Iterator, List, Tuple,  Union
from collections.abc import MutableMapping


class NegativeValueError(Exception):
    '''
    'Negative amount of Boards'
    '''
    pass


class SubtractionError(Exception):
    m = 'Failed to add/subtract two StackElements self.amount < 0'

    def __init__(self) -> None:
        super().__init__(self.m)


class Board():
    """
        (id=1, len=1500, sclad_id=3)
    """

    def __init__(self, id: int, len: int, sclad_id: int, _: Any, min_remain: int = 0, max_remain: int = 0, *unused: Any) -> None:
        self.id = id
        self.len = len
        self.sclad_id = sclad_id

        self.max_remain = max_remain
        self.min_remain = min_remain

    def __len__(self):
        return self.len

    def __str__(self) -> str:
        return f'[{self.id}, {self.len}, {self.sclad_id}]'

    def __eq__(self, other: 'Board') -> bool:  # type:ignore
        return (self.id, self.len, self.sclad_id) == \
            (other.id, other.len,  other.sclad_id)

    def __hash__(self) -> int:
        return hash(str(self))


class StackElement():
    """
        одна стопка - доска и ее количество 
        (id=1, len=1500, sclad_id=3): 10 
    """

    def __hash__(self) -> int:
        return hash(str(self))

    def __init__(self, board: Board, amount: int):
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

    def __eq__(self, other: 'StackElement'):  # type:ignore
        return self.board == other.board #\
            # and self.amount == other.amount

    def __str__(self) -> str:
        return ('{'+f'{self.board}: {self.amount}'+'}')

    def __len__(self):
        """
            Общая длина всех досок в стек элементе
            amount * len mother board
        """
        return self.len * self.amount

    def __add__(self, other: 'StackElement') -> 'StackElement':
        self = copy(self)

        if self.board == other.board:
            self.amount += other.amount
            if self.amount < 0:
                raise SubtractionError()
            return self

        raise SubtractionError()

    def __sub__(self, other: 'StackElement') -> 'StackElement':
        other = copy(other)
        other.amount = - other.amount
        return self + other

    def __copy__(self):

        return StackElement(self.board, int(self.amount))


class BoardStack(List[StackElement]):
    """
        набор стопок досок, каждая с id и количеством в кучке
        [(id=1, len=1500, sclad_id=3):10, ...]
    """

    def __init__(self, seq: List[StackElement] = [], kpd: float = 0.0):
        super().__init__()
        self.kpd = kpd
        self.extend(seq)
        self._kpd = -1.0

    @property
    def amount(self):
        ''' сумма всех досок в стаке '''
        return sum([x.amount for x in self])

    @property
    def length(self):
        ''' сумма элементов стака, длина массива '''
        return sum([len(x) for x in self])

    def __eq__(self, other: 'BoardStack') -> bool:  # type:ignore
        if self.length == other.length and \
                self.amount == other.amount and \
                len(self) == len(other):
            pass
        else:
            return False

        try:
            self.sort(key=lambda el: hash(el))
            other.sort(key=lambda el: hash(el))

            res = all([self[x] == other[x] for x in range(len(self))])

            return res
        except ValueError:
            return False

    def __hash__(self) -> int:  # type:ignore
        return hash(str(self))

    def __contains__(self, other: Union['BoardStack', 'StackElement']):  # type:ignore
        if isinstance(other, StackElement):
            try:
                i = self.index(other)
                return True if i >= 0 and self[i].amount >= other.amount else False
            except ValueError:
                return False
        
        for el in self:
            if el not in other:
                return False                
        return True

    def __sub__(self, other: Union['BoardStack', StackElement]) -> 'BoardStack':
        other = copy(other)
        if isinstance(other, BoardStack):
            for el in other:
                el.amount = -el.amount
        if isinstance(other, StackElement):
            other.amount = -other.amount

        return self + other

    def __add__(self, other: Union[StackElement, 'BoardStack']):  # type:ignore
        self = copy(self)
        if isinstance(other, StackElement):
            self.append(other)

        if isinstance(other, BoardStack):
            [self.append(x) for x in other]

        return self
    def equal(self,other:StackElement):
        pass

    def append(self, stack_element: StackElement) -> None:
        if stack_element.amount == 0:
            return

        try:
            # проблема в том что они равны но не идентичны
            res = self.pop(self.index(stack_element)) + stack_element
            if res.amount > 0:
                super().append(res)
            if res.amount < 0:
                raise NegativeValueError()
        except ValueError:
            if stack_element.amount > 0:
                super().append(copy(stack_element))
            if stack_element.amount < 0:
                raise NegativeValueError()

    def extend(self, __iterable: Iterable[StackElement]) -> None:
        [self.append(x) for x in __iterable]

    def __str__(self) -> str:
        self.sort(key=lambda el: hash(el))

        return '\n[ ' + ','.join([str(el) for el in self]) + '] '

    def __copy__(self):
        return BoardStack([copy(x) for x in self], self.kpd)


class ElementCutsaw(List[BoardStack]):
    """
    board - доска
    boards_combinations - набор кучек досок
    """

    def __init__(self, store_board: Board, seq: Iterable[BoardStack] = []):
        super().__init__()
        self.store_board = store_board
        self.extend(seq)

    def __copy__(self):
        return ElementCutsaw(self.store_board, [copy(x) for x in self])

    @property
    def length(self):
        return sum([el.length for el in self])

    def __eq__(self, other: 'ElementCutsaw') -> bool:  # type:ignore
        if len(self) == len(other) and \
                self.store_board == other.store_board and \
                self.length == other.length:
            pass
        else:
            return False
        try:
            return all([bool(self.index(x)+1) for x in other])

        except ValueError:
            return False

    def __hash__(self):  # type:ignore
        return hash(str(self))

    def select_best_stack_board(self, limit_to: BoardStack):
        '''
        Выбирает лучший распил для этой доски чтобы в них было множество досок которыми
        ограничен отбор @limit_to
        '''
        best_stack = None
        for el in self:
            if el in limit_to:
                if best_stack and best_stack.kpd < el.kpd:
                    best_stack = el
                if best_stack is None:
                    best_stack = el
        if best_stack:
            return ElementCutsaw(self.store_board, [best_stack])
        return

    def calc_kpd_and_order_stack_boards(self, optimize_map:  dict[int, bool], width_saw: int):
        """
            Все комбинации проверяются на возможность распила 
            Сортируются по убыванию КПД

        """
        if len(self) == 0:
            return
        [self.calculate_kpd(
            self.store_board, b_stack, width_saw, optimize_map[self.store_board.sclad_id])
            for b_stack in self]
        els = filter(lambda el: el.kpd > 0.0, self)
        self.clear()
        self.extend(els)
        self.sort(key=lambda x: x.kpd)
        self.reverse()

    def calculate_kpd(self, board: Board, stack: BoardStack, width_saw: int, optimize: bool):
        """
            -1.0  если невозможно распилить по этой схеме распила
            от 0 до 100 - КПД
        """
        if stack.amount == 0:
            return
        if stack.amount < 0:
            raise NegativeValueError()

        remain = len(board) - (width_saw *
                               (stack.amount - 1) + len(stack))
        if remain < 0:
            return
        kpd = 100.0 - round(remain / (len(board)/100), 2)
        '''  возможность распилить длинномер на такие отрезки c учетом
            оптимизации '''
        if optimize is False:
            stack.kpd = kpd
            return
        if board.min_remain >= remain or \
                board.max_remain <= remain:
            stack.kpd = kpd

    def __str__(self: 'ElementCutsaw') -> str:
        sorted_el = sorted(self, key=lambda el: hash(el))
        return '\n {' + f' {self.store_board}: [' \
            + ','.join([str(el) for el in sorted_el]) + ']}'


class Cutsaw(MutableMapping[ElementCutsaw, int]):
    """
       { board: [BoardStack, ...] : 1...n, 
            .... }
    """

    def __init__(self, seq: List[Tuple[ElementCutsaw, int]] = []):
        super().__init__()
        self._d:dict[ElementCutsaw, int] = {}
        self.update(seq)

    def __hash__(self) -> int:  # type:ignore
        return hash(str(self))

    def __copy__(self):

        return Cutsaw([(copy(key), self[key]) for key in self])
    def __len__(self) -> int:
        return len(self._d)
    def __add__(self, other: Union['Cutsaw', ElementCutsaw]) -> 'Cutsaw':  # type:ignore
        new = copy(self)

        if isinstance(other, ElementCutsaw):
            new.sub_add__(other, 1)
        if isinstance(other, Cutsaw):
            [new.sub_add__(x, y) for (x, y) in other.items()]
        return new

    def sub_add__(self, other: ElementCutsaw, amount: int):
        try:
            self[other] += amount
        except KeyError:
            self.setdefault(other, amount)

    def __getitem__(self, __k: ElementCutsaw) -> int:
        hhash = hash(__k)
        for key in self._d:
            if hash(key) == hhash:
                return self._d[key]
        raise KeyError

    def  __setitem__(self, __k: ElementCutsaw, __v: int) -> None:
        self._d[__k] = __v

    def __delitem__(self, __k: ElementCutsaw) -> None:
        if self._d.get(__k, None):
            self._d.pop(__k)
        raise KeyError

    def __iter__(self) -> Iterator[ElementCutsaw]:
        return iter(self._d)


    def delete_unusable_boards(self, boards: list[Board]):
        on_delete: list[ElementCutsaw] = []
        for key in self:
            if key.store_board not in boards:
                on_delete.append(key)
        for el in on_delete:
            self.pop(el)

    def __str__(self):
        return '{' + ','.join([f'{x}: {self[x]}' for x in self]) + '}'

    def select_and_order_cutsaw_elements(self,  optimize_map:  dict[int, bool], width_saw: int):
        """
            1 - выбираем те что можно распилить
            2 - сортируем по КПД стаки распилов
        """
        if len(self) == 0:
            return

        [key.calc_kpd_and_order_stack_boards(optimize_map, width_saw)
         for key in self]

        els = filter(lambda key: len(key), self)

        self.clear()
        [self.setdefault(val, 1) for val in els]

    def select_good_element_cutsaw(self, store_boards: BoardStack, boards: BoardStack):
        s_boards = [el.board for el in store_boards]
        best = None
        for key in self:
            if key.store_board in s_boards:
                best_stack = key.select_best_stack_board(boards)
                if best is None:
                    best = best_stack
                if best and best_stack and best[0].kpd < best_stack[0].kpd:
                    best = best_stack
        return best
