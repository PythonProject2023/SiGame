import zipfile
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


class Question:

    def __init__(self, price, text=None, image=None, sound=None, video=None):
        self.price = price
        self.text = text
        self.image = image
        self.sound = sound
        self.video = video

    def get_price(self):
        return self.price
    
    def get_text(self):
        return self.text

    def get_image(self):
        return self.image

    def get_sound(self):
        return self.sound

    def get_video(self):
        return self.video


class Theme:
    questions = list()

    def __init__(self, name):
        self.name = name

    def add_question(self, q):
        self.questions.append(q)

    def get_question(self):
        yield from self.questions

    def __str__(self):
        return self.name


class Round:
    themes = list()

    def __init__(self, name):
        self.name = name

    def add_theme(self, t):
        self.themes.append(t)

    def get_theme(self):
        yield from self.themes

    def __str__(self):
        return self.name


class Package:
    author = ''
    rounds = list()

    def set_author(self, a):
        self.author = a

    def get_author(self):
        return self.author

    def add_round(self, round):
        self.rounds.append(round)

    def get_round(self):
        yield from self.rounds

    def __str__(self):
        return f"{author}\n" + '\n'.join(self.rounds)


directory_path = Path.cwd()
packet_path = sys.argv[1]

with zipfile.ZipFile(packet_path) as file:
    file_list = file.namelist()
    with file.open(file_list[0]) as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()

# Получаем пространство имен из корневого элемента
namespace = {'ns': root.tag.split('}')[0].strip('{')}

p = Package()

# Используем пространство имен при поиске элементов
info = root.find('ns:info', namespace)
authors = info.find('ns:authors', namespace)
author = authors.find('ns:author', namespace)
p.set_author(author.text)

game = root.find('ns:rounds', namespace)
for rnd in game.findall('ns:round', namespace):
    R = Round(rnd.get('name'))
    p.add_round(R)
    topics = rnd.find('ns:themes', namespace)
    for t in topics.findall('ns:theme', namespace):
        T = Theme(t.get('name'))
        R.add_theme(T)
        qs = t.find('ns:questions', namespace)
        for q in qs.findall('ns:question', namespace):
            pr = q.get('price', namespace)
            txt = None
            im = None
            snd = None
            vd = None
            scen = q.find('ns:scenario', namespace)
            for atom in scen.findall('ns:atom', namespace):
                if (tp := atom.get('type')):
                    match tp:
                        case 'image':
                            im = atom.text
                        case 'voice':
                            snd = atom.text
                        case 'video':
                            vd = atom.text
                        case 'marker':   # всё, что дальше - ответ
                            continue
                        case _:
                            txt = atom.text
            Q = Question(pr, txt, im, snd, vd)
            T.add_question(Q)