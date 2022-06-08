
from queue import Queue
from typing import List, Dict
from data_structs.board import Board, BoardStack, Cutsaw, ElementCutsaw, StackElement


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
            [StackElement(Board(*x), x[3]) for x in boards if x[3] > 0])
        self.store_boards = BoardStack(
            [StackElement(Board(*x), x[3]) for x in store_boards if x[3] > 0])
        self.optimize_map = optimize_map
        self.priority_map = priority_map
        self.width_saw = width_saw

        self.boards_by_id: Dict[int, BoardStack] = {}
        self.store_boards_by_id: Dict[int, BoardStack] = {}

        self.resulted_cutsaw: Cutsaw = Cutsaw()

    def main(self):
        remain_iterations = 10000
        while(not self.priority_map.empty()):
            stores = self.priority_map.get_nowait()
            while(self.iteration(stores) != 0):
                if remain_iterations < 0:
                    raise Exception(
                        'Exceeded remain iteration limit: Over 10k iterations')
                else:
                    remain_iterations -= 1

    def iteration(self, sclad_id: list[int]) -> int:
        """
        возвращаем кол-во добавленых новых распилов
        при нулевом значении не удалось найти оптимальный распил
        """
        # разбить доски на группы по ид
        self._to_order_boards_by_id(sclad_id)
        sub_result = self.calculate_per_id()
        for cut_element in sub_result:
            self.store_boards -= cut_element.store_board
            self.boards -= cut_element[0]
        self.resulted_cutsaw += sub_result
        return len(sub_result)

    def _to_order_boards_by_id(self, included_sclads: list[int] = []):
        ids = set([x.id for x in self.boards])
        for id in ids:
            self.boards_by_id[id] = BoardStack(
                [x for x in self.boards if x.id == id])
            self.store_boards_by_id[id] = BoardStack(
                [x for x in self.store_boards if x.id ==
                 id and x.sclad_id in included_sclads])

    def calculate_per_id(self) -> Cutsaw:
        """
         На данном этапе получаем лучший Cutsaw по одной доске от каждого Id
         {
             [board_with_id1: [BoardStack]] : 1,
             [board_with_id2: [BoardStack]] : 1,
             ...
         } 
        """
        results: Cutsaw = Cutsaw()
        for (board_id, boards) in self.boards_by_id.items():

            # 1. просчитать потенциально возможные комбинации
            boards_cutsaw = self.calculate_per_boards(
                boards, self.store_boards_by_id[board_id])
            # 2. отсеять неподходящие распилы
            boards_cutsaw.thick_off_cutsaw_elements(
                self.optimize_map, self.width_saw)
            results += boards_cutsaw

        return results

    def calculate_per_boards(self, boards: BoardStack, store_boards: BoardStack) -> Cutsaw:
        '''
        Калькуляция палок и комбинаций под них
        для каждой палки из store_board
        '''
        return Cutsaw([(self.combinate(
            board.board, boards), 1) for board in store_boards])

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
