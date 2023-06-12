import zipfile
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


class Answer:
    def __init__(self, right, wrong=None, text=None, image=None, sound=None, video=None):
        self.right = right
        self.wrong = wrong
        self.text = text
        self.image = image
        self.sound = sound
        self.video = video

    def get_right(self):
        return self.right

    def get_wrong(self):
        return self.wrong
    
    def get_text(self):
        return self.text

    def get_image(self):
        return self.image

    def get_sound(self):
        return self.sound

    def get_video(self):
        return self.video


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

    def add_answer(self, ans):
        self.ans = ans

    def get_answer(self):
        return self.ans


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
        return f"{author}\n\n" + '\n'.join(str(i) for i in self.rounds)


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
author = authors.find('ns:author', namespace).text
p.set_author(author)

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
            marker_flag = False
            it = iter(scen.findall('ns:atom', namespace))
            for atom in it:
                if (tp := atom.get('type')):
                    match tp:
                        case 'image':
                            im = atom.text
                        case 'voice':
                            snd = atom.text
                        case 'video':
                            vd = atom.text
                        case 'marker':   #всё, что дальше - ответ
                            marker_flag = True
                            break
                        case _:
                            txt = atom.text
            Q = Question(pr, txt, im, snd, vd)
            if marker_flag:
                r_ans = None
                w_ans = None
                txt = None
                im = None
                snd = None
                vd = None
                for atom in it:
                    if (tp := atom.get('type')):
                        match tp:
                            case 'image':
                                im = atom.text
                            case 'voice':
                                snd = atom.text
                            case 'video':
                                vd = atom.text
                            case _:
                                txt = atom.text
            else:
                r_ans = q.find('ns:right', namespace)
                r_ans = r_ans.find('ns:answer', namespace).text
                w_ans = q.find('ns:wrong', namespace)
                if w_ans is not None:
                    w_ans = w__ans.find('ns:answer', namespace).text  # надо найти пакет
            ans = Answer(r_ans, w_ans, txt, im, snd, vd)
            Q.add_answer(ans)
            T.add_question(Q)