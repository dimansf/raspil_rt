
import os
import time
from pathlib import Path


def multiply_files(path: str, base: str):
    for x in range(10):
        time.sleep(10)
        with open(os.path.join(path, f'{base}_{x}'), 'w') as f:
            f.write(f'done{x}')


def main():
    from multiprocessing import Process

    p1 = Process(target=multiply_files, args=(
        str(Path(__file__).parent.joinpath('temp')), 'f1'))
    p2 = Process(target=multiply_files, args=(
        str(Path(__file__).parent.joinpath('temp')), 'f2'))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


class Student:
    def __init__(self, name, age, major):
        self.name = name
        self.age = age
        self.major = major
    def __len__(self):
        return self.age




def test():
    students = [Student('John', 88, None) for _ in range(100)]

    # for _ in range(10000):
    #     test1(students)

    for _ in range(10000):
        test2(students)


def test1(arrange: list[Student]):
    return sum([len(x) for x in arrange])


def test2(arrange: list[Student]):
    k = 0
    for s in arrange:
        k+=len(s) 
    return k

if __name__ == "__main__":
    test()