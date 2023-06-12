import random
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
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(Label(text='Своя игра', font_size=40))

        self.buttons = [
            ('Создать игру', 'create_game'),
            ('Присоединиться к игре', 'join_game'),
            ('Правила', 'rules'),
            ('Выход', 'exit'),
        ]

        for text, screen_name in self.buttons:
            button = Button(text=text, size_hint=(1, 0.2), on_release=self.switch_to_screen(screen_name))
            self.layout.add_widget(button)

        self.add_widget(self.layout)

    def switch_to_screen(self, screen_name):
        def switch(*args):
            if screen_name == 'exit':
                App.get_running_app().stop()
            else:
                self.manager.current = screen_name
                
        return switch


class CreateGame(Screen):
    pass
        
        
class JoinGame(Screen):
    pass


class Rules(Screen):
    pass


class MyApp(App):
    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(MainMenu(name='main_menu'))
        screen_manager.add_widget(CreateGame(name='create_game'))
        screen_manager.add_widget(JoinGame(name='join_game'))
        screen_manager.add_widget(Rules(name='rules'))

        return screen_manager
