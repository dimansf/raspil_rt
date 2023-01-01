from copy import copy
from functools import cached_property
from typing import Any, Iterable, Iterator, List, Tuple,  Union
from collections.abc import MutableMapping

debug = False


class NegativeValueError(Exception):
    '''
    'Negative amount of Boards'
    '''
    pass


class Board():
    """
        (id=1, len=1500, sclad_id=3, min_remain, max_remain)
    """

    def __init__(self, num_id: int, length: int, sclad_id: int, _: Any, min_remain: int = 0, max_remain: int = 0, *unused: Any) -> None:
        self.num_id = num_id
        self.len = length
        self.sclad_id = sclad_id
        self.max_remain = max_remain
        self.min_remain = min_remain
        self.str = f'[{self.num_id}, {self.len}, {self.sclad_id}]'
        self.hash = hash(str(self))
        self.id = id(self)

   

    def __str__(self) -> str:
        return self.str

    def __eq__(self, other: 'Board') -> bool:  # type:ignore
        return id(self) == id(other)

    def __hash__(self) -> int:
        return self.hash


def board_builder(boards: list[Board]):
    pass


class StackElement():
    """
        одна стопка - доска и ее количество 
        (id=1, len=1500, sclad_id=3): 10 
    """

    def __hash__(self) -> int:
        return self.hash

    def __init__(self, board: Board, amount: int, stack_dict: dict[Board, list['StackElement']]):
        self.board = board
        self.amount = amount
        self.hash = hash(str(self))
        self.num_id = self.board.num_id
        self.sclad_id = self.board.sclad_id
        self.str = ('{'+f'{self.board}: {self.amount}'+'}')
        self.len = self.board.len * self.amount
        self.stack_base = stack_dict
        self.id = id(self)

    def identity(self, other: 'StackElement'):
        return id(self) == id(other)

    def __eq__(self, other: 'StackElement'):  # type:ignore
        return self.board == other.board

    def __str__(self) -> str:
        return self.str

    

    def __add__(self, other: 'StackElement', sub: bool = False) -> 'StackElement':

        if self.board == other.board:
            try:
                if sub:
                    return self.stack_base[self.board][self.amount - other.amount]
                else:
                    return self.stack_base[self.board][self.amount + other.amount]

            except IndexError:
                raise Exception(
                    'Failed to add two StackElements amount < 0')

        raise Exception('Failed to add two StackElements')

    def __sub__(self, other: 'StackElement') -> 'StackElement':
        return self.__add__(other, True)


def stack_board_builder(stack_boards: list[StackElement]) -> dict[int, list[StackElement]]:
    pass


class BoardStack(dict[int, StackElement]):
    """
        набор стопок досок, каждая с id и количеством в кучке
        {(id=1, len=1500, sclad_id=3): "StackElement(id=1, len=1500, sclad_id=3):10", 
        ...}
    """

    def __init__(self, se: list[StackElement], kpd: float = 0.0):
        super().__init__()
        self.kpd = kpd
        [self.append(x) for x in se]

    @property
    def amount(self):
        return sum([x.amount for x in self.values()])
    
    def shallow_eq_sign(self):
        return [[el, self[el].len] for el in self]

    def __eq__(self, other: 'BoardStack') -> bool:  # type:ignore
        try:
            if self.amount == other.amount and len(self.keys()) == len(other.keys()):

                for k in self:
                    other[k]
                return True
            else:
                return False
        except KeyError:
            return False
    @property
    def total_len(self) -> int:
        return sum([el.len for el in self.values()])

    def __sub__(self, other: Union['BoardStack', StackElement]) -> 'BoardStack':
        if isinstance(other, BoardStack):
            for el in other.values():
                self.append(el, False)
        if isinstance(other, StackElement):
            self.append(other, False)

        return self

    def __add__(self, other: Union[StackElement, 'BoardStack'])-> 'BoardStack':
        if isinstance(other, BoardStack):
            for el in other.values():
                self.append(el)
        if isinstance(other, StackElement):
            self.append(other)
        return self

    def append(self, stack_element: StackElement, add:bool=True) -> None:
        if stack_element.amount == 0:
            return
        # + addition
        board = stack_element.board
        res = self.pop(board.id, None)
        if add:
            if res:
                self[board.id] = res.stack_base[board][res.amount + stack_element.amount]
            else:
                self[board.id] = stack_element.stack_base[board][stack_element.amount]
        # - subtraction
        else:
            try:
                if res:
                    self[board.id] = res.stack_base[board][res.amount - stack_element.amount]
                else:
                    raise KeyError()
            except KeyError:
                raise Exception(
                'Некорректное вычитание BoardStack.append()')

    def extend(self, __iterable: Iterable[StackElement]) -> None:
        [self.append(x) for x in __iterable]

    def __str__(self) -> str:
        return '\n[ ' + ','.join([str(el) for el in sorted(self, key=lambda el: hash(el))]) + '] '

    def __copy__(self):
        return BoardStack([x for x in self.values()], self.kpd)


