from flask import Flask, request
import logging
import json
from random import choice
from Get_sheet import list_of_dicts

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. Начнём игру?'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ]
    else:
        if not sessionStorage[user_id]['game_started']:
            if 'да' in req['request']['nlu']['tokens']:
                if len(sessionStorage[user_id]['guessed_cities']) == 3:
                    res['response']['text'] = 'Ты сварил прекрасное зелье!'
                    res['end_session'] = True
                else:
                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            else:
                res['response']['text'] = 'Не поняла ответа! Так да или нет?'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    }
                ]
        else:
            play_game(res, req)


def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        quest = get_quest(list_of_dicts)
        while quest in sessionStorage[user_id]['quest']:
            quest = get_quest(list_of_dicts)
        sessionStorage[user_id]['quest'] = quest
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = quest['quest']
        res['response']['card']['image_id'] = quest['image']
        res['response']['text'] = 'Тогда сыграем!'
        res['response']['buttons'] = [
            {
                'title': quest['var1'],
                'hide': True
            },
            {
                'title': quest['var2'],
                'hide': True
            },
            {
                'title': quest['var3'],
                'hide': True
            },
        ]
    else:
        quest = get_quest(list_of_dicts)
        if quest in sessionStorage[user_id]['quest']:
            if req['request']['original_utterance'].lower() == quest['answer'].lower():
                res['response']['text'] = 'Правильно! Переходим к следующему вопросу?'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                ]
            return

        if req['request']['original_utterance'].lower() == quest['answer'].lower():
            res['response']['text'] = 'Правильно!'
            sessionStorage[user_id]['quest'].append(quest)
            return
        else:
            res['response']['text'] = 'Неправильно'
            if attempt == 3:
                res['response']['text'] = f'Вы пытались. Сыграем ещё?'
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['quest'].append(quest)
                return
            else:
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = 'Неправильно.'
                res['response']['card']['image_id'] = '12' ## Сюда фигачим айдишник разбитого зелья
                res['response']['text'] = 'А вот и не угадал!'
    sessionStorage[user_id]['attempt'] += 1



def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)\



def get_quest(sp):
    try:
        question = choice(sp)
        sp.remove(question)
        return question
    except Exception as e:
        return 'А вопросы кончились'

