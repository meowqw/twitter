from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import LoginManager, login_user, login_required, current_user
import db
from UserLogin import UserLogin
from main import log_in, start_sending, start_auto_answer
from random_message import message_processing
from search_ import search_by_text
import os

app = Flask(__name__)
login_manager = LoginManager(app)
app.secret_key = 'secret'

# --------------------------
# АВТОРИЗАЦИЯ (AUTHORIZATION)
# --------------------------


# авторизация
@app.route('/login', methods=["POST", "GET"])
def login_auth():
    if request.method == "POST":
        user_log = db.get_user_by_login(request.form['login'])
        if user_log and (user_log[0][-1] == request.form['password']):
            user_login = UserLogin().create(user_log)
            login_user(user_login)
            return redirect(url_for('index'))
        flash('Ошибка')
    return render_template('login.html')


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDataBase(user_id, db)


# --------------------------
# АДМИНКА (ADMIN)
# --------------------------

@app.route('/admin')
@login_required
def admin():
    if db.get_user(current_user.get_id())[0][1] == 'admin':
        return render_template('admin.html', data=db.get_all_users())
    else:
        return render_template('index.html')


# управдение пользователями из админ панели (control users from admin panel)
@app.route('/users', methods=['POST', 'GET'])
@login_required
def users():
    if db.get_user(current_user.get_id())[0][1] == 'admin':
        if request.method == "GET":
            if list(request.args)[2] == 'del_user':
                print(request.args['del_user'])
                db.del_user(request.args['del_user'])
            elif list(request.args)[0] == 'login':
                if len(request.args['login']) != 0 and len(request.args['password']) != 0:
                    print(request.args['login'])
                    print(request.args['password'])
                    db.add_new_user([request.args['login'], request.args['password']])

    return render_template('admin.html', data=db.get_all_users())


# --------------------------
# АККАУНТЫ (ACCOUNTS)
# --------------------------

# Главная страница (main page)
@app.route('/')
@login_required
def index():
    data = db.select_all_data_account(db.get_user(current_user.get_id())[0][1])
    main = db.get_user(current_user.get_id())[0][1]
    return render_template('index.html', main_data=data, main=main)


# Страницы аккаунта (page account)
@app.route('/account/<string:login>/')
@login_required
def user(login):
    main = db.get_user(current_user.get_id())[0][1]
    return render_template('account.html', data=db.select_account_data(login),
                           main_data=db.select_all_data_account(main), main=main)


# переключатель автоответа и отправки (switch authoanswer and sending)
@app.route('/stop_auto', methods=['post', 'get'])
@login_required
def stop_auto():
    if request.method == 'GET':
        if list(request.args)[0] == 'log_auto':
            login = (request.args['log_auto'])
            db.switch_auto_answer_status(login, 0)
        elif list(request.args)[0] == 'log_send':
            login = (request.args['log_send'])
            db.switch_work_status(login, 0)
        elif list(request.args)[0] == 'del':
            login = (request.args['del'])

            # удаление из базы (del from base)
            db.del_account(login)
            db.del_chats(login)
            # удаление куков (del cookies)
            os.remove(f'./cookies/{login}')

    main = db.get_user(current_user.get_id())[0][1]
    return render_template('index.html',
                           main_data=db.select_all_data_account(main), main=main)


# Авторизация нового аккаунта (auth new account)
@app.route('/auth', methods=['post', 'get'])
@login_required
def auth():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        proxy = request.form.get('proxy')
        ua = request.form.get('user-agent')
        num = request.form.get('number')

        main = db.get_user(current_user.get_id())[0][1]
        # запуск функции (start function LOG_IN)
        status = log_in(login, password, 0, proxy, main, ua, num)

        # ОТСЛЕЖИВАНИЕ ОШИБОК АВТОРИЗАЦИИ (error tracking auth)
        if type(status) != list:
            print("[INFO]: authorization successful")
            return render_template('index.html',
                                   main_data=db.select_all_data_account(main), main=main)
        else:
            print('[ERROR]: Ошибка авторизации')
            return render_template('error.html', data=[login, 'Auth', 'Сheck the entered data (proxy and ua)',
                                                       'Exception: ' + status[1]],
                                   main_data=db.select_all_data_account(main), main=main)


# настройка акканута (setting account)
@app.route('/settings/<string:login>/', methods=["POST", "GET"])
@login_required
def settings(login):
    main = db.get_user(current_user.get_id())[0][1]
    data = db.select_account_data(login)
    return render_template('settings.html', main_data=db.select_all_data_account(main), main=main, data=data)


