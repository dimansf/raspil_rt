from raspil_rt.data_structs.StoreBoard import StoreBoard, StoreBoardCollection
from typing import List, Dict, NamedTuple, Union
from .data_structs.Board import Board, BoardCollection, BoardCombinations, MapResult


class Program:
    def __init__(self, boards, store_boards, optimize=True, sclad_max=True, width_saw=4):
        self.boards = BoardCollection([Board(*x) for x in boards])
        self.store_boards = StoreBoardCollection(
            [StoreBoard(*x) for x in store_boards])
        self.optimize = optimize
        self.sclad_max = sclad_max
        self.width_saw = width_saw

        self.ids = set([x.id for x in self.boards])

        self.sclad_map = {
            'longs': (3, 4, 5),
            'shorts': (1, 2)
        }
        self.calc_map_longmeasures()
        self.map_result = MapResult()

    def main(self):
        counter = 0
        while(not self.iteration(self.sclad_map['shorts']
                                 if self.sclad_max else self.sclad_map['longs'])):
            if counter > 1000:
                break
            counter += 1
        while(not self.iteration(self.sclad_map['shorts'] + self.sclad_map['longs'])):
            if counter > 1000:
                break
            counter += 1
        self.optimize = False
        while(not self.iteration(self.sclad_map['shorts'] + self.sclad_map['longs'])):
            if counter > 1000:
                break
            counter += 1

    def iteration(self, sclad_id=[]) -> bool:
        map_r = self.calc_per_id(sclad_id)
        self.iteration_subtraction(map_r)
        self.map_result += map_r
        return map_r.is_empty()

    def iteration_subtraction(self, mr: MapResult):
        for m in mr.values():
            for d in m.keys():
                self.boards -= d[0]
                self.store_boards -= StoreBoardCollection([d.store_board])

    def calc_map_longmeasures(self):
        res = dict()
        #  процент нижней границы высчитывается из максимальной палки с 5 склада
        lngms = [x for x in self.store_boards if x.sclad_id == 5]
        for x in lngms:
            res[x.id] = x.len if res.get(x.id, 0) < x.len else res[x.id]
        self.map_lmeasures = res

    def optimize_selection(self, res: List[BoardCombinations]) -> Dict[BoardCombinations, int]:
        bests: List[BoardCombinations] = []
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

    def calc_per_id(self, sclad_ids=[]) -> MapResult:
        results = MapResult()
        for id in self.ids:
            brds = BoardCollection(
                [x for x in self.boards if x.id == id])
            sbrds = StoreBoardCollection(
                [x for x in self.store_boards if x.id == id and x.sclad_id in sclad_ids])

            res = self.optimize_selection(
                self.calc_per_boards(brds, sbrds))
            if sum([len(x[0]) for x in res.keys()]) != 0:
                results[id] = res  # type:ignore

        return results

    def calc_per_boards(self, boards: BoardCollection, store_boards: StoreBoardCollection):
        '''
        Палка и ее возможный список распилов
        '''
        res: List[BoardCombinations] = []
        for bs in store_boards:
            #  получены все комбинации по простому условию
            res.append(self.form_combinations(
                BoardCollection(), 0, boards, bs))
        return res

    def can_to_saw(self, coll: BoardCollection, b: Board, i: int, bs: StoreBoard):
        ttl = coll.len + coll.amount * self.width_saw + b.len * i + i * self.width_saw
        if bs.len - ttl >= - self.width_saw:
            return True
        return False

    def form_combinations(self, current_collection: BoardCollection,
                          index: int, boards: BoardCollection, store_board: StoreBoard) -> BoardCombinations:
        '''
        Просчет комбинаций через рекурсивный перебор с условием на превышение длины summ(boards) < boards_len
        '''
        try:
            board: Board = boards[index]
        except:
            return BoardCombinations(store_board)

        a = BoardCombinations(store_board)
        for i in range(0, board.amount+1):
            if self.can_to_saw(current_collection, board, i, store_board):
                cs = BoardCollection.copy(
                    current_collection) if i != 0 else current_collection
                if i != 0:
                    cs.append(Board.copy(board, i))
                    a.append(cs)
                res = self.form_combinations(cs, index+1, boards, store_board)
                if len(res) != 0:
                    a += res
        return a
