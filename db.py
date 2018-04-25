from datetime import datetime
from bson.dbref import DBRef
import pymongo


def get_coins(user):
    client = pymongo.MongoClient("mongo.yandexlyceum.ru", 27017)
    user = str(user)
    transactions = list(client.db.log.find())
    coins = []
    for coin0 in client.db.coins.find():
        coin, name = coin0['_id'], coin0['user']
        coin_log = list(filter(lambda x: x['coin'].id == coin, transactions))
        last_transaction = sorted(coin_log, key=lambda x: x['time'])[-1] if len(coin_log) > 0 else None
        coins += [coin] if \
            ((last_transaction['to'] == user) if last_transaction is not None else (name == user)) \
            else []
    return list(coins)


def is_coin_added(user, coin):
    client = pymongo.MongoClient("mongo.yandexlyceum.ru", 27017)
    return client.db.coins.find({"user": str(user), "string": coin}).count() > 0


def get_top():
    client = pymongo.MongoClient("mongo.yandexlyceum.ru", 27017)

    def f(x):
        x['total'] = len(get_coins(x['_id']))
        return x

    return sorted(map(f, list(client.db.coins.aggregate([{'$group': {'_id': '$user'}}]))),
                  key=lambda x: x['total'],
                  reverse=True)[:10]


def add_coin(user, coin):
    client = pymongo.MongoClient("mongo.yandexlyceum.ru", 27017)
    if not is_coin_added(user, coin):
        client.db.coins.insert_one(
            {
                "string": coin,
                "time": datetime.utcnow(),
                "user": user,
            }
        )


def transfer_coin(f, t):
    client = pymongo.MongoClient("mongo.yandexlyceum.ru", 27017)
    coin = get_coins(f)
    if len(coin) > 0:
        coin = coin[0]
        client.db.log.insert_one(
            {
                "coin": DBRef('coins', coin),
                "from": f,
                "to": t,
                "time": datetime.utcnow()
            }
        )
        return True
    return False
