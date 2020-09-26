from raspil_rt.data_structs.StoreBoard import StoreBoard, NegativeSubtraction
from typing import Callable, Tuple, List, List, Dict


class Board:
    '''
    Абстракция доски в распиле пришедшей в заказ
    '''

    def __init__(self, id, len, amount) -> None:
        self.id = id
        self.len = len
        self.amount = amount

    @staticmethod
    def copy(dup: 'Board', amount=-1):
        return Board(dup.id, dup.len, amount if amount != -1 else dup.amount)

    def __len__(self) -> int:
        return self.amount * self.len

    def __isub__(self, other: 'Board'):
        if self == other:
            self.amount -= other.amount
            if self.amount < 0:
                raise NegativeSubtraction
        return self

    def __iadd__(self, other):
        if self == other:
            self.amount += other.amount
        return self

    def __eq__(self, o: object) -> bool:
        return (self.id, self.len) == (o.id, o.len)  # type: ignore

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self) -> str:
        return f'( {self.id}, {self.len}, {self.amount} )'





class BoardCollection(List[Board]):
    '''
    Список Досок из заказа. Имеют несколько полезных методов
    '''

    def __init__(self, seq: List[Board] = []) -> None:
        super().__init__()
        for el in seq:
            self.append(el)

    @staticmethod
    def copy(bc: 'BoardCollection'):
        bcn = BoardCollection()
        for el in bc:
            bcn.append(Board.copy(el))
        return bcn

    def append(self, el: Board):
        for x in self:
            if el == x:
                x.amount += el.amount
                return
        super().append(el)

    @property
    def amount(self) -> int:
        return sum([x.amount for x in self])

    def __isub__(self, other: 'BoardCollection'):
        del_list = []
        for board in other:
            for b in self:
                if b == board:
                    b -= board
        for x in self:
            if x.amount == 0:
                del_list.append(x)
        for x in del_list:
            self.remove(x)
        return self

    def __eq__(self, o: 'BoardCollection') -> bool:
        d1 = [str(x) for x in self]
        d2 = [str(x) for x in o]
        return set(d1) == set(d2)

    @property
    def len(self) -> int:
        return sum([x.amount*x.len for x in self])

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self):
        s = 'Collection: (\n'
        for b in self:
            s += f'{b},'
        return s + '\n\t)'


class BoardCombinations(List[BoardCollection]):
    '''
    Список комбинаций для одной доски на складе
    '''

    def __init__(self, sb: StoreBoard) -> None:
        super().__init__()
        self.store_board = sb
        self.payload = 0

    def calc_best_combination(self, use_condition=False, lmeasure=6000, width_saw=4, long_arr=[3,4,5]) -> 'BoardCombinations':
        '''
        Кэширует результат и выдает
        '''
        best_board = BoardCollection()
        pl = 0
        for x in self:
            if use_condition:
                fl = self._in_liquid_condition(x, self.store_board, lmeasure, width_saw, long_arr)
            else: fl = True
            p = round(100 * (x.len/self.store_board.len))
            if fl and (p > pl or  (p == pl and best_board.amount < x.amount)):
                best_board = x
                pl = p
            
        b = BoardCombinations(self.store_board)
        b.append(best_board)
        b.payload = pl
        return b

    def _in_liquid_condition(self, bc: BoardCollection, sb: StoreBoard, long_m, width_saw, lm_arr):

        lower = round(long_m * sb.remain_per * 0.01)
        final_len = sb.len - (bc.amount * width_saw + bc.len)
        # условие если распил не умещается в одну доску
        if bc.amount == 1 and bc.len*2 > long_m and sb.id in lm_arr:
            return True
        return lower >= final_len or final_len >= sb.min_len

    def __eq__(self, o: 'BoardCombinations') -> bool:
        if self.store_board == o.store_board and \
                self[0] == o[0] and \
                self.payload == o.payload:
            return True
        return False
   
    def __hash__(self) -> int:
        d1 = [str(x) for x in self]
        
        return hash(''.join(set(d1)))
    def __str__(self) -> str:
        s = 'Board Combinations: { \n'
        s+= f'source is {self.store_board} \n'
        for x in self:
            s += f'\t{x}\n'
        return s + '\n \t}'


class MapResult(Dict[int, Dict[BoardCombinations, int]]):
    def __init__(self):
        super().__init__()

    def __iadd__(self, other: 'MapResult'):
        for id in other.keys():
            if self.get(id, None) is None:
                self[id] = other[id]
                continue
            for r1 in other[id].keys():
                try:
                    self[id][r1] += 1
                except KeyError:
                    self[id][r1] = 1
        return self

    def __str__(self):
        s = 'Map result: {\n'
        for x in self.keys():
            s += f'\tId: {x} => [ \n'
            d_comb = self[x]
            for elems in d_comb.keys():
                s += f'\t\tAmount: {d_comb[elems]} => [ \n]'
                s += f'\t\t\t {elems}'
                s += '\t\t] \n'
            s += '\t] \n'
        s += '}\n'
        return s

        
        

    def is_empty(self: 'MapResult') -> bool:
        for id in self.values():
            for bc in id:
                if len(bc) != 0:
                    return False
        return True
