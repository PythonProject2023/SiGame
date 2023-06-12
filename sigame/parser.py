"""
Парсер пакета.
"""
import zipfile
import xml.etree.ElementTree as ET
import urllib.parse


class Answer:
    """
    Класс ответа на вопрос.

    :param right: верный ответ на вопрос.
    :type right: str
    :param wrong: неверный ответ на вопрос.
    :type wrong: str
    :param text: текст ответа на вопрос, если ответ составной.
    :type text: str
    :param image: ссылка на рисунок ответа.
    :type image: str
    :param sound: ссылка на звук ответа.
    :type sound: str
    :param video: ссылка на видео ответа.
    :type video: str
    """

    def __init__(self, right, wrong=None, text=None, image=None, sound=None, video=None):
        self.right = right
        self.wrong = wrong
        self.text = text
        self.image = urllib.parse.quote(image.encode('utf-8')) if image is not None else None
        self.sound = urllib.parse.quote(sound.encode('utf-8')) if sound is not None else None
        self.video = urllib.parse.quote(video.encode('utf-8')) if video is not None else None

    def get_right(self):
        """
        Получение правильного ответа.

        :rtype: str
        :return: правильный ответ.
        """

        return self.right

    def get_wrong(self):
        """
        Получение неправильного ответа.

        :rtype: str
        :return: неправильный ответ.
        """
        return self.wrong

    def get_text(self):
        """
        Получение текста ответа.

        :rtype: str
        :return: текст ответа.
        """

        return self.text

    def get_image(self):
        """
        Получение ссылки на картинку ответа.

        :rtype: str
        :return: ссылка на картинку ответа.
        """

        return self.image

    def get_sound(self):
        """
        Получение ссылки на звук ответа.

        :rtype: str
        :return: ссылка на звук ответа.
        """

        return self.sound

    def get_video(self):
        """
        Получение ссылки на видео ответа.

        :rtype: str
        :return: ссылка на видео ответа.
        """

        return self.video


class Question:
    """
    Класс вопроса.

    :param price: стоимость вопроса.
    :type price: str
    :param text: текст вопроса.
    :type text: str
    :param image: ссылка на рисунок вопроса.
    :type image: str
    :param sound: ссылка на звук вопроса.
    :type sound: str
    :param video: ссылка на видео вопроса.
    :type video: str
    """

    def __init__(self, price, text=None, image=None, sound=None, video=None):
        self.price = price
        self.text = text
        self.image = urllib.parse.quote(image.encode('utf-8')) if image is not None else None
        self.sound = urllib.parse.quote(sound.encode('utf-8')) if sound is not None else None
        self.video = urllib.parse.quote(video.encode('utf-8')) if video is not None else None

    def get_price(self):
        """
        Получение стоимости вопроса.

        :rtype: str
        :return: стоимость вопроса.
        """

        return self.price

    def get_text(self):
        """
        Получение текста вопроса.

        :rtype: str
        :return: текст вопроса.
        """

        return self.text

    def get_image(self):
        """
        Получение ссылки на картинку вопроса.

        :rtype: str
        :return: ссылка на картинку вопроса.
        """

        return self.image

    def get_sound(self):
        """
        Получение ссылки на звук вопроса.

        :rtype: str
        :return: ссылка на звук вопроса.
        """

        return self.sound

    def get_video(self):
        """
        Получение ссылки на видео вопроса.

        :rtype: str
        :return: ссылка на видео вопроса.
        """

        return self.video

    def add_answer(self, ans):
        """
        Добавление ответа на вопрос.
        """

        self.ans = ans

    def get_answer(self):
        """
        Получение ответа на вопрос.

        :rtype: Answer
        :return: объект - ответ на вопрос.
        """

        return self.ans


class Theme:
    """
    Тема вопросов.

    :param name: название темы.
    :type name: str
    :param questions: словарь вопросов.
    :type questions: dict
    """

    def __init__(self, name):
        self.name = name
        self.questions = dict()

    def add_question(self, q):
        """
        Добавление вопроса.

        :param q: объект - вопрос.
        :type q: Question
        """
        self.questions[q.get_price()] = q

    def get_question(self, p):
        """
        Получение вопроса.

        :param p: стоимость вопроса.
        :type p: str

        :rtype: Question
        :return: объект - вопрос.
        """

        return self.questions[p]

    def __str__(self):
        return self.name


class Round:
    """
    Раунд.

    :param name: название раунда.
    :type name: str
    :param themes: темы вопросов.
    :type themes: dict
    """

    def __init__(self, name):
        self.name = name
        self.themes = dict()

    def add_theme(self, t):
        """
        Добавление темы.

        :param t: тема.
        :type t: Theme
        """

        self.themes[str(t)] = t

    def get_theme(self, nm):
        """
        Получение темы.

        :param nm: название темы.
        :type nm: str

        :rtype: Theme
        :return: объект - тема.
        """

        return self.themes[nm]

    def __str__(self):
        return self.name


class Package:
    """
    Пакет вопросов.

    :param author: автор пакета.
    :type author: str
    :param rounds: раунды игры.
    :type rounds: list
    """

    author = ''
    rounds = list()

    def set_author(self, a):
        """
        Добавление автора.

        :param a: автор.
        :type a: str
        """

        self.author = a

    def get_author(self):
        """
        Получение автора.

        :rtype: str
        :return: автор.
        """
        return self.author

    def add_round(self, rnd):
        """
        Добавление раунда.

        :param rnd: раунд.
        :type rnd: Round
        """
        self.rounds.append(rnd)

    def get_round(self, num):
        """
        Получение раунда.

        :param num: номер раунда.
        :type num: int
        :rtype: Round
        :return: раунд.
        """

        return self.rounds[num]

    def __str__(self):
        return f"{self.author}\n\n" + '\n'.join(str(i) for i in self.rounds)


def parse_package(packet_path):
    """
    Парсинг пакета.

    :param packet_path: путь к файлу-пакету.
    :type packet_path: str

    :rtype: Package
    :return: пакет.
    """

    with zipfile.ZipFile(packet_path) as file:
        with file.open('content.xml') as xml_file:
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
                                im = 'Images/' + atom.text[1:]
                            case 'voice':
                                snd = 'Audio/' + atom.text[1:]
                            case 'video':
                                vd = 'Video/' + atom.text[1:]
                            case 'marker':   # всё, что дальше - ответ
                                marker_flag = True
                                break
                            case _:
                                txt = atom.text
                    else:
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
                                    im = 'Images/' + atom.text[1:]
                                case 'voice':
                                    snd = 'Audio/' + atom.text[1:]
                                case 'video':
                                    vd = 'Video/' + atom.text[1:]
                                case _:
                                    txt = atom.text
                        else:
                            txt = atom.text
                else:
                    r_ans = q.find('ns:right', namespace)
                    r_ans = r_ans.find('ns:answer', namespace).text
                    w_ans = q.find('ns:wrong', namespace)
                    if w_ans is not None:
                        if w_ans.find('ns:answer', namespace) is not None:
                            w_ans = w_ans.text  # надо найти пакет
                ans = Answer(r_ans, w_ans, txt, im, snd, vd)
                Q.add_answer(ans)
                T.add_question(Q)
    return p

# p = parse_package(sys.argv[1])
# for i in p.rounds:
#    print(i.name)
#    for j in i.themes:
#        print(j)
#    print('\n\n\n')

# print(p.get_round(0).get_theme('Тело человека').get_question('200').get_text())
