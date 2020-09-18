from ..main import *

store_boards = [[2732, 2164, 1, 210, 4, 2], [66, 2827, 1, 1500, 4, 2], [
    66, 264, 1, 1500, 4, 1], [10946, 272, 19, 1000, 4, 1]]

boards = [[2732, 150, 3], [2732, 150, 6], [2732, 150, 4], [2732, 150, 6], [2732, 150, 4], [2732, 150, 2], [
    2732, 150, 4], [2732, 150, 6], [2732, 150, 4], [2732, 150, 4], [2732, 150, 6], [2732, 150, 2]]


b1 = [[2732, 150, 2],[2732, 150, 1],[2732, 150, 7],[2732, 150, 6]] + \
[[2732, 150, 1],[2732, 150, 2],[2732, 150, 3],[2732, 150, 4],[2732, 150, 5]]

b_boards = [
    [1, 2998, 3],
    [1, 100, 5]

]
bs_boards = [
    [1, 6000, 2, 2000, 4,  2]
]


p = Program(b_boards, bs_boards) 

print(p.calc(p.boards, p.store_boards.pop()))