# coding: utf-8

import json
import requests
import time

with open('config.json', 'r') as f:
    data = json.load(f)
    V = data["V"]
    ID = data["ID"]
    TOKEN = data["TOKEN"]

ERROR_CODE = 0

PARAMS = dict(access_token=TOKEN, v=V, extended=1, fields='')


def make_request(method_name, params):
    result = requests.get('https://api.vk.com/method/{}'.format(method_name),
                          params).json()

    while 'error' in result:
        ERROR_CODE = result['error']['error_code']
        if ERROR_CODE == 6:
            print('Сбавляю скорость')
            time.sleep(1)
            result = requests.get(
                'https://api.vk.com/method/{}'.format(method_name),
                params).json()

        else:
            print('Невозможно совершить операцию. Код ошибки:{}'.format(
                ERROR_CODE))
            return result  #вернет ответ сервера вк с описанием ошибки в виде json-словаря

    else:
        return result


def get_unique_groups(source_group_list, friend_list):

    PARAMS['extended'] = 0

    unique_groups = set()
    friends_ids = list()
    calls_left = len(friend_list)

    for group in source_group_list:
        unique_groups.add(group['id'])

    for friend in friend_list:
        friends_ids.append(friend['id'])

    for friend_id in friends_ids:
        PARAMS['user_id'] = friend_id
        print('Делаю запрос к API VK id{}. Осталось: {}'.format(
            friend_id, calls_left))
        calls_left -= 1

        try:
            current_id_groups = make_request('groups.get', PARAMS)['response']['items']
        except KeyError as e:
            current_id_groups = set()  #значение по умолчанию, возвращаемое в случае ошибок

        unique_groups = unique_groups - set(current_id_groups)

    #возвращает список уникальных айди групп
    return unique_groups


print('Получаю список групп и друзей...')

PARAMS['extended'] = 1
PARAMS['fields'] = 'members_count'
PARAMS['user_id'] = ID
user_subscriptions = make_request('groups.get', PARAMS)['response']['items']

PARAMS['extended'] = 0
user_friends = make_request('friends.get', PARAMS)['response']['items']
unique_ids = get_unique_groups(user_subscriptions, user_friends)

user_subscriptions_unique = list(
    filter(lambda x: x['id'] in unique_ids, user_subscriptions))

output_file = []

for group in user_subscriptions_unique:
    output_file.append(
        dict(
            name=group['name'],
            gid=group['id'],
            members_count=group['members_count']))

with open('result.json', 'w') as fp:
    json.dump(output_file, fp)
