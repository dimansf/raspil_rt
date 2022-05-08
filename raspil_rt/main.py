
from ast import Index
from typing import List, Dict, NamedTuple, Union
from xml.dom.minidom import Element
from cached_property import cached_property
from raspil_rt.data_structs.board import Board, BoardStack, Cutsaw, ElementCutsaw, StackElement


class Program:
    def __init__(self: 'Program', boards: List[List[int]]=[], store_boards: List[List[int]]=[],
                 optimize=True, sclad_max=True, width_saw=4):
        self.src_boards = boards
        self.src_store_boards = store_boards
        self.boards = BoardStack(
            [StackElement(Board(x[0], x[1], -1), x[3]) for x in boards])
        self.store_boards = BoardStack(
            [StackElement(Board(x[0], x[1], x[4]), x[3]) for x in store_boards])
        self.optimize = optimize
        self.sclad_max = sclad_max
        self.width_saw = width_saw

        self.ids = set([x.id for x in self.boards])

        self.map_result = []

    @property
    def longmeasures(self):
        return (3, 4, 5)

    @property
    def shortsmeasures(self):
        return (1, 2)

    def main(self):
        counter = 0
        while(True):
            counter = self.iteration(self.longmeasures
                                     if self.sclad_max else self.longmeasures)
            if counter > 0:
                continue

            self.iteration(self.shortsmeasures + self.longmeasures)
            if counter > 0:
                continue

            self.optimize = False
            counter = self.iteration(self.shortsmeasures + self.longmeasures)
            if counter == 0:
                break

    def iteration(self, sclad_id=[]) -> int:
        map_r = self.calc_per_id(sclad_id)
        self.iteration_subtraction(map_r)
        self.map_result += map_r
        return map_r.is_empty()

    def iteration_subtraction(self, mr ):
        for m in mr.values():
            for d in m.keys():
                self.boards -= d[0]
                self.store_boards -= BoardStack([d.store_board])

    @cached_property
    def map_longmeasures(self):
        res = dict()
        #  процент нижней границы высчитывается из максимальной палки с 5 склада
        lngms = [x for x in self.store_boards if x.sclad_id == 5]
        for x in lngms:
            res[x.id] = x.len if res.get(x.id, 0) < x.len else res[x.id]
        return res

    def optimize_selection(self, res) :
        bests = []
        for bc in res:
            bests.append(bc.calc_best_combination(self.optimize,
                                                  self.map_lmeasures[bc.store_board.id],
                                                  self.width_saw,
                                                  self.sclad_map['longs']))
        try:
            best = bests.pop()
        except:
            return {}
        for bb in bests:
            if best.payload < bb.payload:
                best = bb
        return {best: 1}

    def calculate_per_id(self, sclad_ids: List[int] = []) -> Cutsaw:
        results = Cutsaw()
        for id in self.ids:
            boards = BoardStack(
                [x for x in self.boards if x.id == id])
            store_boards = BoardStack(
                [x for x in self.store_boards if x.id == id and x.sclad_id in sclad_ids])
            # 1. просчитать потенциально возможные комбинации
            res = self.calculate_per_boards(boards, store_boards)
            # 2. отсеять неподходящие распилы
            if sum([len(x[0]) for x in res.keys()]) != 0:
                results[id] = res  # type:ignore

        return results

    def calculate_per_boards(self, boards: BoardStack, store_boards: BoardStack):
        '''
        Палки и их возможные комбинации распилов
        '''
        res = Cutsaw()
        for board in store_boards:
            el = self.combinate_boards(
                board.board, boards)
        return res

    def can_to_saw(self, coll, b: Board, i: int, bs):
        ttl = coll.len + coll.amount * self.width_saw + b.len * i + i * self.width_saw
        if bs.len - ttl >= - self.width_saw:
            return True
        return False

    

    def combinate(self,  board: Board, other_boards: BoardStack, current_stack: BoardStack = BoardStack())-> ElementCutsaw:
        try:
            iteration_board = other_boards.pop()
        except IndexError:
            return ElementCutsaw(board)

        el_cutsaw = ElementCutsaw(board)

        for i in range(iteration_board.amount + 1):
            if len(board) >= len(current_stack) + i * iteration_board.len:
                good_stack = current_stack + StackElement(iteration_board.board, i)
                el_cutsaw.append(good_stack)
                el_cutsaw += self.combinate(board, other_boards, good_stack)

        other_boards.append(iteration_board)
        return el_cutsaw
