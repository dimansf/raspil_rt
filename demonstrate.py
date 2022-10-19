import os
import time
from pathlib import Path
def multiply_files(path:str, base:str):
    for x in range(10):
        time.sleep(10)
        with open(os.path.join(path, f'{base}_{x}'), 'w') as f:
            f.write(f'done{x}')


def main():
    from multiprocessing import Process


    p1 = Process(target=multiply_files, args=(str(Path(__file__).parent.joinpath('temp')), 'f1'))
    p2 = Process(target=multiply_files, args=(str(Path(__file__).parent.joinpath('temp')), 'f2'))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__== "__main__":
    main()