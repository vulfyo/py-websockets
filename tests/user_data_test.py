data = {1: {
    101: ['ws101_1', 'ws101_2'],
    102: ['ws102']},
    2: {
        201: ['ws201'],
        202: ['ws202']}
}

# new agency
data_new_agency = {'agency_id': 5, 'user_id': 501, 'ws': 'ws501_1'}
data_new_user = {'agency_id': 5, 'user_id': 502, 'ws': 'ws502_1'}
data_new_user_ws = {'agency_id': 5, 'user_id': 502, 'ws': 'ws502_2'}

print(data_new_agency)
print(data_new_user)
print(data_new_user_ws)

# add user
def add_user(data_new):
    if data_new['agency_id'] not in data:
        # new agency
        data.update({data_new['agency_id']: {data_new['user_id']: [data_new['ws']]}})
    elif 502 not in data[5]:
        # new user
        data[data_new['agency_id']][data_new['user_id']] = [data_new['ws']]
    elif 'ws502_2' not in data[5][502]:
        # new token
        data[data_new['agency_id']][data_new['user_id']].append('ws502_2')


add_user(data_new_agency)
add_user(data_new_user)
add_user(data_new_user_ws)
print()
print(data)


# remove user
def remove_user(websocket):
    for users_key, users_value in data.copy().items():
        for user_data_key, user_data_value in users_value.items():
            # if user have only one token
            if len(user_data_value) == 1:
                if user_data_value[0] == websocket:
                    if len(users_value) == 1:
                        # if was only one user in agency - remove all agency dict
                        del data[users_key]
                    else:
                        # if were many users
                        del users_value[user_data_key]
                    break
            else:
                # if many tokens are
                ws_to_remove = [x for x in user_data_value if x == websocket]
                if len(ws_to_remove):
                    user_data_value.remove(websocket)
                    break

# remove_user('ws502_2')
print(data)


# find ws by agency_id and user_id
# print(next(iter({v for k, v in data[1].items() if k == 101})))

dictionary = [v for k, v in data[1].items() if k == 102][0]
print(dictionary)

exit()

# find ws for all users in agency
[v for k, v in data[1].items()]