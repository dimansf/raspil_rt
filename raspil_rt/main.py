# from raspil_rt.data_structs.StoreBoard import StoreBoard, StoreBoardCollection
from typing import Iterable, List, Dict, NamedTuple, Union

from raspil_rt.data_structs.stack_element import BoardStack, StackElement
# from .data_structs.boards import Board, BoardCollection, BoardCombinations, MapResult
from .data_structs.boards import Board, BoardDict, _MapCombinations, DictCombinations



def main(self, boards: Iterable[Iterable[int]], storeBoards: Iterable[Iterable[int]],
                optimize=True, sclad_max=True, width_saw=4):
    """
    optimize - использовать как можно больше досок без учета оптимальности распила
    width_saw - толщина пилы при отпиле досок в мм
    sclad_max - пилить все что есть на складе только потом брать из заказанных
    """
    self.boards = BoardStack(
        [ StackElement(Board(x[0], x[1]), x[2]) for x in boards], boards)
    self.storeBoards = BoardStack(
        [StackElement(Board(x[0], x[1],  x[3]), x[2]) for x in storeBoards],storeBoards)
    self.optimize = optimize
    self.sclad_max = sclad_max
    self.width_saw = width_saw

    self.ids = set([x.id for x in self.boards.keys()])

    self.sclad_map = {
        'longs': (3, 4, 5),
        'shorts': (1, 2)
    }
    
    # self.calc_map_longmeasures()
    self.map_result = _MapCombinations()

    # def main(self):
    #     counter = 0
    #     while(not self.iteration(self.sclad_map['shorts']
    #                              if self.sclad_max else self.sclad_map['longs'])):
    #         if counter > 1000:
    #             break
    #         counter += 1
    #     while(not self.iteration(self.sclad_map['shorts'] + self.sclad_map['longs'])):
    #         if counter > 1000:
    #             break
    #         counter += 1
    #     self.optimize = False
    #     while(not self.iteration(self.sclad_map['shorts'] + self.sclad_map['longs'])):
    #         if counter > 1000:
    #             break
    #         counter += 1

    # def iteration(self, sclad_id=[]) -> bool:
    #     map_r = self.calc_per_id(sclad_id)
    #     self.iteration_subtraction(map_r)
    #     self.map_result += map_r
    #     return map_r.is_empty()

    # def iteration_subtraction(self, mr: MapResult):
    #     for m in mr.values():
    #         for d in m.keys():
    #             self.boards -= d[0]
    #             self.storeBoards -= StoreBoardCollection([d.storeBoard])

    # def calc_map_longmeasures(self):
    #     res = dict()
    #     #  процент нижней границы высчитывается из максимальной палки с 5 склада
    #     lngms = [x for x in self.storeBoards if x.sclad_id == 5]
    #     for x in lngms:
    #         res[x.id] = x.len if res.get(x.id, 0) < x.len else res[x.id]
    #     self.map_lmeasures = res

    # def optimize_selection(self, res: List[BoardCombinations]) -> Dict[BoardCombinations, int]:
    #     bests: List[BoardCombinations] = []
    #     for bc in res:
    #         bests.append(bc.calc_best_combination(self.optimize,
    #                                               self.map_lmeasures[bc.storeBoard.id],
    #                                               self.width_saw,
    #                                               self.sclad_map['longs']))
    #     try:
    #         best = bests.pop()
    #     except:
    #         return {}
    #     for bb in bests:
    #         if best.payload < bb.payload:
    #             best = bb
    #     return {best: 1}

    # def calc_per_id(self, sclad_ids=[]) -> _MapCombinations:
    #     results = _MapCombinations()
    #     for id in self.ids:
    #         brds = BoardCollection(
    #             [x for x in self.boards if x.id == id])
    #         sbrds = StoreBoardCollection(
    #             [x for x in self.storeBoards if x.id == id and x.sclad_id in sclad_ids])

    #         res = self.optimize_selection(
    #             self.calc_perBoards(brds, sbrds))
    #         if sum([len(x[0]) for x in res.keys()]) != 0:
    #             results[id] = res  # type:ignore

    #     return results

def calculate_perBoards(self, boards: BoardDict, storeBoards: BoardDict) -> DictCombinations:
    '''
    Палка и ее возможный список распилов
    '''
    res = DictCombinations()
    for bs in storeBoards:
        res[bs] = self._combinate(BoardDict(),  boards, bs)
    return res

def can_to_saw(self, coll: BoardDict, b: Board, i: int, bs: Board):
    ttl = coll.length + coll.amount * self.width_saw + b.len * i + i * self.width_saw
    if bs.len - ttl >= - self.width_saw and i != 0:
        return True
    return False

def _combinate(self, current_collection: BoardDict, boards: BoardDict, storeBoard: Board) -> List[BoardDict]:
    try:
        currentBoard, amount = boards.popitem() # popitem выдает пары в LIFO порядке
    except KeyError:
        return []
    res = []
    overf = 0
    for i in range(amount+1):
        cc = current_collection.copy()
        if  self.can_to_saw(cc, currentBoard, i, storeBoard):
            cc[currentBoard] = i
            res.append(cc)
        else: overf += 1
        if overf == 2: break
        res += self._combinate(cc, boards, storeBoard)  
    boards[currentBoard] = amount  
    return res    

    # def form_combinations(self, current_collection: BoardDict,
    #                       index: int, boards: BoardDict, storeBoard: Board) -> BoardCombination:
    #     '''
    #     Просчет комбинаций через рекурсивный перебор с условием на превышение длины summ(boards) < boards_len
    #     '''
    #     try:
    #         board = boards[index]
    #     except:
    #         return BoardCombination(storeBoard)

    #     a = BoardCombinations(storeBoard)
    #     for i in range(0, board.amount+1):
    #         if self.can_to_saw(current_collection, board, i, storeBoard):
    #             cs = BoardCollection.copy(
    #                 current_collection) if i != 0 else current_collection
    #             if i != 0:
    #                 cs.append(Board.copy(board, i))
    #                 a.append(cs)
    #             res = self.form_combinations(cs, index+1, boards, storeBoard)
    #             if len(res) != 0:
    #                 a += res
    #     return a
