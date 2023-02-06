from copy import copy
from socket import socket

from raspil_rt.data_structs.board import CutsawList
from raspil_rt.data_structs.board import Board, BoardStack, Cutsaw, CutsawElement, BoardsWrapper, BoardStackSet
from multiprocessing import cpu_count
from multiprocessing.pool import Pool
from raspil_rt.convertation import TimeCounter
from pathlib import Path
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
                 priority_map: dict[int,dict[int,bool]],
                 width_saw: int = 4,threshold:int=0, time_metric:bool=False,
                 log_path:Path=Path.home(), log_name:str='raspil_rt_log.json'):
        self.src_boards = boards
        self.src_store_boards = store_boards
        bs1 = BoardStackSet(
            [(Board(*x), x[3]) for x in boards if x[3] > 0]).res
        self.boards = BoardStack(bs1)
        bs2 = BoardStackSet(
            [(Board(*x), x[3]) for x in store_boards if x[3] > 0]).res
        self.store_boards: BoardStack = BoardStack(bs2)
        self.threshold = threshold
        self.priority_map = priority_map
        self.num_proc = cpu_count()
        self.width_saw = width_saw
        self.on_reaction: socket | None = None
        self.test_round = 0
        
        self.t:TimeCounter | None =  TimeCounter(log_path.joinpath(log_name)) if time_metric else None
       
        self.resulted_cutsaw = Cutsaw()

    def setCallcaback(self, conn:socket):
        
            
        self.on_reaction = conn

    def main(self, stop_on_round: int = 0):

        for round_num in self.priority_map:
            self.test_round = round_num
            self.iteration([x for x in self.priority_map[round_num]])

            if stop_on_round == self.test_round:
                break

    def iteration(self, sclads_id: list[int]):
        """
        возвращаем положительное значение если добавлены новые распилы
        при ложном значении не удалось найти оптимальный распил
        """
        ids = list(set([el.num_id for el in self.boards]))

        for _id in ids:
            
            res = self.calculate(sclads_id, _id)
            if self.on_reaction:
                self.on_reaction.sendall(str(res).encode())
                
            self.resulted_cutsaw += res

        return
    
    def calculate(self, sclad_id: list[int], _id: int):
        """
            Просчет заказов по каждой доске на складе
            Отбор оптимальной и формирование распила
        """

        results = Cutsaw()

        while True:
           
            calcs = self.calculate_per_boards(
                self.boards.filter(_id), self.store_boards.filter(_id, sclad_id))
            res = self.select_and_subtract(calcs)
            
            if self.on_reaction:
           
                self.on_reaction.sendall(str(res).encode())
            if len(res):
                results += res
            else:
                break

        return results

    def select_and_subtract(self, boards_cutsaw: CutsawList):
        # 2. выделить лучший распил и произвести вычитание
        results = Cutsaw()

        is_best = boards_cutsaw.get_best_cutsaw_elements(
            self.boards, self.store_boards)
       
        if is_best and is_best.last_best:
            while 1:
                if is_best.last_best in self.boards and\
                    (is_best.store_board, 1) in self.store_boards:

                    self.boards -= is_best.last_best
                    self.store_boards -= (is_best.store_board, 1)
                    results += copy(is_best)
                else:
                    break
            
    
        
        return results

    def calculate_per_boards(self, boards: BoardStack, store_boards: BoardStack):
        '''
        Калькуляция N лучших вариантов распила заказов для каждой доски со склада
        '''
        with Pool(processes=self.num_proc) as pool:
            input_vals = [(self, BoardsWrapper(boards), store_board, CutsawElement(store_board))
                          for store_board in store_boards]
            results = CutsawList(pool.starmap(Program.combinate, input_vals))

        return results

    def combinate(self,  boards: BoardsWrapper, store_board: Board,
                  current_best: CutsawElement, current_stack: BoardStack = BoardStack()):
        try:
            
            iteration_board, amount = boards.pop()
        except IndexError:
            return current_best
        try:
            if current_best[0].remain <= self.threshold:
                return current_best
        except:
            pass
        
        for i in range(amount + 1):
           
            remain = self.cutsaw_condition(
                current_stack, iteration_board, i, store_board)
            if remain == -2:
                break
            cs = (current_stack + (iteration_board, i)) if i > 0 else current_stack
            cs.remain = remain
           
            if remain >= 0:
                current_best.add_best(cs)
                
            self.combinate(boards, store_board,  current_best, cs)

        boards.shift()
        return current_best

    def cutsaw_condition(self, current_stack: BoardStack, board: Board, amount: int, store_board: Board):
        # 1. фаза проверки на возможность распила
        total_saw_width = (current_stack.amount + amount) * self.width_saw
        total_len = current_stack.total_len + amount * board.len + total_saw_width
        remain = store_board.len - total_len
        remain = 0 if 0 > remain >= -self.width_saw else remain

        if remain > store_board.len + self.width_saw:
            raise RemainError()
        if remain < 0:
            return -2
        # 2. фаза проверки на условие ликвидности
        if self.priority_map[self.test_round][store_board.sclad_id]:
            if store_board.min_remain >= remain or \
                    store_board.max_remain <= remain:
                return remain
            else:
                return -1
        else:
            return remain


class RemainError(Exception):
    pass
