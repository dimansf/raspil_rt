# Модуль socketserver для сетевого программирования
from multiprocessing import Process, Pipe
from multiprocessing.connection import PipeConnection
import subprocess
import time


# def worker(name:str, ppe: PipeConnection):
#     for _ in range(10):
#         time.sleep(2)
#         ppe.send(f'{name}')
#     ppe.close()
    

# if __name__ == "__main__":
#     in1,out = Pipe()
#     in2, out2 = Pipe()
#     p1 = Process(target=worker, args=('bob', out))
#     p2 = Process(target=worker, args=('alice',out2))
#     p1.start()
#     p2.start()
#     while not in1.closed or not in2.closed:
#         if not in1.closed:
            
#             print(f'{in1.recv()}')
#         if not in2.closed:
#             print(f'{in2.recv()}')
#     p1.join()


def create_worker():
    from subprocess import run 
    from pathlib import Path
    from raspil_py.tests.main_test import  big_input
    in1 = open(big_input, 'r').read()
    
    res = run([f'{Path(__file__).parent.joinpath("proc1.exe")}', in1], encoding='utf-8', stdout=subprocess.PIPE)
    print(f'return code - {res.returncode}')
    print(f'stdout - {res.stdout}')

create_worker()