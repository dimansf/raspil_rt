from typing import Dict


class Board:
    def __init__(self, id, len, amount) -> None:
        self.id = id
        self.len = len
        self.amount = amount
    
    def __len__(self):
        self.amount * self.len

    def __hash__(self) -> int:
        h = f'({self.id}, {self.len}, {self.amount})'
        print(h)
        return hash(h)
    

class BoardCollection(dict):
    def __init__(self, bc=False) -> None:
        super()
    
    def __len__(self):
        pass

    def __getitem__(self, key):
        print(key)
        return None


