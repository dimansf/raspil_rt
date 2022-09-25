




import socket
from raspil_rt.tests.main_test import big_input

host = 'localhost'
port = 8888
addr = (host, port)
conn = socket.create_connection(addr)

def data1():
    with open(big_input, 'r') as f:
        conn.send(f.read().encode())
        conn.send('...///'.encode())


def data2():
     conn.send('12345678..9'.encode())

data1()

print(f'name is {conn.recv(1024).strip().decode()}')