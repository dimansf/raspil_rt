from typing import Callable
from raspil_rt.data_structs.board import Board, BoardStack, Cutsaw, CutsawElement, BoardsWrapper, BoardStackSet
from multiprocessing import cpu_count
from multiprocessing.pool import Pool

class Program:
    """
        boards - доски в заказе
        store_boards  - доски со складов на распил
        [ 
            [id, len, store_id, amount, min_rem, max_rem],
        ] 
        priority_map - порядок обхода складов по номерам
        [
            [1,4], [2], [3], [5]],
        ]
        optimize_map -параметры оптимизации по номерам складов
        {
            sclad_id : optimize_flag
        } 
            1 - 5        true/false
        widht_saw - толщина пила в мм
            4
    """

    def __init__(self, boards: list[list[int]], store_boards: list[list[int]],
                 optimize_map: dict[int, bool], priority_map: list[list[int]], 
                 width_saw: int = 4, best_elements_arrray_size:int =2):
        self.src_boards = boards
        self.src_store_boards = store_boards
        bs1 = BoardStackSet(
            [(Board(*x), x[3]) for x in boards if x[3] > 0]).res
        self.boards = BoardStack(bs1)
        bs2 = BoardStackSet(
            [(Board(*x), x[3]) for x in store_boards if x[3] > 0]).res
        self.store_boards: BoardStack = BoardStack(bs2)
        self.optimize_map = optimize_map
        self.priority_map = priority_map
        self.num_proc = cpu_count()
        self.width_saw = width_saw
        self.on_reaction:Callable[[Cutsaw], None]| None = None
        CutsawElement.array_size = best_elements_arrray_size

        self.resulted_cutsaw = Cutsaw()
    def setCallcaback(self, f:Callable[[Cutsaw], None]):
        self.on_reaction = f
    def main(self, test_round: int = 6):

        for stores in self.priority_map:
            self.iteration(stores)

            test_round -= 1
            if not test_round:
                break

    def iteration(self, sclads_id: list[int]):
        """
        возвращаем положительное значение если добавлены новые распилы
        при ложном значении не удалось найти оптимальный распил
        """
        ids  = list( set([el.num_id for el in self.boards]))        

        boards_by_id = dict([ (_id, self.boards.filter(_id) )for _id in ids])
        store_boards_by_id = dict([(_id, self.store_boards.filter(_id, sclads_id)) for _id in ids])
            
        
        for _id in boards_by_id:
            res = self.calculate(boards_by_id[_id],store_boards_by_id[_id], sclads_id  ,_id)
            if self.on_reaction:
                self.on_reaction(res)
            self.resulted_cutsaw += res
                
                
        return

    def calculate(self, boards:BoardStack, store_boards:BoardStack, sclad_id: list[int], _id:int):
        """

        """
        
        results = Cutsaw()
        
        
        while True:
            
            calcs = self.calculate_per_boards(
                boards, store_boards)
            res = self.select_and_subtract(calcs)
            boards = self.boards.filter(_id)
            store_boards = self.store_boards.filter(_id,sclad_id)
            if len(res):
                results += res
            else:
                break

        return results

    def select_and_subtract(self, boards_cutsaw: Cutsaw):
        # 2. выделить лучший распил и произвести вычитание
        results = Cutsaw()

        while (True):
            
            res = boards_cutsaw.get_best_cutsaw_elements(
               self.boards, self.store_boards)
            if res and res.last_best:
                self.boards -= res.last_best
                self.store_boards -= (res.store_board,1)
                results += res
            else:
                break
        return results

    def calculate_per_boards(self, boards: BoardStack, store_boards: BoardStack) -> Cutsaw:
        '''
        Калькуляция N лучших вариантов распила заказов для каждой доски со склада
        '''       
        with Pool(processes=self.num_proc) as pool:
            input_vals = [(self, BoardsWrapper(boards), store_board, CutsawElement(store_board))
                          for store_board in store_boards]
            results = pool.starmap(Program.combinate, input_vals)

        res = Cutsaw([(res, 1) for res in results if len(res) > 0])

        return res

    def combinate(self,  boards: BoardsWrapper, store_board: Board,
                  current_best: CutsawElement, current_stack: BoardStack = BoardStack()):
        try:
            iteration_board, amount = boards.pop()
        except IndexError:
            return current_best

        for i in range(amount + 1):
            remain = self.cutsaw_condition(
                current_stack, iteration_board, i, store_board)
            if remain == -2:
                break
            if remain >= 0:
                good_stack = current_stack
                if i > 0:
                    good_stack = current_stack + (iteration_board, i)
                    good_stack.remain = remain

                    current_best.add_best(good_stack)
                self.combinate(boards, store_board,  current_best, good_stack)

        boards.shift()
        return current_best

    def cutsaw_condition(self, current_stack: BoardStack, board: Board, amount: int, store_board: Board):
        # 1. фаза проверки на возможность распила
        total_saw_width = (current_stack.amount + amount) * self.width_saw
        total_len = current_stack.total_len + amount * board.len + total_saw_width
        remain = store_board.len + self.width_saw - total_len

        if remain > store_board.len + self.width_saw:
            raise RemainError()
        if remain < 0:
            return -2
        # 2. фаза проверки на условие ликвидности
        if self.optimize_map[store_board.sclad_id]:
            if store_board.min_remain >= remain or \
                    store_board.max_remain <= remain:
                return remain
            else:
                return -1
        else:
            return remain

 


class RemainError(Exception):
    pass
