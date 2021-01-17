from raspil_rt.data_structs.store_boards import StoreBoard, NegativeSubtraction
from typing import Callable, ItemsView, Iterable, Tuple, List, List, Dict, Union


class _Board:
    def __init__(self, id, len, rem=0, remain_p=0, store_id=0):
        """
        Обьектное представление доски
        """
        self.id = id
        self.len = len
        self.remain = rem
        self.remain_p = remain_p
        self.store_id = store_id

    def __eq__(self, o: '_Board') -> bool:
        return (self.id, self.len, self.store_id) == (o.id, o.len, o.store_id)

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self) -> str:
        return f' [{self.id}, {self.len}, {self.remain},{self.remain_p},{self.store_id}]'


class NegativeValue(Exception):
    pass


class _BoardDict(Dict[_Board, int]):
    def __init__(self, it: Iterable[Tuple[_Board, int]] = {}):
        super().__init__()
        self.update(it)

    def __getitem__(self, k: _Board) -> int:
        if k not in self:
            self[k] = 0
        return super().__getitem__(k)

    def __setitem__(self, k: _Board, v: int) -> None:
        if v < 0:
            raise NegativeValue
        return super().__setitem__(k, v)
    def __isub__(self, other:'_BoardDict'):
        for x in other.keys():
            self[x] -= other[x]
    def copy(self):
        return _BoardDict(self)

    @property
    def length(self):
        return sum([x.len * self[x] for x in self.keys()])

    @property
    def amount(self):
        return sum(self.values())

    def thin_out(self, counter=0):
        on_del = []
        for x in self.keys():
            if self[x] == counter:
                on_del.append(x)
        for x in on_del:
            self.pop(x, None)

    # def __eq__(self, o: '_Board') -> bool:
    #     return

    # def __hash__(self) -> int:
    #     return hash(str(self))

    def __str__(self) -> str:
        s = '{'
        for x in self.keys():
            s += f' {x}: {self[x]}'
        s += '}'


class _BoardCombination(List[_BoardDict]):
    def __init__(self, brd: _Board) -> None:
        self.board = brd

    def thin_out(self):

        pass

    def __eq__(self, o: '_BoardCombination') -> bool:
        if self.board != o.board and len(self) != len(o):
            return False
        for x in self:
            if x not in o:
                return False

        return True

    # def __hash__(self) -> int:
    #     return hash(str(self))

    # def __str__(self) -> str:
    #     pass


class _MapCombinations(Dict[_BoardCombination, int]):
    def __getitem__(self, k: _BoardCombination) -> int:
        if k not in self:
            self[k] = 0
        return super().__getitem__(k)


# class BoardCombinations(List[BoardCollection]):
#     '''
#     Список комбинаций для одной доски на складе
#     '''

#     def __init__(self, sb: StoreBoard) -> None:
#         super().__init__()
#         self.store_board = sb
#         self.payload = 0

#     def calc_best_combination(self, use_condition=False, lmeasure=6000, width_saw=4, long_arr=[3, 4, 5]) -> 'BoardCombinations':
#         '''
#         Кэширует результат и выдает
#         '''
#         best_board = BoardCollection()
#         pl = 0
#         for x in self:
#             if use_condition:
#                 fl = self._in_liquid_condition(
#                     x, self.store_board, lmeasure, width_saw, long_arr)
#             else:
#                 fl = True
#             p = round(100 * (x.len/self.store_board.len))
#             if fl and (p > pl or (p == pl and best_board.amount < x.amount)):
#                 best_board = x
#                 pl = p

#         b = BoardCombinations(self.store_board)
#         b.append(best_board)
#         b.payload = pl
#         return b

#     def _in_liquid_condition(self, bc: BoardCollection, sb: StoreBoard, long_m, width_saw, lm_arr):

#         lower = round(long_m * sb.remain_per * 0.01)
#         final_len = sb.len - (bc.amount * width_saw + bc.len)
#         # условие если распил не умещается в одну доску
#         if bc.amount == 1 and bc.len*2 > long_m and sb.id in lm_arr:
#             return True
#         return lower >= final_len or final_len >= sb.min_len

#     def __eq__(self, o: 'BoardCombinations') -> bool:
#         if self.store_board == o.store_board and \
#                 self[0] == o[0] and \
#                 self.payload == o.payload:
#             return True
#         return False

#     def __hash__(self) -> int:
#         d1 = [str(x) for x in self]

#         return hash(''.join(set(d1)))

#     def __str__(self) -> str:
#         s = 'Board Combinations: { \n'
#         s += f'source is {self.store_board} \n'
#         for x in self:
#             s += f'\t{x}\n'
#         return s + '\n \t}'


# class MapResult(Dict[int, Dict[BoardCombinations, int]]):
#     def __init__(self):
#         super().__init__()

#     def __iadd__(self, other: 'MapResult'):
#         for id in other.keys():
#             if self.get(id, None) is None:
#                 self[id] = other[id]
#                 continue
#             for r1 in other[id].keys():
#                 try:
#                     self[id][r1] += 1
#                 except KeyError:
#                     self[id][r1] = 1
#         return self

#     def __str__(self):
#         s = 'Map result: {\n'
#         for x in self.keys():
#             s += f'\tId: {x} => [ \n'
#             d_comb = self[x]
#             for elems in d_comb.keys():
#                 s += f'\t\tAmount: {d_comb[elems]} => [ \n]'
#                 s += f'\t\t\t {elems}'
#                 s += '\t\t] \n'
#             s += '\t] \n'
#         s += '}\n'
#         return s

#     def is_empty(self: 'MapResult') -> bool:
#         for id in self.values():
#             for bc in id:
#                 if len(bc) != 0:
#                     return False
#         return True
