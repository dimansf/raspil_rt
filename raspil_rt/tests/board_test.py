from ..data_structs.Board import *

b1 = [[2732, 150, 2],[2732, 150, 1],[2732, 150, 7],[2732, 150, 6]] + \
[[27, 150, 1],[27, 150, 2],[27, 150, 3],[27, 150, 4],[27, 150, 5]]

boards = BoardCollection([Board(x[0], x[1], x[2]) for x in b1])

print(boards)
print(len(boards) == 2)
