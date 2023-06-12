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

        self.password_label = Label(text="Пароль:", font_size=20)
        self.layout.add_widget(self.password_label)
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
    def __init__(self, master, player_name, **kwargs):
        global widgets, game_params
        # Установка соединения с сервером
        super(Game, self).__init__(**kwargs)
        # присваиваме ГЛОБАЛЬНОЙ переменной widgets шаблонный вид.
        # Далее, перед добавлением любого виджета на какой-либо layout 
        # он будет добавляться в какую-то ячейку словаря widgets
        widgets = {'buttons': {}, 'labels': {}, 'text_fields': {}, 'layouts': {}}
        layout = BoxLayout(orientation='vertical')
        # текущий список игроков, включая ведущего и нас
        players = game_params["players"]
        # колво игроков
        cur_players = len(players)
        # максимально допустимое число игроков (указано при создании пати)
        players_count = game_params["players_count"]
        players_layout = GridLayout(rows=2, cols=players_count+1, spacing=10)
        for p in range(players_count):
            # если текущий индекс есть в фактическом массиве игроков,
            # то берем имя от туда, иначе шаблон: "player_i"
            if p < cur_players:
                cur_text = players[p]
            else:
                cur_text = f"player_{p}"
            # Лейблы с именами игроков
            cur_label = Label(text=cur_text, font_size=20)
            widgets['labels'].setdefault('players', {})
            widgets['labels']['players'][cur_text] = cur_label
            players_layout.add_widget(cur_label) #name

        button_exit = Button(
                    text='Exit',
                    background_color = 'red',
                    on_release=self.switch_to_screen(master),
                )
        players_layout.add_widget(button_exit)
        
        for p in range(players_count):
            # То же самое, что и предыдущий виджет, но для лейблов с очками
            if p < cur_players:
                cur_text = players[p]
                game_params["cur_players"].append(cur_text)
            else:
                cur_text = f"player_{p}"
                game_params["cur_players"].append(None)
            cur_label = Label(text='0', font_size=20)
            widgets['labels'].setdefault('scores', {})
            widgets['labels']['scores'][cur_text] = cur_label
            players_layout.add_widget(cur_label) #score
            
        game_field = GridLayout(cols=2, padding=10, spacing=10)
        q_table = GridLayout(cols=game_params['table_size'][1]+1, padding=10, spacing=10)
        # Локаль
        q_label = Label(text='Ищи вопрос тут', font_size=40)
        for th in game_params['table']:
            # Лейблы с названиями тем
            cur_label = Label(text=th, font_size=20)
            cur_label.text_size = cur_label.size
            widgets['buttons'].setdefault('questions', {})
            widgets['labels'].setdefault('themes', {})
            widgets['labels']['themes'][th] = cur_label
            q_table.add_widget(cur_label)
            for q in game_params['table'][th]:
                if master:
                    but_func = empty_func
                else:
                    but_func = choose_button(th, q)
                # Кнопки с ценами вопросов
                button = Button(
                    text=str(q),
                    size_hint=(1, 0.2),
                    on_release=but_func,
                )
                widgets['buttons']['questions'].setdefault(th, {})
                widgets['buttons']['questions'][th][str(q)] = button
                q_table.add_widget(button)
            tmp_cost = -1
            for _ in range(len(game_params['table'][th]), game_params['table_size'][1]):
                button = Button(text = '', on_release = empty_func)
                widgets['buttons']['questions'][th][str(tmp_cost)] = button
                q_table.add_widget(button)
                tmp_cost -=1
        tmp_name = -1
        print("COMPARE:", len(game_params['table']),  game_params['table_size'][0])
        for _ in range(len(game_params['table']),  game_params['table_size'][0]):
            cur_label = Label(text='', font_size=20)
            cur_label.text_size = cur_label.size
            widgets['buttons'].setdefault('questions', {})
            widgets['labels'].setdefault('themes', {})
            widgets['labels']['themes'][str(tmp_name)] = cur_label
            q_table.add_widget(cur_label)
            tmp_cost = -1
            for _ in range(game_params['table_size'][1]):
                button = Button(
                    text='',
                    size_hint=(1, 0.2),
                    on_release=empty_func,
                )
                widgets['buttons']['questions'].setdefault(str(tmp_name), {})
                widgets['buttons']['questions'][str(tmp_name)][str(q)] = button
                q_table.add_widget(button)
                tmp_cost -= 1
            tmp_name -= 1


        widgets['labels']['q_label'] = q_label
        widgets['layouts']['table'] = q_table
        game_field.add_widget(q_table)
        game_field.add_widget(q_label)
        
        gamer_tools = BoxLayout(orientation='horizontal')
        # Лейбл для вывода сообщений через "info:"
        timer = Label(text='00:00', size=(10,10))
        widgets['labels']['timer'] = timer
        gamer_tools.add_widget(timer)
        info = Label(text='info:', size=(10,10))
        widgets['labels']['info'] = info
        gamer_tools.add_widget(info)
        
        if master:
            # Для окна ведущего
            answers = BoxLayout(orientation='vertical')
            # Лейбл на котором будет отображаться верный ответ
            # Локаль
            right_ans = Label(text='Верный ответ:')
            widgets['labels']['right_ans'] = right_ans
            answers.add_widget(right_ans)
            # Лейбл на котором будет отображаться текущий ответ игрока
            # Локаль
            curr_ans = Label(text='Ответ игрока')
            widgets['labels']['curr_ans'] = curr_ans
            answers.add_widget(curr_ans)
            gamer_tools.add_widget(answers)
            
            buttons = BoxLayout(orientation='vertical')
            # Кнопка для принятия ответа
            # Локаль
            button_accept = Button(text='Принять', background_color = red)
            widgets['buttons']['accept'] = button_accept
            buttons.add_widget(button_accept)
            # Кнопка для отклонения ответа
            # Локаль
            button_reject = Button(text='Отклонить', background_color = red)
            widgets['buttons']['reject'] = button_reject
            buttons.add_widget(button_reject)
            gamer_tools.add_widget(buttons)
        else:
            #Для окна игрока
            # кнопка для отправки ответа
            ans_button = Button(text='', background_color = red)
            widgets['buttons']['answer'] = ans_button
            gamer_tools.add_widget(ans_button)
            # Поле для ввода ответа
            ans_field = TextInput(background_color=(0, 0, 0, 1/255), readonly=True)
            widgets['text_fields']['answer'] = ans_field
            gamer_tools.add_widget(ans_field)
        
        layout.add_widget(players_layout)
        layout.add_widget(game_field)
        layout.add_widget(gamer_tools)
        widgets['layouts']['players'] = players_layout
        widgets['layouts']['game'] = game_field
        widgets['layouts']['tools'] = gamer_tools
        widgets['layouts']['main'] = layout
        self.add_widget(layout)
        # для ведущего своя функция-reader
        if master:
            self.reader_thread = threading.Thread(target = master_read, daemon = True)
        else:
            self.reader_thread = threading.Thread(target = client_read, args = (player_name,), daemon = True)
        self.reader_thread.start()
        self.timer_thread = threading.Thread(target = timer_func, args = (master,), daemon = True)
        self.timer_thread.start()

    
    def switch_to_screen(self, master):
        def switch(*args):
            global sock, finish_flag, server_proc
            finish_flag = True
            self.reader_thread.join()
            self.timer_thread.join()
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            if master:
                server_proc.kill()

            
            self.manager.current = 'main_menu'
            if self.manager.has_screen('game'):
               self.manager.remove_widget(self.manager.get_screen('game'))
        return switch


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
