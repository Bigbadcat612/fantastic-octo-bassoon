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

def make_request(method_name, params):
    base_params = dict(
    access_token=TOKEN,
    v=V,
    )

    params.update(base_params)
    result = requests.get('https://api.vk.com/method/{}'.format(method_name), params).json()

    while 'error' in result:
        ERROR_CODE = result['error']['error_code']
        if ERROR_CODE == 6:
            print('Сбавляю скорость')
            time.sleep(1)
            result = requests.get('https://api.vk.com/method/{}'.format(method_name), params).json()

        else:
            print('Невозможно совершить операцию. Код ошибки:{}'.format(ERROR_CODE))
            return result  #вернет ответ сервера вк с описанием ошибки в виде json-словаря

    else:
        return result


def get_unique_groups(source_group_list, friend_list):
    unique_groups = set()
    calls_left = len(friend_list)

    for group in source_group_list:
        unique_groups.add(group['id'])

    for friend_id in friend_list:
        friend_groups_params = dict(
            user_id = friend_id
            )
        print('Делаю запрос к API VK id{}. Осталось: {}'.format(friend_id, calls_left))
        calls_left -= 1

        try:
            current_id_groups = make_request('groups.get', friend_groups_params)['response']['items']
        except KeyError as e:
            current_id_groups = set()  #значение по умолчанию, возвращаемое в случае ошибок

        unique_groups = unique_groups - set(current_id_groups)

    #возвращает список уникальных айди групп
    return unique_groups


print('Получаю список групп и друзей...')

user_params = dict(
    user_id = ID,
    fields = 'members_count',
    extended = 1
    )
user_subscriptions = make_request('groups.get', user_params)['response']['items']

user_friends_params = dict(
    user_id = ID
    )
user_friends = make_request('friends.get', user_friends_params)['response']['items']
print(user_friends)
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
