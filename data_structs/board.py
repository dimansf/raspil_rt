from copy import copy

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
        return self.id









        

class BoardStack(dict[Board, int]):
    """
        набор стопок досок, каждая с id и количеством в кучке
        {(id=1, len=1500, sclad_id=3): 10", 
        (id=2, len=2500, sclad_id=3): 10"
        ...}
    """

    def __init__(self, seq: list[tuple[Board, int]] = [], remain: int = 0):
        super().__init__()
        self.remain = remain
        [self.__add__(p) for p in seq]

    @property
    def amount(self):
        return sum([ x for x in self.values()])
    @property
    def total_len(self) -> int:
        return sum([b.len * self[b] for b in self])
    
    def __contains__(self, other: 'BoardStack') -> bool: # type:ignore
        try:
            for k in self:
                if other[k] < self[k]:
                    return False
        except:
            return False
        
        return True
        
    def __eq__(self, other: 'BoardStack') -> bool:  # type:ignore
        try:
            if self.amount == other.amount and len(self) == len(other):

                for k in self:
                    other[k]
                return True
            else:
                return False
        except KeyError:
            return False
    

    def __sub__(self, other: Union['BoardStack', tuple[Board,int]]) -> 'BoardStack':
        
        self.__add__(other, False)

        return self

    def __add__(self, other: Union['BoardStack', tuple[Board,int]], fl:bool=True):  # type:ignore
        
        if isinstance(other, tuple):
            c = self.get(other[0], None)
            if c:
                self[other[0]] += other[1] * 1 if fl else -1
            else: 
                self[other[0]] = other[1] * 1 if fl else -1
            if self[other[0]] < 0:
                    raise Exception('Отрицательное значение количества доски при вычитании')
            if self[other[0]] == 0:
                del self[other[0]]

        if isinstance(other, BoardStack):
            [self.__add__((x, other[x])) for x in other]
  
        return self

    def __str__(self) -> str:
        return '\n[ ' + ','.join([str(el) for el in sorted(self, key=lambda el: hash(el))]) + '] '

    def __copy__(self):
        return BoardStack(list(self.items()), self.remain)

class BoardsWrapper:
    def __init__(self, target:BoardStack) -> None:
        self.i = 0
        self.len = len(target)
        self.t = list(target.items())
        
    def pop(self):
        self.i -= 1
        return self.t[self.i+1]
    def append(self):
        self.i += 1
        return self.t[self.i-1]
    
    
class CutsawElement(List[BoardStack]):
    """
    board - доска
    boards_combinations - набор досок комбинаций
    """

    def __init__(self, store_board: Board, seq: Iterable[BoardStack] = []):
        super().__init__()
        self.store_board = store_board
        self.extend(seq)

    def __copy__(self):
        return CutsawElement(self.store_board, [copy(x) for x in self])
    
    def length(self):
        return sum([el.total_len for el in self])

    def __eq__(self, other: 'CutsawElement') -> bool:  # type:ignore
        if self.store_board == other.store_board and \
                len(self) == len(other) and \
                self.length == other.length:
                
            for el in self:
                
                fl = False
                for el2 in other:
                    if el.total_len == el2.total_len and el == el2:
                        fl = True
                        break
                if not fl:
                    return False
                
            return True
        return False

                
        
        
    def append(self, __object: BoardStack) -> None:
        return super().append(__object)

    def __hash__(self) -> int:  # type:ignore
        return hash(str(self))

    def get_best_stack(self, condition:BoardStack=BoardStack()):
        best=None
        for el in self:
            if el in condition:
                if best and  el.remain < best.remain:
                    best = el
                if best is None:
                    best = el
            
        return best
        

    
    def __iadd__(self, __x: 'CutsawElement') -> 'CutsawElement':  # type:ignore
       
        super().__iadd__(__x)

        return self

    

    @property
    def _hash(self):
        return hash(str(self))

    def __str__(self: 'CutsawElement') -> str:
        sorted_el = sorted(self, key=lambda el: hash(el))
        return '\n {' + f' {self.store_board}: [' \
            + ','.join([str(el) for el in sorted_el]) + ']}'


class Cutsaw(MutableMapping[CutsawElement, int]):
    """
       { board: [BoardStack, ...] : 1...n, 
            .... }
    """

    def __init__(self, seq: List[Tuple[CutsawElement, int]] = []):
        super().__init__()
        self.els: List[Tuple[CutsawElement, int]] = []
        self.update(seq)

    def __hash__(self) -> int:  # type:ignore
        return hash(str(self))

    def __copy__(self):

        return Cutsaw([(copy(key), self[key]) for key in self])

    def __add__(self, other: Union['Cutsaw', CutsawElement]) -> 'Cutsaw':  # type:ignore
        new = copy(self)

        if isinstance(other, CutsawElement):
            new._sub_add__(other, 1)
        if isinstance(other, Cutsaw):
            if debug:
                print('other ' + str(other))
                print('new ' + str(new))

            [new._sub_add__(x, y) for (x, y) in other.items()]
        return new

    def _sub_add__(self, other: CutsawElement, amount: int):
        if debug:
            print('sub add ' + str(self))
        try:
            self[other] += amount
        except KeyError:
            self.setdefault(other, amount)

    def __getitem__(self, __k: CutsawElement) -> int:
        hhash = hash(__k)
        for el in self.els:
            if hash(el[0]) == hhash:
                return el[1]
        raise KeyError

    def __setitem__(self, __k: CutsawElement, __v: int) -> None:
        hhash = hash(__k)
        for el in self.els:
            if hash(el[0]) == hhash:
                self.els.remove(el)
        self.els.append((__k, __v))

    def __delitem__(self, __v: CutsawElement) -> None:
        hhash = hash(__v)
        for el in self.els:
            if hash(el[0]) == hhash:
                return self.els.remove(el)
        raise KeyError

    def __iter__(self) -> Iterator[CutsawElement]:
        s = self

        class InnerIterator(Iterator[CutsawElement]):
            
            def __init__(self) -> None:
                super().__init__()
                self.x = -1
            def __next__(self) -> CutsawElement:

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
