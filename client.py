



import socket
from raspil_rt.tests.main_test import big_input

host = 'localhost'
port = 8888
addr = (host, port)
conn = socket.create_connection(addr)

with open(big_input, 'r') as f:
    conn.send(f.read().encode())
    conn.send('\\r\\n'.encode())

print(bytes.decode(conn.recv(1024)))