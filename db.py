from mysql.connector import connect, Error

HOST = 'localhost'
PORT = '3306'
USER = 'user'
PASSWORD = '2110'
DB_NAME = 'twitter'




def create_table_account(con):
    create_account = """
       CREATE TABLE account(
           id int AUTO_INCREMENT primary key,
           login varchar(300) NOT NULL ,
           password varchar(300) NOT NULL ,
           proxy varchar(300) default NULL NULL,
           work_status int default 0 NOT NULL ,
           message_list text default NULL NULL,
           login_list text default NULL NULL,
           work_status_autoanswer int default 0 NOT NULL ,
           user varchar(100) NOT NULL,
           ua varchar(500) NOT NULL,
           img varchar(300) default NULL NULL,
           number varchar(300) default NULL NULL
       )
       """
    with con.cursor() as cursor:
        cursor.execute(create_account)
        con.commit()


def create_table_chats(con):
    create_chats = """
           CREATE TABLE chats(
               id int AUTO_INCREMENT primary key,
               login varchar(300),
               parent varchar(300),
               all_message text default NULL NULL ,
               send_status int default 0 NOT NULL ,
               chat_link varchar(500),
               favorit_status int default 0 NOT NULL, 
               main_favorit_status int default 0 NOT NULL
           )
           """
    with con.cursor() as cursor:
        cursor.execute(create_chats)
        con.commit()


def create_table_users(con):
    create_users = """
           CREATE TABLE users(
               id int AUTO_INCREMENT primary key,
                login varchar(300) NOT NULL,
                password varchar(300) NOT NULL
           )
           """
    with con.cursor() as cursor:
        cursor.execute(create_users)
        con.commit()


def create_table_errors(con):
    create_errors = """
           CREATE TABLE error_log(
               id int AUTO_INCREMENT primary key,
                type varchar(300),
                text text,
                time datetime default current_timestamp,
                user varchar(300),
                login varchar(300)
                
           )
           """
    with con.cursor() as cursor:
        cursor.execute(create_errors)
        con.commit()



# добавление данных в базу
def insert_data_account(con, data):
    insert_reviewers_query = """INSERT INTO account
    (login, password, proxy, work_status, user, ua, number)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    with con.cursor() as cursor:
        cursor.execute(insert_reviewers_query,
                       data)
        con.commit()


def insert_data_chats(con, data):
    insert_data = """INSERT INTO chats
    (login, parent, all_message, send_status, chat_link)
    VALUES (%s, %s, %s, %s, %s)
    """
    with con.cursor() as cursor:
        cursor.execute(insert_data,
                       data)
        con.commit()


# подключение к базе и вызов функции записи
def insert_account(data):
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            insert_data_account(connection, data)
    except Error as e:
        print(e)

# with connect(
#         host=HOST,
#         user=USER,
#         port=PORT,
#         password=PASSWORD,
#         database=DB_NAME,
# ) as connection:
#     with connection.cursor() as cursor:
#         try:
#             create_table_chats(connection)
#             create_table_account(connection)
#             create_table_users(connection)
#             create_table_errors(connection)
#         except:
#             print('sd')



def insert_chats(data):
    """Добавленте данных в чаты"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            insert_data_chats(connection, data)
    except Error as e:
        print(e)


def select_data_account(con, user):
    """Вывод списка аккаунтов"""
    select_query = "SELECT * FROM account WHERE user=%s"
    with con.cursor() as cursor:
        cursor.execute(select_query, (user,))
        return cursor.fetchall()


def select_chats(parent):
    """Вывод данных акканта"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            select = """SELECT * FROM chats WHERE parent=%s"""
            with connection.cursor() as cursor:
                cursor.execute(select, (parent,))
                result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def select_all_data_account(user):
    """Вывод данных"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            return select_data_account(connection, user)
    except Error as e:
        print(e)


