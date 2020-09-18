from raspil_rt.data_structs.Board import BoardCollection
from ..data_structs.StoreBoard import *

x1 = StoreBoard(id=2732,  len=2164, amount=4, min_len=210, remain_per=4,  sclad_id=2)
x11 = StoreBoard(id=2732,  len=2164, amount=5, min_len=210, remain_per=4,  sclad_id=2)
x2 = StoreBoard(id=232,  len=2164, amount=1, min_len=210, remain_per=4,  sclad_id=2)

xs = StoreBoard(id=2732,  len=2164, amount=9, min_len=210, remain_per=4,  sclad_id=2)


store_boards = [
    [2732, 2164, 1, 210, 4, 2], 
    [2732, 2164, 10, 210, 4, 2], 
    [66, 2827, 1, 1500, 4, 2], 
    [ 66, 264, 1, 1500, 4, 1], 
    [ 66, 264, 11, 1500, 4, 1], 
    [10946, 272, 19, 1000, 4, 1]
]
print(StoreBoardCollection([StoreBoard(*x) for x in store_boards ]))
print(len(StoreBoardCollection([StoreBoard(*x) for x in store_boards ])) == 4)

print(x1 == x11)
print(hash(x1) != hash(x11))
print(hash(xs) == hash(x1+x11))
