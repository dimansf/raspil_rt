# Модуль socketserver для сетевого программирования

from sys import argv
import socket
import json
from multiprocessing import Process

from json import loads
import random


from pathlib import Path


from raspil_rt.convertation import load_simple_config


from raspil_rt.main import Program


from raspil_rt.convertation import convertation_for_program
import traceback
import os


def handle_program(config: dict[str, str],
                   conn: socket.socket):
    data = ''
    conn.settimeout(1.1)
    try:
        while 1:
            data += conn.recv(1024).strip().decode()
    except TimeoutError:
        pass
    print(data)

    data = loads(data)

    name = f'{bytes([random.randint(65, 90) for _ in range(100)]).decode()}.txt'

    print('Имя отправлено')
    conn.sendall(name.encode())
    boards, store_boards, optimize = \
        convertation_for_program(
            data['orders'], data['store'], data['optimize'])

    program = Program(boards, store_boards, optimize,
                      data['store_order'], int(data['width_saw']))
    program.setCallcaback(conn)
    try:
        program.main()
        out_file = os.path.join(config['out_path'], name)
        Path(config['out_path']).mkdir(parents=True, exist_ok=True)
        with open(out_file, 'w') as f:
            f.write(str(program.resulted_cutsaw))
    except Exception as ex:
        Path(config['log_file']).parent.mkdir(parents=True, exist_ok=True)
        with open(config['log_file'], 'w') as f:
            tb_str = traceback.format_exception(
                type(ex), ex, tb=ex.__traceback__)
            f.write("".join(tb_str))
    finally:
        conn.sendall('%end%'.encode())
        conn.close()


def load_config(path: str) -> dict[str, str]:
    try:
        config_file = Path(path)
        config = load_simple_config(str(config_file))
        return config
    except:
        raise Exception('Cant load config')


config = load_config(argv[1])
addr = (config['host'], int(config['port']))


processes: list[Process] = []


def run_serve(addr: tuple[str, int]):

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(addr)
            s.listen(5)
            while 1:
                
                conn, addr = s.accept()
                
                p = Process(target=handle_program, args=(config, conn))

                p.start()

                processes.append(p)
                print(f'processes status {[x.exitcode for x in processes]}')
                print('Сервер ждет поключения')

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
    print(json.dumps(config, sort_keys=True, indent=4))
    if not is_port_in_use(addr[1]):
        run_serve(addr)

    else:
        print('Port is not free.')
