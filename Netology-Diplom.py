# coding: utf-8

import json
import requests
import time

with open('config.json', 'r') as f:
    data = json.load(f)
    V = data["V"]
    ID = data["ID"]
    TOKEN = data["TOKEN"]

URL = 'vk.com/'


def make_request(user_ids, method_name, fields='', is_extended=1):
    default = {'response': {'items': [{'id': 0}]}} #словарь по умолчанию, чтобы возвращать его в случае ошибок

    params = dict(
            access_token=TOKEN,
            v=V,
            extended=is_extended,
            fields=fields)

    for user_id in user_ids:
        params['user_id'] = user_id

        result = requests.get(
            'https://api.vk.com/method/{}'.format(method_name), params).json()

        while 'error' in result:
            error_code = result['error']['error_code']
            if error_code == 6:
                print('Сбавляю скорость')
                time.sleep(0.5)
                result = requests.get('https://api.vk.com/method/{}'.format(method_name), params).json()

            else:
                print('Невозможно подключиться к id{}. Код ошибки:{}'.format(user_id, error_code))
                return default

        else:
            return result['response']['items']


def get_unique_groups(source_group_list, friend_list):
    non_unique_groups = set()
    source_ids = set()
    unique_groups = source_ids
    calls_left = len(friend_list)

    for user_id in source_group_list:
        source_ids.add(user_id['id'])

    for user_id in friend_list:
        print('Делаю запрос к API VK id{}. Осталось: {}'.format(user_id, calls_left))
        calls_left -= 1
        current_id_groups = set(
            make_request([user_id], 'groups.get', is_extended=0))

        unique_groups = unique_groups - current_id_groups

    #возвращает список уникальных айди групп
    return unique_groups


user_subscriptions = make_request([ID], 'groups.get', 'members_count', 1)
user_friends = make_request([ID], 'friends.get')
unique_ids = get_unique_groups(user_subscriptions, user_friends)

user_subscriptions_unique = list(filter(lambda x: x['id'] in unique_ids, user_subscriptions))

output_file = []

for group in user_subscriptions_unique:
    output_file.append(
        dict(
            name=group['name'],
            gid=group['id'],
            members_count=group['members_count']))

with open('result.json', 'w') as fp:
    json.dump(output_file, fp)

with open('result.json', 'r') as fp:
    data = json.load(fp)
