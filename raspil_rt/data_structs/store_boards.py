
from typing import List, Tuple, Union


class StoreBoard:
    def __init__(self, id, len, amount, min_len, remain_per, sclad_id) -> None:
        self.id = id
        self.len = len
        self.amount = amount
        self.min_len = min_len
        self.remain_per = remain_per
        self.sclad_id = sclad_id

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self) -> str:
        return (f'({self.id}, {self.len},  {self.amount}, {self.min_len}, {self.remain_per}, {self.sclad_id})')

    def __eq__(self, o: 'StoreBoard') -> bool:
        return (self.id, self.len, self.min_len, self.remain_per, self.sclad_id) == \
            (o.id, o.len, o.min_len, o.remain_per, o.sclad_id)

    def __isub__(self, other: 'StoreBoard'):
        self.amount -= other.amount
        if self.amount < 0:
            raise NegativeSubtraction
        return self

    def __add__(self, o: 'StoreBoard'):
        # id=2732,  len=2164, amount=4, min_len=210, remain_per=4,  sclad_id=2
        return StoreBoard(id=self.id, len=self.len, min_len=self.min_len,
                          amount=self.amount+o.amount, remain_per=self.remain_per, sclad_id=self.sclad_id)  # type: ignore


class NegativeSubtraction(Exception):
    '''
    'Negative amount of Boards'
    '''
    pass


class StoreBoardCollection(List[StoreBoard]):
    def __init__(self, seq: List[StoreBoard] = []):
        super().__init__()
        for el in seq:
            self.append(el)

    def __isub__(self, other: 'StoreBoardCollection'):
        for x in other:
            for x2 in self:
                if x == x2:
                    x2 -= x
        on_del = []
        for x in self:
            if x.amount == 0:
                on_del.append(x)
        for x in on_del:
            self.remove(x)
        return self

    def append(self, value: StoreBoard) -> None:
        if value.amount == 0:
            return
        for x in self:
            if x == value:
                x.amount += value.amount
                return
        super().append(value)

    def __str__(self) -> str:
        s = '( \n'
        for el in self:
            s += f'{el}, '
        return s + '\n ) '
