import vk

session = vk.Session()
api = vk.API(session)

cache = {}


def get_user(id):
    if id in cache:
        return cache[id]
    res = api.users.get(user_ids=id, v='1')
    if len(res) > 0:
        res = res[0]
        res['name'] = res['first_name'] + ' ' + res['last_name']
        cache[id] = res
        return res
    else:
        return None
