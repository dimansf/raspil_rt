
from queue import Queue
from typing import List, Dict
from cached_property import cached_property
from raspil_rt.data_structs.board import Board, BoardStack, Cutsaw, ElementCutsaw, StackElement


class Program:
    """
        boards = [ [1, 100, 1, 10, 5, 30], [1, 6000, 3, 10, 5, 1000]]
                 [ [id, len, store_id, amount, min_rem, max_rem], ...] 
        priority_map = [[1,4], [2], [3], [5]]] - в каком порядке проводить поиск оптимальных 
        распилов
        optimize_map = {sclad_id : optimize_flag} - применять параметры оптимизации для склада
                        1- 5        true/false
    """

    def __init__(self, boards: List[List[int]], store_boards: List[List[int]],
                 optimize_map: dict[int, bool], priority_map: Queue[list[int]], width_saw: int = 4):
        self.src_boards = boards
        self.src_store_boards = store_boards
        self.boards = BoardStack(
            [StackElement(Board(x[0], x[1], -1), x[3]) for x in boards if x[3] > 0])
        self.store_boards = BoardStack(
            [StackElement(Board(x[0], x[1], x[2]), x[3]) for x in store_boards if x[3] > 0])
        self.optimize_map = optimize_map
        self.priority_map = priority_map
        self.width_saw = width_saw

        self.boards_by_id: Dict[int, BoardStack] = {}
        self.store_boards_by_id: Dict[int, BoardStack] = {}

        self.map_result = []


    def main(self):
        while(not self.priority_map.empty()):
            stores = self.priority_map.get_nowait()
            self.iteration(stores)

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

    def iteration(self, sclad_id: list[int] = []) -> int:
        """
        возвращаем кол-во добавленых новых распилов
        при нулевом значении не удалось найти оптимальный распил
        """
        # разбить на группы по ид
        self._to_order_boards_by_id(sclad_id)

        self.iteration_subtraction(map_r)
        self.map_result += map_r
        return map_r.is_empty()

    def _to_order_boards_by_id(self, included_sclads: list[int] = []):
        ids = set([x.id for x in self.boards])
        for id in ids:
            self.boards_by_id[id] = BoardStack(
                [x for x in self.boards if x.id == id])
            self.store_boards_by_id[id] = BoardStack([x for x in self.store_boards if x.id ==
                                                      id and x.sclad_id in included_sclads])

    def iteration_subtraction(self, mr):
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

    def optimize_selection(self, res):
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
    # на данном этапе должны выйти элементы распила с лучшей комбинацией
    # [ ElementCutsaw.len == 1, ... ]

    def calculate_per_id(self) -> Cutsaw:
        results:list[Cutsaw] = []
        for (board_id, boards) in self.boards_by_id.items():

            # 1. просчитать потенциально возможные комбинации
            res = self.calculate_per_boards(
                boards, self.store_boards_by_id[board_id])
            # 2. отсеять неподходящие распилы
            res.select_best_stack_board(self.optimize_map, self.width_saw)
        
        return results
    
        
   

    def calculate_per_boards(self, boards: BoardStack, store_boards: BoardStack):
        '''
        Палки и их возможные комбинации распилов
        '''
        return Cutsaw([(self.combinate(
                board.board, boards),1) for board in store_boards])

    def combinate(self,  board: Board, other_boards: BoardStack, current_stack: BoardStack = BoardStack()) -> ElementCutsaw:
        try:
            iteration_board = other_boards.pop()
        except IndexError:
            return ElementCutsaw(board)

        el_cutsaw = ElementCutsaw(board)

        for i in range(iteration_board.amount + 1):
            if len(board) >= len(current_stack) + i * iteration_board.len:
                good_stack = current_stack + \
                    StackElement(iteration_board.board, i)
                el_cutsaw.append(good_stack)
                el_cutsaw += self.combinate(board, other_boards, good_stack)

        other_boards.append(iteration_board)
        return el_cutsaw
