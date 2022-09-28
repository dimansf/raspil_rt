from copy import copy
# import json
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
        return self.board == other.board
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

        if self == other:
            self.amount += other.amount
            if self.amount < 0:
                raise Exception(
                    'Failed to add/subtract two StackElements self.amount < 0')
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

    def __init__(self, seq: List[StackElement] = [], kpd: float = 0.0):
        super().__init__()
        self.kpd = kpd
        self.extend(seq)

    def __len__(self) -> int:
        return sum([len(x) for x in self])
    
    @property
    def amount(self):
        ''' количество стопок в стаке'''
        return super().__len__()
    def __eq__(self, other: 'BoardStack') -> bool:  # type:ignore
       
        try:
           
            self.sort(key=lambda el: hash(el))
            other.sort(key=lambda el: hash(el))

            res =   self.amount == other.amount and \
                all([self[x] == other[x] for x in range(self.amount)])
            
            return res
        except ValueError:
        
            return False

    def __hash__(self) -> int:  # type:ignore
        return hash(str(self))

    @property
    def element_count(self):
        return super().__len__()

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

        if any([x.amount < 0 for x in self]):
            raise Exception(
                'Incorrect behavior BoardStack.__add__ amount of Stackelement lower than 0')

        res = list(filter(lambda x: x.amount > 0, self))

        self.clear()
        self.extend(res)
        return self

    def append(self, stack_element: StackElement) -> None:
        if stack_element.amount == 0:
            return 
        # + addition
        if stack_element.amount > 0:
            try:
                self[self.index(stack_element)] += stack_element
            except ValueError:
                super().append(copy(stack_element))
        # - subtraction
        else:
            self[self.index(stack_element)] += stack_element

    def extend(self, __iterable: Iterable[StackElement]) -> None:
        [self.append(x) for x in __iterable]

    def __str__(self) -> str:
        return '\n[ ' + ','.join([str(el) for el in sorted(self, key=lambda el: hash(el))]) + '] '



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
    def length(self):
        return sum([len(el) for el in self])

    def __eq__(self, other: 'ElementCutsaw') -> bool:  # type:ignore
        if self.store_board == other.store_board and \
                len(self) == len(other) and \
                self.length == other.length:
                
            pass
        else:
            return False
        try:
            ar1 = sorted(self, key=lambda el: hash(el))
            ar2 = sorted(other, key=lambda el: hash(el))
            return all([hash(ar1[x]) == hash(ar2[x])  for x in range(len(ar1))])

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
        """
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

        # if debug:
        #     print(str(s))
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
            raise Exception('select_best_stack_board doesnt work correctly: items more than 1')
