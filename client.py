




import socket
from raspil_rt.tests.main_test import  big_input,small1_input

host = 'localhost'
port = 8888
addr = (host, port)
conn = socket.create_connection(addr)

def data1():
    with open(small1_input, 'r') as f:
        conn.send(f.read().encode())
        conn.send('...///'.encode())
def data3():
    with open(big_input, 'r') as f:
        conn.send(f.read().encode())
        conn.send('...///'.encode())


def data_test():
     conn.send('12345678..9'.encode())

data3()

print(f'name is {conn.recv(1024).strip().decode()}')
conn.close()