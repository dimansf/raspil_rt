# Модуль socketserver для сетевого программирования


from socketserver import StreamRequestHandler, TCPServer




# данные сервера
host = 'localhost'
port = 8888
addr = (host, port)

# обработчик запросов TCP подкласс StreamRequestHandler


class MyTCPHandler(StreamRequestHandler):

    def handle(self):
        data = ''
        while 1:
            data +=  self.request.recv(1024).strip().decode()
            if '...///' in data: break
            
        
        
     
        
        
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