from flask import Flask, request
import logging
import json
from random import choice
from Get_sheet import list_of_dicts

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

bad_image = '1030494/c85f3ac0666a9fca691b'


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
            sessionStorage[user_id]['guessed_quest'] = []
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
                if len(sessionStorage[user_id]['guessed_quest']) == 10:
                    res['response']['text'] = 'Ты сварил прекрасное зелье!'
                    res['end_session'] = True
                else:
                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    que = get_quest(list_of_dicts)
                    sessionStorage[user_id]['quest'] = que
                    play_game(res, req, sessionStorage[user_id]['quest'])
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
            play_game(res, req, sessionStorage[user_id]['quest'])


def play_game(res, req, que):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    quest = que
    if attempt == 1:
        sessionStorage[user_id]['quest'] = quest
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = quest['quest']
        res['response']['card']['image_id'] = quest['image']
        res['response']['text'] = quest['quest'][:-1:]
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
            }
        ]
    else:
        print(str(req['request']['original_utterance']).capitalize())
        print(quest['answer'])
        if str(req['request']['original_utterance']).capitalize() in str(quest['answer']):
            res['response']['text'] = 'Правильно! Сыграем ещё?'
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
            sessionStorage[user_id]['guessed_quest'].append(quest)
            sessionStorage[user_id]['game_started'] = False
            return
        else:
            if attempt == 3:
                bad_image
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = f'Вы пытались. Это {quest["answer"]}. Сыграем ещё?'
                res['response']['text'] = f'Вы пытались. Это {quest["answer"]}. Сыграем ещё?'
                res['response']['card']['image_id'] = bad_image

                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_quest'].append(quest)
                return
            else:
                res['response']['text'] = f'Неправильно, подумайте ещё.\n{quest["quest"]}'
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
                    }
                ]
    sessionStorage[user_id]['attempt'] += 1


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


def get_quest(sp):
    try:
        question = choice(sp)
        sp.remove(question)
        return question
    except Exception as e:
        return 'А вопросы кончились'


if __name__ == '__main__':
    app.run()
