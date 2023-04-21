from flask import Flask, request
import logging
import json
from random import choice
from Get_sheet import list_of_dicts

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

bad_image = '1030494/c85f3ac0666a9fca691b'
good_image = '997614/df0eec6ada760b40841e'

yes_list = ['да', 'давай', 'конечно', 'приступим', 'попробуем', 'ага']
no_list = ['нет', 'не хочу', 'не буду', 'не']

level = 2  # Сколько десяков задач, столько уровней


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
        res['response']['text'] = 'Привет! Давай знакомиться! Назови своё имя!'
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
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. ' \
                                      f'Тебе нужно будет помочь Хрюне сварить зелье. Только старайся не допускать ' \
                                      f'ошибок, иначе ничего не выйдет! Приступим?'
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
            if str(req['request']['original_utterance']).lower() in yes_list:
                if len(sessionStorage[user_id]['guessed_quest']) == 10:
                    res['response']['card'] = {}
                    res['response']['card']['type'] = 'BigImage'
                    res['response']['card']['title'] = f'' \
                                                       'Хрюня очень рад, что ты ему помог! ' \
                                                       'Зелье получилось просто замечательным!' \
                                                       'Перейдём на следующий уровень?'
                    res['response']['text'] = 'Хрюня очень рад, что ты ему помог! ' \
                                              'Зелье получилось просто замечательным!' \
                                              'Перейдём на следующий уровень?'
                    res['response']['card']['image_id'] = good_image
                    res['end_session'] = True
                else:
                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    sessionStorage[user_id]['level'] = 1
                    que = get_quest(list_of_dicts)
                    sessionStorage[user_id]['quest'] = que
                    play_game(res, req, sessionStorage[user_id]['quest'])
            elif str(req['request']['original_utterance']).lower() in no_list:
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
    if sessionStorage[user_id]['level'] != level + 1:
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
                res['response']['text'] = 'Правильно! Перейдём к следующему вопросу?'
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
                    res['response']['card'] = {}
                    res['response']['card']['type'] = 'BigImage'
                    res['response']['card']['title'] = f'Вы пытались. Это {quest["answer"]}. Может попробуем ещё разок?'
                    res['response']['text'] = f'Вы пытались. Это {quest["answer"]}. Может попробуем ещё разок?'
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
    else:
        res['response']['text'] = 'К сожалению, опросы пока кончились. Приходи позже'


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
