from raspil_rt.data_structs.StoreBoard import StoreBoard, StoreBoardCollection
from typing import List, Dict, NamedTuple
from .data_structs.Board import Board, BoardCollection, BoardCombinations


class Program:
    def __init__(self, boards, store_boards, optimize=True, sclad_max=True, width_saw=4):
        self.boards = BoardCollection([Board(*x) for x in boards])
        self.store_boards = StoreBoardCollection(
            [StoreBoard(*x) for x in store_boards])
        self.optimize = optimize
        self.sclad_max = sclad_max
        self.width_saw = width_saw
        self.current_id = 0
        self.ids = set([x.id for x in self.boards])
        self.map_lmeasures = None
        self.sclad_map = {'longs': (3, 4, 5), 'shorts': (1, 2)}
        self.calc_map_longmeasures()
        self.raspile_map = None

    def main(self):
        while(self.iteration(self.sclad_map['shorts']
                             if self.sclad_max else self.sclad_map['longs']) != 0):
            pass
        while(self.iteration(self.sclad_map['shorts'] + self.sclad_map['longs']) != 0):
            pass

    def iteration(self, sclad_id=[]) -> int:
        pass

    def calc_map_longmeasures(self):
        res = dict()
        lngms = [x for x in self.store_boards if lambda x: x.sclad_id == 5]
        for x in lngms:
            res[x.id] = x.len
        self.map_lmeasures = res

    def select_optimal_combination(self, cmb: Dict[StoreBoard, StoreBoardCollection]):
        for board in cmb.keys():
            pass

    def liquid_condition(self, bc: BoardCombinations):
        sb = bc.store_board
        try:
            current_lmeasure = self.map_lmeasures[self.current_id]
        except:
            current_lmeasure = 6000
        for ic in range(len(bc)):
            fl = False
            cc = bc[ic]
            cr = sb.len - len(cc)
            lower = current_lmeasure * sb.remain_per * 0.01
            final_len = cr - cc.total_amount() * self.width_saw
            # условие если распил не умещается в одну доску
            if cc.total_amount() == 1 and len(cc)*2 > current_lmeasure:
                fl = True
            fl = fl or (final_len >= -self.width_saw
                        and (lower >= final_len or sb.min_len <= final_len))
            if not fl:
                del bc[ic]

    def thinning(self, res: List[BoardCombinations]):
        for bc in res:
            self.liquid_condition(bc)

    def calc_per_id(self, sclad_ids=[]) -> Dict[int, List[BoardCombinations]]:

        results = dict()
        for id in self.ids:
            self.current_id = id
            brds = BoardCollection(
                [x for x in self.boards if lambda x: x.id == id])
            sbrds = StoreBoardCollection(
                [x for x in self.store_boards if lambda x: x.id == id and x.sclad_id in sclad_ids])

            results[id] = self.calc_per_board(brds, sbrds)

        return results

    def calc_per_board(self, boards: BoardCollection, store_boards: StoreBoardCollection) -> List[BoardCombinations]:
        '''
        Основная функция расчета на уровне без айдишников по одной доске склада
        '''
        res:List[BoardCombinations] = []
        for bs in store_boards:
            #  получены все комбинации по простому условию
            res.append(self.form_combinations(
                BoardCollection(), 0, boards, bs))

        if self.optimize:
            self.thinning(res)
        return res

    # def calc(self, boards:BoardCollection, store_board:StoreBoard) ->BoardCombinations:

    #     return self.form_combinations(BoardCollection(), 0, boards, store_board)

    def form_combinations(self, current_collection: BoardCollection, index: int, boards: BoardCollection, store_board: StoreBoard) -> BoardCombinations:
        '''
        Просчет комбинаций через рекурсивный перебор с условием на превышение длины summ(boards) < boards_len
        '''
        try:
            board: Board = boards[index]
        except:
            return BoardCombinations(store_board)

        a = BoardCombinations(store_board)
        for i in range(0, board.amount+1):
            if store_board.len >= board.len * i + len(current_collection):
                cs = BoardCollection.copy(current_collection)
                if i != 0:
                    cs.append(Board.copy(board, i))
                    a.append(cs)
                res = self.form_combinations(cs, index+1, boards, store_board)
                if len(res) != 0:
                    a += res
        return a
