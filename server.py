import asyncio
import shlex
from io import StringIO
import random
import copy
import locale
import os
import gettext
from .parser import parse_package


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
	pass

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
    server = await asyncio.start_server(SIG, '0.0.0.0', 1350)
    async with server:
        await server.serve_forever()


def server_starter(game_name, real_password, package_path, players_count):
    asyncio.run(main(game_name, real_password, package_path, players_count))
