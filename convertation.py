# type:ignore
'''
    Перед тем как отдать данные с json их нужно подготовить для программы обработки
    после обработки их нужно также преобразовать обратно 
'''



from time import perf_counter
from pathlib import Path

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

def load_simple_config(file:str) -> dict[str,str]:
    d = {}
    with open(file) as c:
        lines =  [list(map(lambda x: x.strip(), line.split('='))) for line in c.readlines()]
        [d.setdefault(l[0], l[1]) for l in lines]
    return d

class TimeCounter(dict[str, list[float]]):
    def __init__(self, path:Path) -> None:
        self.path = path
        self.inner_pair_counter:dict[str, int] = {}
   
    def print(self):
        self.print(str(self))
    
    def write(self):
        
        with open(str(self.path), 'a') as f:
            f.write(f'\n{self}')
                
    def __str__(self) -> str:
        return '{' + ',\n'.join([f'"{k }": {self[k]}' for k in self]) + '}'

        
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
    @staticmethod
    def try_mark(name:str):
        
        def f(f):
            def ff(*args):
                self = args[0]
                if.self.t:
                    self.t.mark('name')
                    res = f(*args)
                    self.t.mark('name')
                else:
                    res =  f(*args)
                return res
            return ff
        return f

            
from typing import Callable



timer = TimeCounter('')

def perform_marking(f:Callable[[str, str], str]):
    # Внутри себя декоратор определяет функцию-"обёртку". Она будет обёрнута вокруг декорируемой,
    # получая возможность исполнять произвольный код до и после неё.
    def the_wrapper_around_the_original_function():
        timer.mark()
        function_to_decorate() # Сама функция
        print("А я - код, срабатывающий после")
    # Вернём эту функцию
    return the_wrapper_around_the_original_function

import time

def timeit(func): 
    def timed(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        te = time.time()
        print('Function', func.__name__, 'time:', round((te -ts)*1000,1), 'ms')
        print()
        return result
    return timed

# @timeit
# def math_harder():
#     [x**(x%17)^x%17 for x in range(1,5555)]
# math_harder()

# @timeit
# def sleeper_agent():
#     time.sleep(1)
# sleeper_agent()