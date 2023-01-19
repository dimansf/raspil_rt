


from raspil_rt.convertation import load_simple_config

import socket
from sys import argv

conf = load_simple_config(argv[2])
addr = (conf['host'], int(conf['port']))
conn = socket.create_connection(addr)
stop_code = '%end%'
def data1(file:str):
    
    with open(file, 'r') as f:
        conn.send(f.read().encode())
        
        while 1:
            res = conn.recv(1024).decode()
            print(res)
            if stop_code in res:
                break


data1(argv[1])


conn.close()