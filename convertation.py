'''
    Перед тем как отдать данные с json их нужно подготовить для программы обработки
    после обработки их нужно также преобразовать обратно 
'''



from time import perf_counter


def convertation_for_program(boards:list[list[int]], store_boards:list[list[int]], 
optimize:dict[str, bool]):
    '''
    Изначально store_boards
        [ ид / длина / количество / максимальный остаток / минимальный остаток / склад_ид ]
    Вывод
        [ ид / длина /  склад_ид  / количество  / минимальный остаток / максимальный остаток]
    Изначально boards
        [ ид / длина / количество]
    Вывод
        [ ид / длина /  склад_ид  / количество  / минимальный остаток / максимальный остаток]
    '''
    
    _boards: list[list[int]] = []
    _store_boards: list[list[int]] = []
    _optimize:dict[int, bool] = {}

    _boards = [[x[0], x[1], 0, x[2], 0, 0] for x in boards]
    _store_boards = [[x[0], x[1], x[5], x[2], x[4], x[3]] for x in store_boards]
    [_optimize.setdefault(int(k), optimize[k]) for k in optimize]
    
    return (_boards, _store_boards, _optimize)



class TimeCounter(dict[str, list[float]]):
    def __init__(self, path:str) -> None:
        self.path = path
        self.inner_pair_counter:dict[str, int] = {}
   
    def print(self, s:str):
        with open(self.path, 'w') as f:
            f.write(s)
    
        
    
    def mark(self, name:str, flag:str=''):
        if self.inner_pair_counter.get(name, None) is None or\
            self.inner_pair_counter[name] % 2 == 0 :
            def operate():
                self[name].append( perf_counter())
                self.inner_pair_counter[name] = 1
            try:
                operate()
            except:
                self[name] = []
                operate()
        else:
            self[name].append(perf_counter() - self[name].pop())
            self.inner_pair_counter[name] = 2
            if flag == 'sum':
                s = sum(self[name])
                self[name].clear()
                self[name].append(s)

            
