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
APICALL_COUNT = 0


def get_user_subscriptions(id, is_extended = 1):
    params = dict(
        access_token = TOKEN,
        v = V,
        user_id = id,
        extended = is_extended,
        fields = 'members_count'
    )

    global APICALL_COUNT
    APICALL_COUNT += 1
    print('Делаю запрос #{} к API VK'.format(APICALL_COUNT))

    subscriptions = requests.get('https://api.vk.com/method/groups.get', params).json()

    try:
        return subscriptions['response']['items']
    except KeyError:
        error_code = subscriptions['error']['error_code']
        print('Невозможно получить информацию с id{}. Код ошибки: {}'.format(id, error_code))

        return {'id': 0}


def get_user_friends(id):
    params = dict(
        token = TOKEN,
        v = V,
        user_id = id,
    )

    global APICALL_COUNT
    APICALL_COUNT += 1
    print('Делаю запрос #{} к API VK'.format(APICALL_COUNT))

    friends_ids = requests.get('https://api.vk.com/method/friends.get', params).json()

    return friends_ids['response']['items']


def get_unique_groups(source_group_list, friend_list):
    non_unique_groups = set()
    source_ids = set()
    unique_groups = source_ids
    calls_left = len(friend_list)

    for id in source_group_list:
        source_ids.add(id['id'])

    for id in friend_list:
        print('Осталось: {}'.format(calls_left))
        calls_left -= 1
        current_id_groups = set(get_user_subscriptions(id, 0))
        time.sleep(0.3)

        unique_groups = unique_groups - current_id_groups

    #возвращает список уникальных айди групп
    return unique_groups


user_subscriptions = get_user_subscriptions(ID)
user_friends = get_user_friends(ID)
unique_ids = get_unique_groups(user_subscriptions, user_friends)

user_subscriptions_unique = list(filter(lambda x: x['id'] in unique_ids, user_subscriptions))

output_file = []


for group in user_subscriptions_unique:
    output_file.append(dict(
        name = group['name'],
        gid = group['id'],
        members_count = group['members_count']
    )
    )

with open('result.json', 'w') as fp:
    json.dump(output_file, fp)


with open('result.json', 'r') as fp:
    data = json.load(fp)