# замена прокси (replacement proxy)
@app.route('/settings/<string:login>/replacement_proxy', methods=["POST", "GET"])
@login_required
def replacement_proxy(login):
    main = db.get_user(current_user.get_id())[0][1]
    if request.method == 'POST':
        db.update_proxy(main, login, request.form['proxy'])

    data = db.select_account_data(login)
    return render_template('settings.html', main_data=db.select_all_data_account(main), main=main, data=data)


# замена ua (replacement ua)
@app.route('/settings/<string:login>/replacement_ua', methods=["POST", "GET"])
@login_required
def replacement_ua(login):
    main = db.get_user(current_user.get_id())[0][1]
    if request.method == 'POST':
        db.update_ua(main, login, request.form['user-agent'])

    data = db.select_account_data(login)
    return render_template('settings.html', main_data=db.select_all_data_account(main), main=main, data=data)


# --------------------------
# ИСТОРИЯ И ИЗБРАННОЕ (history and favorites)
# --------------------------


# Страница истории отправлений (page history message)
@app.route('/history/<string:login>')
@login_required
def history(login):
    data = db.select_chats(login)
    data = list(reversed(data))

    main = db.get_user(current_user.get_id())[0][1]

    if len(data) != 0:
        return render_template('history.html', data=data,
                               main_data=db.select_all_data_account(main), main=main)
    else:
        return render_template('index.html',
                               main_data=db.select_all_data_account(main), main=main)


# изменение статуса для избранного (replacement status for favorites)
@app.route('/addfavorites', methods=['post', 'get'])
@login_required
def add_favorites():
    main = db.get_user(current_user.get_id())[0][1]
    if request.method == 'GET':
        if list(request.args)[0] == 'add_favorites':
            login = request.args['add_favorites'].split(', ')[0]
            parent = request.args['add_favorites'].split(', ')[1]
            db.switch_favorites_status(parent, login, 1)

            return render_template('favorites.html', data=db.select_favorites(parent),
                                   main_data=db.select_all_data_account(main), main=main)

        elif list(request.args)[0] == 'del_favorites':
            login = request.args['del_favorites'].split(', ')[0]
            parent = request.args['del_favorites'].split(', ')[1]
            db.switch_favorites_status(parent, login, 0)

    return render_template('index.html',
                           main_data=db.select_all_data_account(main), main=main)


# Избранное (Favorites)
@app.route('/favorites/<string:login>')
@login_required
def favorites(login):
    data = db.select_chats(login)

    main = db.get_user(current_user.get_id())[0][1]
    if len(data) != 0:
        return render_template('favorites.html', data=db.select_favorites(login),
                               main_data=db.select_all_data_account(main), main=main)
    else:
        return render_template('index.html',
                               main_data=db.select_all_data_account(main), main=main)


# --------------------------
# АВТООТВЕТ (AUTOANSWER)
# --------------------------


# Страница автоответа (page autoanswer)
@app.route('/autoanswer/<string:login>/')
@login_required
def auto_answer(login):
    data = db.select_chats(login)

    main = db.get_user(current_user.get_id())[0][1]
    if len(data) != 0:
        return render_template('autoanswer.html', data=db.select_account_data(login),
                               main_data=db.select_all_data_account(main), main=main)
    else:
        return render_template('index.html',
                               main_data=db.select_all_data_account(main), main=main)


# # Старт автоответа (Start autoanswer)
# @app.route('/autoanswer/<string:login>/start_answer', methods=['post', 'get'])
# @login_required
# def auto_answer_start(login):
#     main = db.get_user(current_user.get_id())[0][1]
#     if request.method == 'POST':
#         text = request.form.get('text')
#         my_login = login
#         account_data = db.select_account_data(login)
#         my_password = account_data[0][2]
#         proxy = account_data[0][3]
#         ua = account_data[0][9]
#         num = account_data[0][11]
#         if text != '':
#             # строка сообщений (string message)
#             message_list = '[end]'.join(message_processing(text))
#             status = start_auto_answer(my_login, my_password, proxy, message_list,
#                                        main, ua, num)
#             # обработка ошибки (processing error)
#             if type(status) != list:
#                 return render_template('index.html',
#                                        main_data=db.select_all_data_account(main), main=main)
#             else:
#                 return render_template('error.html', data=[my_login, "Autoanswer",
#                                                            'Check if the proxy is working, '
#                                                            'restart autoanswer for this account',
#                                                            'Exception: ' + status[1]],
#                                        main_data=db.select_all_data_account(main), main=main)
#         else:
#             return render_template('index.html',
#                                    main_data=db.select_all_data_account(main), main=main)


# --------------------------
# ОТПРАВКА СООБЩЕНИЙ (MESSAGE SENDING)
# --------------------------


