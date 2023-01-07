from raspil_rt.data_structs.board import Board, BoardStack, Cutsaw, CutsawElement, BoardsWrapper
from multiprocessing import  cpu_count

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
                 optimize_map: dict[int, bool], priority_map: list[list[int]], width_saw: int = 4):
        self.src_boards = boards
        self.src_store_boards = store_boards
        self.boards = BoardStack(
            [(Board(*x), x[3]) for x in boards if x[3] > 0])
        self.store_boards: BoardStack = BoardStack(
            [(Board(*x), x[3]) for x in store_boards if x[3] > 0])
        self.optimize_map = optimize_map
        self.priority_map = priority_map
        self.num_proc=  cpu_count()
        self.width_saw = width_saw

        self.resulted_cutsaw = Cutsaw()

    def main(self, test_round: int = 5):

        for stores in self.priority_map:
            self.iteration(stores)

            test_round -= 1
            if not test_round:
                break

    def iteration(self, sclad_id: list[int]):
        """
        возвращаем положительное значение если добавлены новые распилы
        при ложном значении не удалось найти оптимальный распил
        """
        # разбить доски на группы по ид

        boards, s_boards = self.to_order_boards_by_id(sclad_id)
        self.current_sclad_id = sclad_id

        sub_result = self.calculate_per_id(boards, s_boards)

        self.resulted_cutsaw += sub_result
        return

    def calculate_per_id(self, boards_by_id: dict[int, BoardStack],
                         store_boards_by_id: dict[int, BoardStack]) -> Cutsaw:
        """
         На данном этапе получаем лучший Cutsaw по одной доске от каждого Id
         {
             [board_with_id1: [BoardStack]] : 1,
             [board_with_id2: [BoardStack]] : 1,
             ...
         } 
        """
        results = Cutsaw()
        for (board_id, boards) in boards_by_id.items():

            # 1. просчитать потенциально возможные комбинации
            results  += self.calculate_per_boards(
                boards, store_boards_by_id[board_id])
        return self.select_and_subtract(results)

    def select_and_subtract(self, boards_cutsaw:Cutsaw):
            # 2. выделить лучший распил и произвести вычитание
        results = Cutsaw()
        
        while (True):
            res = boards_cutsaw.get_best_cutsaw_elements(
                self.boards, self.store_boards)
            if res:
                self.boards -= res[0]
                self.store_boards -= (res.store_board, 1) 
                results += res
                
            else:
                break
        return results

    def calculate_per_boards(self, boards: BoardStack, store_boards: BoardStack) -> Cutsaw:
        '''
        Калькуляция для каждой палки из store_board
        - есть возможность распараллелить
        '''

        from multiprocessing.pool import Pool
        with Pool(processes=self.num_proc) as pool:
            input_vals = [(self, BoardsWrapper(boards), store_board)
                          for store_board in store_boards]
            results = pool.starmap(Program.combinate, input_vals)

        res = Cutsaw([(res, 1) for res in results if len(res)>0])

        return res

    def combinate(self,  boards: BoardsWrapper, store_board: Board,
                  current_stack: BoardStack = BoardStack()) -> CutsawElement:
        try:
            iteration_board, amount = boards.pop()
        except IndexError:
            return CutsawElement(store_board)

        el_cutsaw = CutsawElement(store_board)

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
                    el_cutsaw.append(good_stack)

                el_cutsaw += self.combinate(boards, store_board, good_stack)

        boards.shift()
        return el_cutsaw

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

    def to_order_boards_by_id(self, included_sclads: list[int] = []):
        boards_by_id: dict[int, BoardStack] = {}
        store_boards_by_id: dict[int, BoardStack] = {}
        ids = set([x.num_id  for x in self.boards])
        for id in ids:
            boards_by_id[id] = BoardStack(
                [(x, self.boards[x]) for x in self.boards if x.num_id == id])
            store_boards_by_id[id] = BoardStack(
                [(x, self.store_boards[x]) for x in self.store_boards if x.num_id ==
                 id and x.sclad_id in included_sclads])
        return (boards_by_id, store_boards_by_id)


class RemainError(Exception):
    pass
