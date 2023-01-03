

from data_structs.board import BoardsWrapper
from copy import copy
from raspil_rt.data_structs.board import Board, BoardStack, Cutsaw, CutsawElement, BoardElement


class Program:
    """
        boards = [ [1, 100, 1, 10, 5, 30], 
                [1, 6000, 3, 10, 5, 1000]]
                [ [id, len, store_id, amount, min_rem, max_rem], ...] 
        priority_map = [[1,4], [2], [3], [5]]] - в каком порядке проводить поиск оптимальных 
        распилов
        optimize_map = {sclad_id : optimize_flag} - применять параметры оптимизации для склада
                        1- 5        true/false
    """

    def __init__(self, boards: list[list[int]], store_boards: list[list[int]],
                 optimize_map: dict[int, bool], priority_map: list[list[int]], width_saw: int = 4):
        self.src_boards = boards
        self.src_store_boards = store_boards
        self.boards = BoardStack(
            [(Board(*x), x[3]) for x in boards if x[3] > 0])
        self.store_boards = BoardStack(
            [(Board(*x), x[3]) for x in store_boards if x[3] > 0])
        self.optimize_map = optimize_map
        self.priority_map = priority_map[::-1]

        self.width_saw = width_saw


        self.resulted_cutsaw: Cutsaw = Cutsaw()

    def main(self, test_round:int=-1):
        remain_iterations = 1000

        while(len(self.priority_map)):

            stores = self.priority_map.pop()
            if 4 - test_round ==  len(self.priority_map):
                break
            while(not self.iteration(stores)):
                if remain_iterations < 0:
                    raise Exception(
                        'Exceeded remain iteration limit: Over 10k iterations')
                else:
                    remain_iterations -= 1

    def iteration(self, sclad_id: list[int]) -> bool:
        """
        возвращаем положительное значение если добавлены новые распилы
        при ложном значении не удалось найти оптимальный распил
        """
        # разбить доски на группы по ид

        boards, s_boards = self.to_order_boards_by_id(sclad_id)

        sub_result = self.calculate_per_id(boards, s_boards)

        for cut_element in sub_result:
            self.store_boards -= BoardElement(cut_element.store_board, 1)
            self.boards -= cut_element[0]

        self.resulted_cutsaw += sub_result
        return len(sub_result)

    def to_order_boards_by_id(self, included_sclads: list[int] = []):
        boards_by_id:dict[int,BoardStack] = {}
        store_boards_by_id:dict[int,BoardStack] = {}
        ids = set([x.id for x in self.boards])
        for id in ids:
            boards_by_id[id] = BoardStack(
                [(x, self.boards[x]) for x in self.boards if x.id == id])
            store_boards_by_id[id] = BoardStack(
                [(x, self.store_boards[x]) for x in self.store_boards if x.id ==
                 id and x.sclad_id in included_sclads])
        return (boards_by_id, store_boards_by_id)

    def calculate_per_id(self, boards_by_id:dict[int,BoardStack],
                         store_boards_by_id:dict[int,BoardStack]) -> Cutsaw:
        """
         На данном этапе получаем лучший Cutsaw по одной доске от каждого Id
         {
             [board_with_id1: [BoardStack]] : 1,
             [board_with_id2: [BoardStack]] : 1,
             ...
         } 
        """
        results: Cutsaw = Cutsaw()
        for (board_id, boards) in boards_by_id.items():

            # 1. просчитать потенциально возможные комбинации
            boards_cutsaw = self.calculate_per_boards(
                boards, store_boards_by_id[board_id])

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

        res = Cutsaw([(self.combinate(BoardsWrapper(boards),
            store_board ), 1) for store_board in store_boards])

        return res

    def combinate(self,  boards: BoardsWrapper, store_board: Board,
                  current_stack: BoardStack = BoardStack(), input:bool=True) -> CutsawElement:
        try:
            iteration_board, amount = boards.pop()
        except IndexError:
            return CutsawElement(store_board)

        el_cutsaw:CutsawElement = CutsawElement(store_board)

        for i in range(amount + 1):
            remain = self.cutsaw_condition(current_stack, iteration_board, i, store_board)
            if remain >= 0:

                good_stack = copy(current_stack) + \
                    (iteration_board, i)
                good_stack.remain = remain
                el_cutsaw.append(good_stack)

                el_cutsaw += self.combinate(boards, store_board, good_stack, False)
        

        boards.append()
        return el_cutsaw

    def cutsaw_condition(self, current_stack:BoardStack, board:Board, amount:int, store_board:Board):
        total_saw_width = (current_stack.amount + amount) * self.width_saw
        total_len = current_stack.total_len + amount * board.len +  total_saw_width
        remain = store_board.len + self.width_saw - total_len
        if remain > store_board.len + self.width_saw:
            raise Exception('remain error')
        # 1. фаза проверки на возможность распила
        if remain >= 0:
            # 2. фаза проверки на условие ликвидности
            if  self.optimize_map[board.sclad_id]:
                if store_board.min_remain >= remain or \
                board.max_remain <= remain:
                    return remain
                else:
                    return -1
            else:
                return remain
        return -1      
        
                    
        
            
        