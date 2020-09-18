from typing import  Tuple, List


class Board:
    def __init__(self, id, len, amount) -> None:
        self.id = id
        self.len = len
        self.amount = amount
    @staticmethod  
    def copy(dup:'Board', amount=False):
        return Board(dup.id, dup.len, amount if amount is not False else dup.amount)
    def __len__(self):
        self.amount * self.len
    
    def __eq__(self, o: object) -> bool:
        return (self.id, self.len) == (o.id, o.len) # type: ignore
    
    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self) -> str:
        return f'( {self.id}, {self.len}, {self.amount} )'
    

class BoardCollection(List[Board]):
    
    def __init__(self, seq:List[Board]=[]) -> None:
        super().__init__()
        for el in seq:
            self.append(el)
    
    @staticmethod
    def copy(bc:'BoardCollection'): 
        bcn = BoardCollection()
        for el in bc:
            bcn.append(Board.copy(el))
        return bcn

    def append(self, el):
        for x in self:
            if el == x:
                x.amount += el.amount
                return 
        super().append(el) 
    
    
    def total_amount(self):
        return sum([x.amount for x in self])
                
    def __len__(self) -> int:
        return sum([x.amount*x.len for x in self])
    
    def __str__(self):
        s = 'Collection: (\n'
        for b in self:
            s += f'{b},  '
        return s + '\n)'
    
    
class BoardCombinations(List[BoardCollection]):
    def __str__(self) -> str:
        s = 'Board Combinations: { \n'
        for x in self:
            s += f'\t{x}\n'
        return s + '\n }'



