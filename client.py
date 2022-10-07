


# # from __init__ import __init__

# # __init__()
# import socket
# from raspil_py.tests.main_test import  big_input,small1_input

# host = 'localhost'
# port = 11999
# addr = (host, port)
# conn = socket.create_connection(addr)

# def data1():
#     with open(small1_input, 'r') as f:
#         conn.send(f.read().encode())
#         conn.send('...///'.encode())
# def data3():
#     with open(big_input, 'r') as f:
#         conn.send(f.read().encode())
#         conn.send('...///'.encode())


# def data_test():
#      conn.send('12345678..9'.encode())

# data1()

# print(f'name is {conn.recv(1024).strip().decode()}')
# conn.close()
class B:
    def f(self,x:tuple[int, int]):
            return x[0]+ x[1]
def pools():
    from multiprocessing import Pool
    data = [(1,2), (3,4)]
    b = B()
    with Pool(2) as p:
        res = p.starmap(b.f, data)
    print(res)


if __name__ == "__main__":
    pools()