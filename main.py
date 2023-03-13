# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request

application = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

# Потом будем брать из бд или типо того
subjectList = [
                "Предмет 1",
                "Предмет 2",
                "Предмет 3",
                "Предмет 4",
                "Предмет 5",
]


# Задаем параметры приложения Flask.
@application.route("/", methods=['POST'])
def main():
    # Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': subjectList
        }

        res['response']['text'] = 'Привет! У меня есть тесты по следующим предметам: 1, 2, 3, 4. ' \
                                  'Выберите предмет или попросите рассказать про другие'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'предмет 1',
        'первый',
        'один',
    ]:
        # Выбрали первый предмет
        res['response']['text'] = 'Первый предмет самый сложный'
        return

    if req['request']['original_utterance'].lower() in [
        'другие',
        'расскажи про другие',
        'ещё предметы',
    ]:
        if sessionStorage[user_id]['suggests']:
            res['response']['text'] = 'У меня есть тесты по следующим предметам: ' \
                                      + sessionStorage[user_id]['suggests'][0] \
                                      + ' Выберите предмет или попросите рассказать про другие'
            res['response']['buttons'] = get_suggests(user_id)
            return
        else:
            res['response']['text'] = 'По другим предметам тестов у меня нет'
            sessionStorage[user_id]['suggests'] = subjectList
            return

    # Если юзер сказал то, что мы не обработали
    res['response']['text'] = 'Я вас не поняла, повторите еще'


# Функция возвращает 4 подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем 4 первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:4]
    ]

    # Убираем первые 4 подсказки, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][4:]
    sessionStorage[user_id] = session

    return suggests


if __name__ == "__main__":
    application.run()
