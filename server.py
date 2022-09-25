# Модуль socketserver для сетевого программирования


from socketserver import StreamRequestHandler, TCPServer
from json import loads
from convertation import convertation_for_program

import random
from main import Program
# данные сервера
host = 'localhost'
port = 8888
addr = (host, port)

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
        # program.main()
        # with open(os.path.join(out_path, name), 'w') as f:
        #     f.write(str(program.resulted_cutsaw))
        
        
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