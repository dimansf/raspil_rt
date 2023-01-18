# Модуль socketserver для сетевого программирования


import json
from multiprocessing import Process

from json import loads
import random


from pathlib import Path


from socketserver import StreamRequestHandler, TCPServer


from raspil_rt.convertation import load_simple_config


from raspil_rt.main import Program


from typing import Any
from raspil_rt.convertation import convertation_for_program
import traceback
import os




def handle_program(data: dict[str, Any], name:str, config:dict[str,str]):
    boards, store_boards, optimize = \
        convertation_for_program(
            data['orders'], data['store'], data['optimize'])

    program = Program(boards, store_boards, optimize,
                      data['store_order'], int(data['width_saw']))
    
    try:
        program.main()
        with open(os.path.join(config['out_path'], name), 'w') as f:
            f.write(str(program.resulted_cutsaw))
    except Exception as ex:
        with open(config['log_file'], 'w') as f:
            tb_str = traceback.format_exception(
                type(ex), ex, tb=ex.__traceback__)
            f.write("".join(tb_str))

def load_config():
    try:
        config_file = Path(__file__).parent.joinpath('config.txt')
        config = load_simple_config(str(config_file))
        return config
    except:
        raise Exception('Cant load config')



config = load_config()
addr = (config['localhost'], int(config['port']))


processes:list[Process] = []

class MyTCPHandler(StreamRequestHandler):

    # функция handle делает всю работу, необходимую для обслуживания запроса.
    # доступны несколько атрибутов: запрос доступен как self.request, адрес как self.client_address, экземпляр сервера как self.server
    def handle(self):
        data = ''
        while 1:
            data += self.request.recv(1024).strip().decode()
            if '...///' in data:
                break

        print(data)
        data = loads(data[:-6])

        name = f'{bytes([random.randint(65, 90) for _ in range(100)]).decode()}.txt'

        print('Имя отправлено')
        self.request.sendall(name.encode())
        
        p = Process(target=handle_program, args=(data,name, config))
        
        p.start()list(list(r)[0])[1]
        processes.append(p)
        print(f'processes status {[x.exitcode for x in processes]}')
        

    def execute_new_process(self):
        pass




def run_server(addr: tuple[str, int]):

    try:

        print('starting server... for exit press Ctrl+C')
        server = TCPServer(addr, MyTCPHandler)
        server.serve_forever()
    except Exception as e:
        with open('error.log', 'w+') as f:
            f.write(repr(e.with_traceback(None)))
    finally:
        for p in processes:
            p.join()

def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0



if __name__ == "__main__":
    print(json.dumps(config,sort_keys=True, indent=4))
    if not is_port_in_use(addr[1]):
        run_server(addr)
        
    else:
        print('Port is not free.')


    