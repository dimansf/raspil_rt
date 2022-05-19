from copy import copy
from typing import Any, Iterable, Iterator, List, Tuple,  Union
from collections.abc import MutableMapping


class NegativeSubtraction(Exception):
    '''
    'Negative amount of Boards'
    '''
    pass


class Board:
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
        return f'({self.id}, {self.len}, {self.sclad_id})'

    def __eq__(self, other: 'Board') -> bool:  # type:ignore
        return (self.id, self.len, self.sclad_id) == \
            (other.id, other.len,  other.sclad_id)


class StackElement:
    """
        одна стопка - доска и ее количество 
        (id=1, len=1500, sclad_id=3): 10 
    """

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
        return self.board == other.board
        # and self.amount == other.amount

    def identity(self, other: 'StackElement'):
        return self == other and self.amount == other.amount

    def __str__(self) -> str:
        return (f'({self.board}: {self.amount})')

    def __len__(self):
        """
            Общая длина всех досок в стек элементе
            amount * len mother board
        """
        return self.len * self.amount

    def __add__(self, other: 'StackElement') -> 'StackElement':
        self = copy(self)

        if self == other:
            self.amount += other.amount
            if self.amount < 0:
                raise Exception(
                    'Failed to add two StackElements self.amount < 0')
            return self

        raise Exception('Failed to add two StackElements')

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

    def __init__(self, seq: List[StackElement] = []):
        super().__init__()
        self._kpd = 0
        self.extend(seq)

    def __len__(self) -> int:
        return sum([len(x) for x in self])

    def __sub__(self, other: Union['BoardStack', Board]) -> 'BoardStack':
        other = copy(other)
        if isinstance(other, BoardStack):
            for el in other:
                el.amount = -el.amount
        if isinstance(other, Board):
            other = BoardStack([StackElement(other, -1)])

        return self + other

    def __eq__(self, other: 'BoardStack') -> bool:  # type:ignore
        try:
            return len(self) == len(other) and \
                all([x.identity(self[self.index(x)]) for x in other])
        except ValueError:
            return False

    @property
    def element_count(self):
        return super().__len__()

    def __add__(self, other: Union[StackElement, 'BoardStack']):  # type:ignore
        self = copy(self)
        if isinstance(other, StackElement):
            self.append(other)

        if isinstance(other, BoardStack):
            [self.append(x) for x in other]

        res = list(filter(lambda x: x.amount > 0, self))

        self.clear()
        self.extend(res)
        return self

    def append(self, stack_element: StackElement) -> None:
        try:
            self[self.index(stack_element)] += stack_element
        except ValueError:
            super().append(copy(stack_element))

    def extend(self, __iterable: Iterable[StackElement]) -> None:
        [self.append(x) for x in __iterable]

    def __str__(self) -> str:
        sorted_stack = sorted(self, key=lambda el: hash(str(el)))
        s = '\n [ '
        for el in sorted_stack[:-1]:
            s += f'{el}, '
        s += f' {sorted_stack[-1]}'
        return s + '] '

    def __copy__(self):
        return BoardStack([copy(x) for x in self])


class ElementCutsaw(List[BoardStack]):
    """
    board - доска
    boards_combinations - набор кучек досок
    """

    def __init__(self, store_board: Board, seq: Iterable[BoardStack] = []):
        super().__init__()
        self.store_board = store_board
        self.extend(seq)
        self._kpd = 0.0

    def __copy__(self):
        return ElementCutsaw(self.store_board, [copy(x) for x in self])

    def __eq__(self, other: 'ElementCutsaw') -> bool:  # type:ignore
        try:
            return len(self) == len(other) and \
                self.store_board == other.store_board and \
                all([bool(self.index(x)+1) for x in other])
        except ValueError:
            return False

    @property
    def kpd(self):
        if len(self) > 1:
            raise Exception(
                'too many Elements in ElementCutsaw for kpd calculating')
        return self._kpd

    def thick_off_stack_boards(self, optimize_map:  dict[int, bool], width_saw: int):
        """
            Все комбинации проверяются на возможность распила и по карте кпд выбирается 
            лучший стак - он один и остается в массиве распилов
            Карта распилов: [ -1.0, 99.20 ... ] 
        """
        if len(self) == 0:
            return None
        kpds = [self._can_to_saw(
            self.store_board, b_stack, width_saw, optimize_map[self.store_board.sclad_id]) for b_stack in self]
        best_stack = self[max(range(len(self)), key=kpds.__getitem__)]
        self._kpd = max(kpds)
        self.clear()
        self.append(best_stack)
        if len(self) > 1:
            raise Exception(
                'after thick_off_stack_boards StackBoards must be only 1')

    def _can_to_saw(self, board: Board, stack: BoardStack, width_saw: int, optimize: bool):
        """
            Возвращается кпд данного распила для этой доски 
            -1.0 если невозможно распилить по этой схеме
        """
        remain = len(board) - (width_saw *
                               (sum([x.amount for x in stack]) - 1) + len(stack))
        kpd_percentage = round((len(board) - remain) / (len(board)/100), 2)
        # 1. условие на возможность физически распилить длинномер на такие отрезки
        if remain >= 0:
            if optimize is False:
                return kpd_percentage
            else:
                if board.min_remain >= remain or \
                        board.max_remain <= remain:
                    return kpd_percentage

        return -1.0

    @property
    def _hash(self):
        return hash(str(self))

    def __hash__(self):  # type:ignore
        return hash(str(self))

    def __str__(self: 'ElementCutsaw') -> str:
        sorted_el = sorted(self, key=lambda el: hash(str(el)))
        s = '\n [' + f' {self.store_board}: '
        for el in sorted_el[:-1]:
            s += f'{el}, '
        s += f"{sorted_el[-1]}"
        return s + ' ] '


class Cutsaw(MutableMapping[ElementCutsaw, int]):
    """
       { board: [BoardStack, ...] : 1...n, 
            .... }
    """

    def __init__(self, seq: List[Tuple[ElementCutsaw, int]] = []):
        super().__init__()
        self.els: List[Tuple[ElementCutsaw, int]] = []
        self.update(seq)

    def __copy__(self):

        return Cutsaw([(copy(key), self[key]) for key in self])

    def __add__(self, other: Union['Cutsaw', ElementCutsaw]) -> 'Cutsaw':  # type:ignore
        new = copy(self)

        if isinstance(other, ElementCutsaw):
            new._sub_add__(other, 1)
        if isinstance(other, Cutsaw):
            if __debug__:
                print('other ' + str(other))
                print('new ' + str(new))
                print('self ' + str(self))

            [new._sub_add__(x, y) for (x, y) in other.items()]
        return new

    def _sub_add__(self, other: ElementCutsaw, amount: int):
        if __debug__:
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
            if hash(el) == hhash:
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

        if __debug__:
            print(str(s))
        return InnerIterator()

    def __len__(self) -> int:
        return len(self.els)

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
        self[best_element] = 1
        if len(self) > 1 or len(self.items()) > 1:
            raise Exception('select_best_stack_board doesnt work correctly')
