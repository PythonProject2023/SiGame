from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider


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
        game_name = self.game_name.text
        password = self.password.text
        players_count = int(self.players_slider.value)
        package_path = self.package_path.text

        # создание комнаты
        print("Создание комнаты")
        print(f"Название игры: {game_name}")
        print(f"Пароль: {password}")
        print(f"Количество игроков: {players_count}")
        print(f"Путь к пакету: {package_path}")

        # Переход на экран игры после создания комнаты
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
        game_name = self.game_name.text
        password = self.password.text
        player_name = self.player_name.text

        print("Присоединение к игре")
        print(f"Название игры: {game_name}")
        print(f"Пароль: {password}")
        print(f"Ваше имя: {player_name}")

        # Переход на экран игры после присоединения к комнате
        self.manager.current = "game"


class Game(Screen):
    pass


class Rules(Screen):
    pass


class MyApp(App):
    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(MainMenu(name="main_menu"))
        screen_manager.add_widget(CreateGame(name="create_game"))
        screen_manager.add_widget(JoinGame(name="join_game"))
        screen_manager.add_widget(Rules(name="rules"))
        screen_manager.add_widget(Game(name="game"))

        return screen_manager