# генерация сообщений и их отправка (generation massage and sending)
@app.route('/account/<string:login>/generate', methods=['post', 'get'])
@login_required
def generate_messages(login):
    main = db.get_user(current_user.get_id())[0][1]
    # генерация (generation)
    if request.method == 'POST':
        if request.form.get('gen') == 'generate':
            login_u = request.form.get('login')
            text = request.form.get('text')
            my_login = login

            # изображения (image)
            file = request.files['f']
            if file.filename != "":
                file.save('/var/www/twitter/static/img/' + file.filename)

            if login_u != '' and text != '':

                # строка сообщений (string message)
                message_list = '[end]'.join(message_processing(text))

                # сохранение в базе (save in base)
                db.update_message_list(my_login, message_list)
                db.update_login_list(my_login, login_u)

                # сохранение пути img в бд (save path img in base)
                if file.filename != "":
                    db.update_img_account(main, login, 'static/img/' + file.filename)
                    img = 'img/' + file.filename
                else:
                    db.update_img_account(main, login, None)
                    img = None
            else:
                db.update_message_list(my_login, None)
                db.update_login_list(my_login, None)

            return render_template('account.html', data=db.select_account_data(login),
                                   main_data=db.select_all_data_account(main), main=main, images=img)

        # отправка (sending)
        elif request.form.get('send') == 'send':
            my_login = login
            account_data = db.select_account_data(login)
            my_password = account_data[0][2]
            proxy = account_data[0][3]
            ua = account_data[0][9]

            # запуск функции (start function START_SENDING)
            status = start_sending(my_login, my_password, 1, proxy, my_login, main, ua)

            if type(status) != list:
                return render_template('index.html',
                                       main_data=db.select_all_data_account(main), main=main)
            else:
                return render_template('error.html', data=[my_login, "Send message",
                                                           'Check if the proxy is working, '
                                                           'restart sending for this account',
                                                           'Exception: ' + status[1]],
                                       main_data=db.select_all_data_account(main), main=main)

        else:
            return render_template('index.html',
                                   main_data=db.select_all_data_account(main), main=main)


# --------------------------
# ПОИСК (SEARCH)
# --------------------------

# страница поиска (page search)
@app.route('/search')
@login_required
def search():
    main = db.get_user(current_user.get_id())[0][1]
    return render_template('search.html',
                           main=main)


# поиск (search)
@app.route('/start', methods=['post', 'get'])
@login_required
def start():
    if request.method == 'GET':
        if list(request.args)[0] == 'text':
            text = request.args['text']
            login = db.get_user(current_user.get_id())[0][1]

            chats = search_by_text(login, text)
            print(chats)

            if len(chats) == 0:
                chats = None

    return render_template('search.html', data=chats,
                           main=login)

# ------------------
# Общее избранное (MAIN FAVORITES)
# ------------------


# страница общего избранного (main favorites page)
@app.route('/main_favorites')
@login_required
def main_favorites():
    main = db.get_user(current_user.get_id())[0][1]
    # даныне для прогрузки (data to download)
    arr_account_data = db.select_all_data_account(main)
    account_login_arr = [i[1] for i in arr_account_data]

    # опредление родителя данных (definition father data)
    chats = []
    for a in account_login_arr:
        for c in db.select_chats(a):
            chats.append(c)

    data = []
    for i in chats:
        if i[7] == 1:
            data.append(i)

    return render_template('main_favorites.html',
                           data=data, main=main)


# изменение статуса для общего избранного (replacement status for main favorites)
@app.route('/addmainfavorites', methods=['post', 'get'])
@login_required
def add_main_favorites():
    main = db.get_user(current_user.get_id())[0][1]
    if request.method == 'GET':
        if list(request.args)[0] == 'add_main_favorites':
            login = request.args['add_main_favorites'].split(', ')[0]
            parent = request.args['add_main_favorites'].split(', ')[1]
            db.switch_main_favorites_status(parent, login, 1)
        elif list(request.args)[0] == 'del_main_favorites':
            login = request.args['del_main_favorites'].split(', ')[0]
            parent = request.args['del_main_favorites'].split(', ')[1]
            db.switch_main_favorites_status(parent, login, 0)

    # данные для прогрузки (data to download)
    arr_account_data = db.select_all_data_account(main)
    account_login_arr = [i[1] for i in arr_account_data]
    # опредление родителя данных (definition father data)
    chats = []
    for a in account_login_arr:
        for c in db.select_chats(a):
            chats.append(c)

    data = []
    for i in chats:
        if i[2] in account_login_arr and i[7] == 1:
            data.append(i)

    return render_template('main_favorites.html',
                           data=data, main=main)

# ------------------
# Лог ошибок (ERROR LOG)
# ------------------


# страница ошибок (error log page)
@app.route('/error_log')
@login_required
def error_log():
    main = db.get_user(current_user.get_id())[0][1]
    return render_template('error_log.html',
                           main=main, main_data=db.select_all_data_account(main), data=db.select_error(main))


if __name__ == "__main__":
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
