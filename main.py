from flask import Flask, render_template, url_for, request, redirect, jsonify, session, abort, g, flash
import os
from FDataBase import FDataBase
import sqlite3
import uuid, hashlib, random
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, session

# конфигурация
DATABASE = 'db.db'
DEBAG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SESSION_TYPE'] = 'redis'
app.config['SECRET_KEY'] = 'adfg2hjklry3uiopv5hiodh8fjdf'

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'db.db')))

menu = [{"name": "Главная", "url": "/"}, {"name": "Авторизация", "url": "/auto"},
        {"name": "Регистрация", "url": "/reg"}]
menuauth = [{"name": "Главная", "url": "/"}, {"name": "Профиль", "url": "/profile"}, {"name": "Выйти", "url": "/exit"}]


def connect():
    con = sqlite3.connect(app.config['DATABASE'])
    con.row_factory = sqlite3.Row
    return con


def create_db():
    db = connect()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect()
        return g.link_db


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)
    # print(dbase)


@app.route('/')
@app.route('/index')
def index():
    if (session.get('user')):
        return render_template('/index.html', menu=menuauth)
    else:
        return render_template('/index.html', menu=menu)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/auto')
def auto():
    return render_template('/auto.html', title='авторизация')


@app.route('/reg')
def reg():
    return render_template('/reg.html')


@app.route('/auto', methods=['POST', 'GET'])
def autos():
    session['err'] = ''
    session.modified = True
    session.permanent = True
    if request.method == 'POST':
        autos = dbase.SingIn(request.form['login'], request.form['psw'])
        if autos:
            session['user'] = dbase.SearchUser(request.form['login'])
            session['login'] = request.form['login']
            session.modified = True
            return redirect(url_for('index'))
        else:
            flash('такого пользователя нет')
            print(session['err'])
            print('все плохо')
    else:
        flash('руки крюки')
        print('руки крюки')
    return render_template('/auto.html')


@app.route('/reg', methods=['POST', 'GET'])
def regs():
    if request.method == 'POST':
        if len(request.form['login']) > 4 and len(request.form['psw']) > 4 and request.form['psw2'] == request.form[
            'psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['login'], hash)
            if res:
                session['user'] = dbase.SearchUser(request.form['login'])
                session['login'] = request.form['login']
                session.modified = True
                return redirect(url_for('index'))
            else:
                print('все плохо')
                return redirect(url_for('reg'))

        else:
            flash('логин и пароль должны быть больше 4 символов, пароли должны совпадать')
            return redirect(url_for('reg'))


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        if (len(request.form['search']) > 5):
            link = ''
            user = ''
            type = ''
            linnk = ''
            if session.get('user'):
                user = session['user']
                type = request.form['type']
            else:
                type = 'public'
                user = '0'
            if (len(request.form.getlist('chek')) > 0):
                linnk = request.base_url + request.form['psev']
            else:
                link = hashlib.md5(request.form['search'].encode()).hexdigest()[:random.randint(8, 12)]
                linnk = request.base_url + link
            res = dbase.addLink(request.form['search'], linnk, type, user)
            if res:
                flash(linnk)
                return redirect(url_for('index'))
            else:
                flash('не получилось')
                return 'не получилось'
        else:
            flash('ссылка и так короткая')
            return redirect(url_for('index', er='ссылка и так короткая'))
    else:
        flash('руки крюки')
        print('руки крюки')


@app.route('/exit')
def exit():
    session.clear()
    return redirect(url_for('index'))


@app.route('/create<link_name>')
def redirect_url(link_name):
    session.pop('link', None)
    lnk = dbase.searchLink(link_name)
    print(lnk)
    if lnk is None:
        return render_template('page404.html', title='страница не найдена'), 404
    else:
        type = lnk['type']
        if type == 'private':
            if session['user'] == lnk['id_user']:
                dbase.updateCount(lnk[0])
                print(lnk[0])
                return redirect(lnk['link'])
            else:
                flash('ссылка не ваша')
                return redirect(url_for('index'))
        elif type == 'ogr':
            if session.get('user'):
                dbase.updateCount(lnk[0])
                return redirect(lnk['link'])

            else:
                flash('сначала войдите')
                return redirect(url_for('index'))
        else:
            dbase.updateCount(lnk[0])
            return redirect(lnk['link'])


# @app.route('/index')
# def index():
#     db = get_db()
#     return render_template('index.html')

@app.route('/profile')
def prof():
    session.pop('link', None)
    links = dbase.userLinks(session['user'])
    return render_template('prof.html', links=links, menu=menuauth)


@app.route('/red', methods=['POST', 'GET'])
def red():
    if request.method == 'POST':
        link = request.form['red']
        linki = dbase.serLink(link)
        # print(linki)
        return render_template('red.html', linkk=linki)
    else:
        return 'dct plolo'


@app.route('/redact', methods=['POST', 'GET'])
def redact():
    if request.method == 'POST':
        link = request.form['r']
        type = request.form['type']
        psev = request.form['psev']
        dbase.updat(link, psev, type)
        return redirect(url_for('prof'))
    else:
        return 'fggh'


@app.route('/del', methods=['POST', 'GET'])
def dell():
    if request.method == 'POST':
        print(request.form['del'])
        dbase.delLink(request.form['del'])
        return redirect(url_for('prof'))
    else:
        return 'ffgghhd'


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='страница не найдена'), 404


if __name__ == "__main__":  # чисто для локалки, у сервера будет название этого файла
    app.run(debug=True)