class ElementCutsaw(List[BoardStack]):
    """
    board - доска
    boards_combinations - набор досок комбинаций
    """

    def __init__(self, store_board: Board, seq: Iterable[BoardStack] = []):
        super().__init__()
        self.store_board = store_board
        self.extend(seq)

    def __copy__(self):
        return ElementCutsaw(self.store_board, [copy(x) for x in self])
    @property
    def total_len(self):
        return sum([el.total_len for el in self])

    def total_amount(self):
        return sum([el.amount for el in self])
    
    
    def __eq__(self, other: 'ElementCutsaw') -> bool:  # type:ignore
        return self.shallow_eq(self, other) # type:ignore

    def shallow_eq(self, other: 'ElementCutsaw') -> bool:
        if not self.store_board == other.store_board or \
            not self.total_len == other.total_len or \
            not self.total_amount == other.total_amount:
            return False
        try:
            ar1 = self
            ar2 = 
            return all([hash(ar1[x]) == hash(ar2[x]) for x in range(len(ar1))])

        except ValueError:
            return False
        

    def __hash__(self) -> int:  # type:ignore
        return hash(str(self))

    @property
    def kpd(self):
        if len(self) > 1:
            raise Exception(
                'too many Elements in ElementCutsaw for kpd calculating')
        return -1.0 if next(iter(self), 0) is 0 else self[0].kpd

    def thick_off_stack_boards(self, optimize_map:  dict[int, bool], width_saw: int):
        """
            Все комбинации проверяются на возможность распила и по карте кпд выбирается 
            лучший стак - он один и остается в массиве распилов
            Карта распилов: [ -1.0, 99.20 ... ] 
        """
        if len(self) == 0:
            return None
        [self._kpd_to_saw(
            self.store_board, b_stack, width_saw, optimize_map[self.store_board.sclad_id])
            for b_stack in self]
        kpds = [x.kpd for x in self]
        best_stack = self[max(range(len(self)), key=kpds.__getitem__)]

        self.clear()
        self.append(best_stack) if best_stack.kpd > 0 else None
        if len(self) > 1:
            raise Exception(
                'after thick_off_stack_boards StackBoards must be only 0-1')

    def __iadd__(self, __x: 'ElementCutsaw') -> 'ElementCutsaw':  # type:ignore

        super().__iadd__(__x)

        return self

    def _kpd_to_saw(self, board: Board, stack: BoardStack, width_saw: int, optimize: bool):
        """
            Возвращается кпд данного распила для этой доски 
            -1.0 если невозможно распилить по этой схеме
        
          
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
        kpd = round(100.0 - remain / (len(board)/100), 2)
        '''  возможность распилить длинномер на такие отрезки c учетом
            оптимизации '''
        if optimize is False:
            stack.kpd = kpd
            return
        if board.min_remain >= remain or \
                board.max_remain <= remain:
            stack.kpd = kpd

    @property
    def _hash(self):
        return hash(str(self))

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
        self.els: List[Tuple[ElementCutsaw, int]] = []
        self.update(seq)

    def __hash__(self) -> int:  # type:ignore
        return hash(str(self))

    def __copy__(self):

        return Cutsaw([(copy(key), self[key]) for key in self])

    def __add__(self, other: Union['Cutsaw', ElementCutsaw]) -> 'Cutsaw':  # type:ignore
        new = copy(self)

        if isinstance(other, ElementCutsaw):
            new._sub_add__(other, 1)
        if isinstance(other, Cutsaw):
            if debug:
                print('other ' + str(other))
                print('new ' + str(new))

            [new._sub_add__(x, y) for (x, y) in other.items()]
        return new

    def _sub_add__(self, other: ElementCutsaw, amount: int):
        if debug:
            print('sub add ' + str(self))
        try:
            self[other] += amount
        except KeyError:
            self.setdefault(other, amount)

    def __getitem__(self, __k: ElementCutsaw) -> int:
        hhash = hash(__k)
        for el in self.els:
            if hash(el[0]) == hhash:
                return el[1]
        raise KeyError

    def __setitem__(self, __k: ElementCutsaw, __v: int) -> None:
        hhash = hash(__k)
        for el in self.els:
            if hash(el[0]) == hhash:
                self.els.remove(el)
        self.els.append((__k, __v))

    def __delitem__(self, __v: ElementCutsaw) -> None:
        hhash = hash(__v)
        for el in self.els:
            if hash(el[0]) == hhash:
                return self.els.remove(el)
        raise KeyError

    def __iter__(self) -> Iterator[ElementCutsaw]:
        s = self

        class InnerIterator(Iterator[ElementCutsaw]):
            x = -1

            def __next__(self) -> ElementCutsaw:

                self.x += 1
                try:
                    return s.els[self.x][0]
                except:
                    raise StopIteration

            def __iter__(self):
                return InnerIterator()

        return InnerIterator()

    def __len__(self) -> int:
        return len(self.els)

    def __str__(self):
        return '{' + ','.join([f'{x}: {self[x]}' for x in self]) + '}'

    def thick_off_cutsaw_elements(self,  optimize_map:  dict[int, bool], width_saw: int):
        """
            Из всех досок с их картами распилов выбираем лучшую по кпд и оставляем ее
            остальные удаляем
            Должен остаться один вариант доски с одним вариантом распила
             {
                 *kpd: 98.33
                 [board: [BoardStack]] : 1
             }
        """
        if len(self) == 0:
            return None

        [el.thick_off_stack_boards(optimize_map, width_saw)
         for el in self.keys()]

        best_element = max(self.keys(), key=lambda x: x.kpd)

        self.clear()
        self.setdefault(best_element, 1) if best_element.kpd > 0 else None
        if len(self) > 1 or len(self.items()) > 1:
            raise Exception(
                'select_best_stack_board doesnt work correctly: items more than 1')
