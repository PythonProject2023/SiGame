import os

translations = {
    "Своя игра": "My game",
    "Создать игру": "Create game",
    "Присоединиться к игре": "Join game",
    "Правила": "Rules",
    "Сменить язык": "Change language",
    "Выход": "Exit",
    "Название игры:": "Game name:",
    "Пароль:": "Password:",
    "Количество игроков:": "Number of players:",
    "Прикрепить пакет:": "Attach packet:",
    "Создать комнату": "Create room",
    "Ваше имя:": "Your name:",
    "Присоединиться": "Join",
    "Правила и инструкции": "Rules and instructions",
    "Назад": "Back",
    "Игрок": "Player",
    "ответил": "answered",
    "Ищи вопрос тут": "Question will be here",
    "ТЕКСТ ВОПРОСА": "QUESTION TEXT",
    "ТЕКУЩИЙ ВОПРОС": "CURRENT QUESTION",
    "Ваш ответ правильный": "Your answer is correct",
    "ответил правильно": "answered correctly",
    "Ваш ответ неправильный": "Your answer is incorrect",
    "ответил неправильно": "answered incorrectly",
    "подключился": "connected",
    "Правильный ответ": "Correct answer",
    "Ответ игрока": "Player's answer",
    "Верный ответ:": "Correct answer:",
    "Принять": "Accept",
    "Отклонить": "Reject",
    "Пароль": "Password",
    "Был введен неверный": "incorrect password was entered",
    "победил в игре": "won the game",
    "Время вышло": "Time has gone",
    "Выход": "Exit"
}



langs = {
    "ru": {v: k for k, v in translations.items()},
    "en": translations
}

# Create the necessary directories and files
for lang, trans in langs.items():
    dir_path = os.path.join("locale", lang, "LC_MESSAGES")
    os.makedirs(dir_path, exist_ok=True)

    with open(os.path.join(dir_path, "myapp.po"), "w") as f:
        # Write header
        f.write('msgid ""\n')
        f.write('msgstr ""\n')
        f.write('"Content-Type: text/plain; charset=UTF-8\\n"\n\n')

        # Write translations
        for original, translated in trans.items():
            f.write(f'msgid "{original}"\n')
            f.write(f'msgstr "{translated}"\n\n')

print("Translation files have been successfully created!")


# После
# python src/utils/generate_translation.py 
# msgfmt ./locale/en/LC_MESSAGES/myapp.po -o ./locale/en/LC_MESSAGES/myapp.mo
# msgfmt ./locale/ru/LC_MESSAGES/myapp.po -o ./locale/ru/LC_MESSAGES/myapp.mo