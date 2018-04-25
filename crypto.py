from flask import render_template, request
from multiprocessing import Process
from flask import Flask
from hashlib import md5
from vk_wrapper import get_user
import db

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    res = []
    cnt = 0
    uid = None
    if request.method == "POST":
        hashes = request.form["hashes"].strip().split()
        for h in hashes:
            error = False
            if h.find('-') != -1:
                if md5(h.encode('utf8')).hexdigest()[:4] == '0000':
                    uid, rest = h.split('-', maxsplit=1)
                    if get_user(uid) is None:
                        error = True
                else:
                    error = True
            else:
                error = True
            cnt += not error
            res.append((h, error))
    for i in res:
        if not i[1]:
            Process(target=db.add_coin, args=(uid, i[0],)).start()
    return render_template('index.html',
                           res=res,
                           panel_type=("panel-success" if all(map(lambda x: not x[1], res)) else "panel-danger"))


@app.route('/wallet', methods=['POST'])
def wallet():
    try:
        if "wallet" in request.form.keys():
            wallet = request.form["wallet"].strip()
            if get_user(wallet) is None:
                raise ValueError("ID Invalid")
            coins = db.get_coins(wallet)
            if coins is None:
                raise ValueError("DBError")
            return render_template('wallet.html', wallet=wallet, coins=len(coins), res=-1)
        else:
            f, t = request.form["from"].strip(), request.form["to"].strip()
            res = db.transfer_coin(f, t)
            c = db.get_coins(f)
            return render_template('wallet.html', wallet=f, coins=len(c), res=res)
    except:
        return render_template('error.html')


@app.route('/wallet', methods=['GET'])
def wallet_get():
    try:
        return render_template('wallet.html', wallet="", coins=-1, res=-2)
    except:
        return render_template('error.html')


@app.route('/top', methods=['GET'])
def top():
    try:
        res = list(map(lambda x: (x[0], get_user(x[1]['_id'])['name'], x[1]['total']),
                       enumerate(db.get_top())))[:10]
        return render_template('top.html', data=res)
    except:
        return render_template('error.html')


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
