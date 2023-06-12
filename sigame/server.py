import asyncio
import shlex
from io import StringIO
import random
import copy
import locale
import os
import gettext
from sigame.parser import parse_package


clients = {}
master = ''
password = 'password'
game_params = None
question_counter = 0
target_questions = 0
cur_round = 0
p_path = ''


def get_round(package_path):
    global target_questions, cur_round
    package = parse_package(package_path)
    max_len = 0
    for round in range(len(package.rounds)):
        print(round)
        if len(package.rounds[round].themes) > max_len:
            max_len = len(package.rounds[round].themes)
    themes = package.rounds[cur_round].themes
    cur_table = {th: {str(q): (themes[th].get_question(q).get_text(),
                      themes[th].get_question(q).get_answer().get_right()) 
                      for q in themes[th].questions} for th in themes}
    table_size = (max_len, max([len(themes[th].questions) for th in themes]))
    #target_questions = table_size[0]*table_size[1]
    target_questions = 3
    cur_round += 1
    return (cur_table, table_size)


async def SIG(reader, writer):
    """Функция, реализуящая функциональности сервера.

    Организует запуск на выполнение принимаемых от пользователя команд,
    а также посылает ответы пользователю или широковещательные сообщения.
    """
    global clients, master, password, game_params, question_counter, target_questions, p_path
    to_login = asyncio.create_task(reader.readline())
    res = await to_login
    to_pass = asyncio.create_task(reader.readline())
    res.decode()[:-1]
    name = res.decode()[:-1]

    if len(clients) == 0:
        master = name

    if name in clients:
        writer.write(("sorry").encode())
        await writer.drain()
        return False
    else:
        writer.write(("hello").encode())
        await writer.drain()

    res = await to_pass
    to_get = asyncio.create_task(reader.readline())
    got_password = res.decode()[:-1]
    if got_password == password:
        for cur_name in clients:
            await clients[cur_name].put(f'connect {name}')
        writer.write(("hello").encode())
        await writer.drain()
    else:
        writer.write(("sorry").encode())
        await writer.drain()
        return False

    game_params['players'].append(name)
    await to_get
    writer.write(str(game_params).encode())
    await writer.drain()   
    clients[name] = asyncio.Queue()

    # создаем два задания: на чтение и на запись
    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients[name].get())

    while not reader.at_eof():
        # обрабатываем выполненные задания с учетом того, что они могут закончиться одновременно
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())
                cur_rcv = q.result().decode()
                cur_cmd = shlex.split(cur_rcv)
                if len(cur_cmd) != 0:
                    if cur_cmd[0] == "choose":
                        question_counter += 1
                    elif question_counter == target_questions and cur_cmd[0] == "verdict":
                        cur_rcv += ' next'
                    elif cur_cmd[0] == "give":
                        cur_round = get_round(p_path)
                        cur_rcv = f"give {cur_round}\n"
                    for cur_name in clients:
                        await clients[cur_name].put(cur_rcv)
            elif q is receive:
                # достаем результат из очереди и посылаем его клиенту
                receive = asyncio.create_task(clients[name].get())
                cur_rcv = q.result()
                writer.write(cur_rcv.encode())
                await writer.drain()
        else:
            continue
        break
    # закрываем соединение
    send.cancel()
    receive.cancel()

    writer.write("quit".encode())
    await writer.drain()

    del clients[name]
    writer.close()
    await writer.wait_closed()

    await clients[cur_name].put(("{} has disconnected").format(name))

    return True


async def main(game_name, real_password, package_path, players_count):
    """Запуск сервера."""
    global password, game_params, target_questions, cur_round, p_path
    p_path = package_path
    cur_table, table_size = get_round(package_path)
    game_params = {"table": cur_table,
                   "table_size": table_size,
                   "game_name": game_name,
                   "players_count": players_count,
                   "players": []}   
    password = real_password
    server = await asyncio.start_server(SIG, '0.0.0.0', 1321)
    async with server:
        await server.serve_forever()


def server_starter(game_name, real_password, package_path, players_count):
    asyncio.run(main(game_name, real_password, package_path, players_count))
