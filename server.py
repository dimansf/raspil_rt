# Модуль socketserver для сетевого программирования
import traceback
import os
from json import loads


from pathlib import Path



from socketserver import StreamRequestHandler, TCPServer
from convertation import load_simple_config


from raspil_py.convertation import convertation_for_program


import random
from main import Program

config_file = Path(__file__).parent.joinpath('config.txt')

config = load_simple_config(str(config_file))

# данные сервера

addr = (config['localhost'], int(config['port']))

# обработчик запросов TCP подкласс StreamRequestHandler



class MyTCPHandler(StreamRequestHandler):

    # функция handle делает всю работу, необходимую для обслуживания запроса.
    # доступны несколько атрибутов: запрос доступен как self.request, адрес как self.client_address, экземпляр сервера как self.server
    def handle(self):
        data = ''
        while 1:
            data +=  self.request.recv(1024).strip().decode()
            if '...///' in data: break
        
        print(data)
        
        data = loads(data[:-6])
        boards, store_boards, optimize = \
            convertation_for_program(data['orders'], data['store'], data['optimize'])
        
        program = Program(boards, store_boards, optimize,
                          data['store_order'], int(data['width_saw']))
        name = f'{bytes([random.randint(65, 90) for _ in range(100)]).decode()}.txt'

        
        print('Имя отправлено')
        self.request.sendall(name.encode())
        program.main()
        try:
            with open(os.path.join(config['out_path'], name), 'w') as f:
                f.write(str(program.resulted_cutsaw))
        except Exception as ex :
            with open(config['log_file'], 'w') as f:
                tb_str = traceback.format_exception(type(ex), ex, tb=ex.__traceback__)
                f.write("".join(tb_str))
        
        
    def execute_new_process(self):
        pass

def run_server(addr:tuple[str, int]):

    try:

        server = TCPServer(addr, MyTCPHandler)
        print('starting server... for exit press Ctrl+C')
        server.serve_forever()
    except Exception as e:
        with open('error.log', 'w+') as f:
            f.write(repr(e.with_traceback(None)))


if __name__ == "__main__":
    run_server(addr)


