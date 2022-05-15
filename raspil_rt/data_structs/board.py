from copy import copy
from typing import Dict, Iterable, List, Tuple,  Union


class NegativeSubtraction(Exception):
    '''
    'Negative amount of Boards'
    '''
    pass


class Board:
    """
        (id=1, len=1500, sclad_id=3)
    """

    def __init__(self, id: int, len: int, sclad_id: int, min_remain: int = 0, max_remain: int = 0, *_) -> None:
        self.id = id
        self.len = len
        self.sclad_id = sclad_id
        self.max_remain = max_remain
        self.min_remain = min_remain

    def __len__(self):
        return self.len

    def __str__(self) -> str:
        return f'"({self.id}, {self.len}, {self.sclad_id})"'

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
        return self.board == other.board and self.amount == other.amount

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

        if other.board == self.board:
            self.amount += other.amount
            if self.amount < 0:
                raise Exception(
                    'Failed to add two StackElements self.amount < 0')
            return self

        raise Exception('Failed to add two StackElements')

    def __sub__(self, other: 'StackElement') -> 'StackElement':
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

    def __init__(self, seq: List[StackElement] = []):
        super().__init__()
        self._kpd = 0
        self.extend(seq)

    def boards_in_stack(self) -> int:
        return sum([x.amount for x in self])

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
                bool([self.index(x) for x in other]) or True
        except ValueError:
            return False

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

    def __str__(self) -> str:
        s = '\n [ '
        for el in self:
            s += f'{el}, '
        return s + '] '

    def __copy__(self):
        return BoardStack([copy(x) for x in self])


class ElementCutsaw(List[BoardStack]):
    """
    board - доска
    boards_combinations - набор кучек досок
    """

    def __init__(self: 'ElementCutsaw', store_board: Board, seq: Iterable[BoardStack] = []):
        super().__init__()
        self.store_board = store_board
        self.extend(seq)
        self._kpd = 0.0

    def __copy__(self: 'ElementCutsaw'):
        return ElementCutsaw(self.store_board, [copy(x) for x in self])

    def __eq__(self: 'ElementCutsaw', other: 'ElementCutsaw') -> bool:  # type:ignore
        try:
            return len(self) == len(other) and \
                self.store_board == other.store_board and \
                bool([self.index(x) for x in other]) or True
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
            Карта распилов: [ -1.0, 0.86 ... ] 
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

    def __str__(self: 'ElementCutsaw') -> str:
        s = '\n [' + f' {self.store_board}: '
        for el in self:
            s += f'{el}, '
        return s + ' ] '


class Cutsaw(Dict[ElementCutsaw, int]):
    """
       { board: [BoardStack, ...] : 1...n, 
            .... }
    """

    def __init__(self, seq: List[Tuple[ElementCutsaw, int]] = []):
        super().__init__()
        pass

    def __add__(self, other: Union['Cutsaw', ElementCutsaw]) -> 'Cutsaw':  # type:ignore
        self = copy(self)

        if isinstance(other, ElementCutsaw):
            self._sub_add__(other, 1)
        if isinstance(other, Cutsaw):
            [self._sub_add__(x, y) for (x, y) in other.items()]
        return self

    def _sub_add__(self, other: ElementCutsaw, amount: int):
        try:
            self[other] += amount
        except KeyError:
            self.setdefault(other, amount)

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
        if len(self) == 0: return None

        [el.thick_off_stack_boards(optimize_map, width_saw)
         for el in self.keys()]

        best_element = max(self.keys(), key=lambda x: x.kpd)
        self.clear()
        self[best_element] = 1
        if len(self) > 1 or len(self.items()) > 1:
            raise Exception('select_best_stack_board doesnt work correctly')

    def __copy__(self):

        return Cutsaw([(copy(var1), num) for (var1, num) in self.items()])
