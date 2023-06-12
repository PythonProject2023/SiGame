import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput


# сокет
sock = None
# словарь с виджетами
widgets = None
# параметры игры, которые приедут от сервера
game_params = None
# количество очков за выбранный вопрос
active_score = 0
# количество игроков, которые уже получили отказ (для ведущего)
reject_counts = 0
# флаг, определяющий есть в игре активный вопрос или нет (для игрока)
flag_passive = True
# флаг, который блокирует/разблокирует работу таймера
flag_timer = False
# флаг, который завершает работу треда с таймером
finish_flag = False
server_proc = None
red = [1, 0, 0, 1] 
green = [0, 1, 0, 1] 
blue = [0, 0, 1, 1] 
purple = [1, 0, 1, 1]
white = [1, 1, 1, 1]


class MainMenu(Screen):
    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.layout.add_widget(Label(text="Своя игра", font_size=40))

        self.buttons = [
            ("Создать игру", "create_game"),
            ("Присоединиться к игре", "join_game"),
            ("Правила", "rules"),
            ("Выход", "exit"),
        ]

        for text, screen_name in self.buttons:
            button = Button(
                text=text,
                size_hint=(1, 0.2),
                on_release=self.switch_to_screen(screen_name),
            )
            self.layout.add_widget(button)

        self.add_widget(self.layout)

    def switch_to_screen(self, screen_name):
        def switch(*args):
            if screen_name == "exit":
                App.get_running_app().stop()
            else:
                self.manager.current = screen_name

        return switch


class CreateGame(Screen):
    def __init__(self, **kwargs):
        super(CreateGame, self).__init__(**kwargs)
        self.layout = GridLayout(cols=2, padding=10, spacing=10)

        self.layout.add_widget(Label(text="Название игры:", font_size=20))
        self.game_name = TextInput(multiline=False)
        self.layout.add_widget(self.game_name)

        self.layout.add_widget(Label(text="Пароль:", font_size=20))
        self.password = TextInput(multiline=False, password=True)
        self.layout.add_widget(self.password)

        self.layout.add_widget(Label(text="Количество игроков:", font_size=20))
        self.players_slider = Slider(min=2, max=5, value=2, step=1)
        self.layout.add_widget(self.players_slider)

        self.layout.add_widget(Label(text="Прикрепить пакет:", font_size=20))
        self.package_path = TextInput(multiline=False)
        self.layout.add_widget(self.package_path)

        self.create_room_button = Button(
            text="Создать комнату", on_release=self.create_room
        )
        self.layout.add_widget(self.create_room_button)
        self.layout.add_widget(Label())

        self.add_widget(self.layout)

    def create_room(self, *args):
        global sock, game_params, server_proc
        game_name = self.game_name.text
        password = self.password.text
        players_count = int(self.players_slider.value)
        package_path = self.package_path.text
        # создание комнаты
        server_proc = multiprocessing.Process(target = server_starter, args=(game_name, password, package_path, players_count))
        server_proc.start()
        time.sleep(0.3)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 1350))
        sock.send(("master__oogway\n").encode())
        res = sock.recv(4096)
        sock.send((password + '\n').encode())
        res = sock.recv(4096)
        sock.send(('give me a pack' + '\n').encode())
        # Получаем от сервера строку с описанем игры
        game_params = eval(sock.recv(8192).decode())
        game_params['cur_players'] = []
        self.manager.add_widget(Game(True, "master__oogway", name="game"))
        # Переход на экран игры после присоединения к комнате
        self.manager.current = "game"


class JoinGame(Screen):
    def __init__(self, **kwargs):
        super(JoinGame, self).__init__(**kwargs)
        self.layout = GridLayout(cols=2, padding=10, spacing=10)

        self.layout.add_widget(Label(text="Название игры:", font_size=20))
        self.game_name = TextInput(multiline=False)
        self.layout.add_widget(self.game_name)

        self.layout.add_widget(Label(text="Пароль:", font_size=20))
        self.password = TextInput(multiline=False, password=True)
        self.layout.add_widget(self.password)

        self.layout.add_widget(Label(text="Ваше имя:", font_size=20))
        self.player_name = TextInput(multiline=False)
        self.layout.add_widget(self.player_name)

        self.join_button = Button(text="Присоединиться", on_release=self.join_game)
        self.layout.add_widget(self.join_button)
        self.layout.add_widget(Label())

        self.add_widget(self.layout)

    def join_game(self, *args):
        global game_params, sock
        game_name = self.game_name.text
        password = self.password.text
        player_name = self.player_name.text
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 1350))
        sock.send((f"{player_name}\n").encode())
        res = sock.recv(4096).decode()
        if res == 'sorry':
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        else:
            sock.send((password + '\n').encode())
            res = sock.recv(4096).decode()
            # Если пароль неверен, то здесь в res будет "sorry" вместо "hello"
            if res == 'sorry':
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                self.password_label.text = "Пароль: (Был введен неверный)"
                self.password_label.color = 'red'
            else:
                sock.send(('give me a pack' + '\n').encode())
                # Получаем от сервера строку с описанем игры
                game_params = eval(sock.recv(8192).decode())
                game_params['cur_players'] = []
                self.manager.add_widget(Game(False, player_name, name="game"))
                # Переход на экран игры после присоединения к комнате
                self.manager.current = "game"


class Game(Screen):
    pass


class Rules(Screen):
    def __init__(self, **kwargs):
        super(Rules, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.rules_label = Label(text="Правила и инструкции", font_size=30)
        self.layout.add_widget(self.rules_label)

        self.rules_text = """Здесь вы можете добавить инструкции."""

        self.rules = Label(
            text=self.rules_text, font_size=18, halign="left", valign="top"
        )
        self.rules.text_size = self.rules.size
        self.layout.add_widget(self.rules)

        self.back_button = Button(
            text="Назад", size_hint=(1, 0.2), on_release=self.back_to_main_menu
        )
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

    def back_to_main_menu(self, *args):
        self.manager.current = "main_menu"


class MyApp(App):
    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(MainMenu(name="main_menu"))
        screen_manager.add_widget(CreateGame(name="create_game"))
        screen_manager.add_widget(JoinGame(name="join_game"))
        screen_manager.add_widget(Rules(name="rules"))
        screen_manager.add_widget(Game(name="game"))

        return screen_manager