def select_account_data(log):
    """Вывод данных акканта"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            select = """SELECT * FROM account WHERE login=%s"""
            with connection.cursor() as cursor:
                cursor.execute(select, (log,))
                result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def update_chats_data(parent, login, history):
    """Обновление данных в chats"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            update = """UPDATE chats SET all_message=%s WHERE parent=%s and login=%s"""
            with connection.cursor() as cursor:
                cursor.execute(update, (history, parent, login))
                connection.commit()
    except Error as e:
        print(e)


def switch_work_status(login, status):
    """Смена статуса работы отправки сообщений"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            update = """UPDATE account SET work_status=%s WHERE login=%s"""
            with connection.cursor() as cursor:
                cursor.execute(update, (status, login))
                connection.commit()
    except Error as e:
        print(e)


def switch_auto_answer_status(login, status):
    """Смена статуса работы автоответа"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            update = """UPDATE account SET work_status_autoanswer=%s WHERE login=%s"""
            with connection.cursor() as cursor:
                cursor.execute(update, (status, login))
                connection.commit()
    except Error as e:
        print(e)


def update_message_list(login, message_list):
    """Обновление списка сгенерированных сообщений"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            update = """UPDATE account SET message_list=%s WHERE login=%s"""
            with connection.cursor() as cursor:
                cursor.execute(update, (message_list, login))
                connection.commit()
    except Error as e:
        print(e)


def update_login_list(login, login_list):
    """Обновление списка сгенерированных сообщений"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            update = """UPDATE account SET login_list=%s WHERE login=%s"""
            with connection.cursor() as cursor:
                cursor.execute(update, (login_list, login))
                connection.commit()
    except Error as e:
        print(e)


def select_chat_parent_login(parent, login):
    """Вывод данных чата по логину и родителю"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            select = """SELECT * FROM chats WHERE parent=%s and login=%s"""
            with connection.cursor() as cursor:
                cursor.execute(select, (parent, login))
                result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def select_favorites(parent):
    """Вывод данных для избранного"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            select = """SELECT * FROM chats WHERE parent=%s and favorit_status=1"""
            with connection.cursor() as cursor:
                cursor.execute(select, (parent,))
                result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def switch_favorites_status(parent, login, status):
    """Изменение статуса избранного"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            update = """UPDATE chats SET favorit_status=%s WHERE login=%s and parent=%s"""
            with connection.cursor() as cursor:
                cursor.execute(update, (status, login, parent))
                connection.commit()
    except Error as e:
        print(e)


def del_account(login):
    """Удаление аккаунта"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            delete = """DELETE FROM account WHERE login=%s"""
            with connection.cursor() as cursor:
                cursor.execute(delete, (login,))
                connection.commit()
    except Error as e:
        print(e)


def del_chats(parent):
    """Удаление чатов при удалении аккаунта"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            delete = """DELETE FROM chats WHERE parent=%s"""
            with connection.cursor() as cursor:
                cursor.execute(delete, (parent,))
                connection.commit()
    except Error as e:
        print(e)
# ------------------------------------
# АВТОРИЗАЦИЯ
# ------------------------------------


def get_user(user_id):
    """Данные о пользователе по id"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            select = """SELECT * FROM users WHERE id=%s LIMIT 1"""
            with connection.cursor() as cursor:
                cursor.execute(select, (user_id,))
                result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def get_user_by_login(login):
    """Данные о пользователе по логину"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            select = """SELECT * FROM users WHERE login=%s LIMIT 1"""
            with connection.cursor() as cursor:
                cursor.execute(select, (login,))
                result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def get_all_users():
    """Данные о всех пользователях"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            select = """SELECT * FROM users"""
            with connection.cursor() as cursor:
                cursor.execute(select)
                result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def insert_users(con, data):
    insert_data = """INSERT INTO users
    (login, password)
    VALUES (%s, %s)
    """
    with con.cursor() as cursor:
        cursor.execute(insert_data,
                       data)
        con.commit()


def add_new_user(data):
    """Добавить нового пользователя"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            insert_users(connection, data)
    except Error as e:
        print(e)


def del_user(login):
    """Удалить пользователя"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            delete = """DELETE FROM users WHERE login=%s"""
            with connection.cursor() as cursor:
                cursor.execute(delete, (login,))
                connection.commit()
    except Error as e:
        print(e)


def switch_main_favorites_status(parent, login, status):
    """Изменение статуса общего избранного"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            update = """UPDATE chats SET main_favorit_status=%s WHERE login=%s and parent=%s"""
            with connection.cursor() as cursor:
                cursor.execute(update, (status, login, parent))
                connection.commit()
    except Error as e:
        print(e)


def update_proxy(user, login, proxy):
    """Замена прокси"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            update = """UPDATE account SET proxy=%s WHERE login=%s and user=%s"""
            with connection.cursor() as cursor:
                cursor.execute(update, (proxy, login, user))
                connection.commit()
    except Error as e:
        print(e)


def update_ua(user, login, ua):
    """Замена user agent"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            update = """UPDATE account SET ua=%s WHERE login=%s and user=%s"""
            with connection.cursor() as cursor:
                cursor.execute(update, (ua, login, user))
                connection.commit()
    except Error as e:
        print(e)


def update_img_account(user, login, img):
    """Замена img"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            update = """UPDATE account SET img=%s WHERE login=%s and user=%s"""
            with connection.cursor() as cursor:
                cursor.execute(update, (img, login, user))
                connection.commit()
    except Error as e:
        print(e)


def add_error_log(data):
    """Добавление в лог ошибок пользователя"""
    insert_data = """INSERT INTO error_log
        (type, text, user, login)
        VALUES (%s, %s, %s, %s)
        """
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(insert_data,
                               data)
                connection.commit()

    except Error as e:
        print(e)


def select_error(user):
    """Вывод ошибок"""
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
        ) as connection:
            select = """SELECT * FROM error_log WHERE user=%s"""
            with connection.cursor() as cursor:
                cursor.execute(select, (user,))
                result = cursor.fetchall()
            return result
    except Error as e:
        print(e)
