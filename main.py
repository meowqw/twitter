from seleniumwire import webdriver
import time
import os
import pickle
import random
from db import insert_account, insert_chats, select_chats, update_chats_data, switch_work_status, \
    update_message_list, \
    select_account_data, update_login_list, select_chat_parent_login, switch_auto_answer_status, update_img_account, \
    add_error_log

from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By

path_ = '/usr/lib/chromium-browser/chromedriver'
path_cookie = 'cookies/'


#
# -------------------------------------------------
# ОСНОВНОЕ (АВТОРИЗАЦИЯ, СОХРАНЕНИЕ И ЗАГРУЗКА COOKIES) (MAIN - AUTH, SAVE AND LOAD COOKIES)
# -------------------------------------------------


def save_cookies(driver, cookie):
    pickle.dump(driver.get_cookies(), open(path_cookie + cookie, 'wb'))


def load_cookies(driver, cookie):
    for i in pickle.load(open(path_cookie + cookie, 'rb')):
        driver.add_cookie(i)


def log_in(login, password, state, proxy, user, ua, num):
    """Лог пользователя и сохранение куков (login user and save cookies)"""

    login_user = login
    password_user = password

    error_status = 0
    error = ''
    try:
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={ua}')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')

        options_proxy = {
            'proxy': {
                'http': f'http://{proxy}',
                'https': f'https://{proxy}',
                'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
            }
        }

        driver = webdriver.Chrome(executable_path=path_, options=options,
                                  seleniumwire_options=options_proxy)

        driver.get("https://twitter.com/home?lang=en")
        time.sleep(5)

    except Exception as e:
        driver.quit()
        error_status = 1
        error = str(e)

    if error_status != 1:
        # проверка наличия куки файлов (checking for cookies)
        if os.path.isfile(path_cookie + login_user):
            load_cookies(driver, login_user)
            driver.refresh()
            time.sleep(10)
        else:
            try:
                # ввод логина (entering login)
                time.sleep(10)
                login_input = driver.find_element(
                    By.XPATH, "//input[@autocomplete='username']").send_keys(login_user)

                but_next = driver.find_elements(
                    By.XPATH, "//div[@role='button']")[-2].click()
                time.sleep(4)

                password_input = driver.find_element(
                    By.XPATH, "//input[@name='password']").send_keys(password_user)

                but_login = driver.find_element(
                    By.XPATH, "//div[@data-testid='LoginForm_Login_Button']").click()
                time.sleep(4)

                       # check phone field
                phone_input = driver.find_elements(
                    By.XPATH, "//input[@inputmode='tel']")
                if len(phone_input) > 0:
                    phone_input[0].send_keys(num)
                time.sleep(2)

                try:
                    but_next_log = driver.find_elements(
                        By.XPATH, "//div[@role='button']")[-1].click()
                except Exception as e:
                    pass

                time.sleep(10)
                check = driver.find_elements(
                    By.XPATH, "//div[@data-testid='tweetButtonInline']")
                if len(check) > 0:
                    print('Auth completed. Cookies saved')
                    save_cookies(driver, login_user)
                    insert_account(
                        (login_user, password_user, proxy, 0, user, ua, num))
                else:
                    error_status = 1

            except Exception as e:
                print(e)
                error_status = 1
            #     # МОБИЛЬНАЯ ВЕРСИЯ (MOBILE VER)
            #     # ввод логина (entering login)
            #     time.sleep(10)
            #     name = driver.find_element_by_xpath(
            #         "//input[@name='username']")
            #     name.send_keys(login_user)
            #     time.sleep(10)

            #     but = driver.find_elements_by_xpath("//div[@role='button']")[1]
            #     but.click()
            #     time.sleep(10)

            #     password = driver.find_element_by_xpath(
            #         "//input[@name='password']")
            #     password.send_keys(password_user)
            #     time.sleep(2)

            #     but = driver.find_elements_by_xpath("//div[@role='button']")[1]
            #     but.click()
            #     time.sleep(10)

            #     try:
            #         but_num = driver.find_element_by_xpath(
            #             "//input[@inputmode='tel']")
            #         but_num.send_keys(num)

            #         but = driver.find_elements_by_xpath(
            #             "//div[@role='button']")[1]
            #         but.click()
            #         time.sleep(10)
            #     except:
            #         pass

            #     # проверка на наличие элемента (checking element)
            #     try:
            #         driver.find_element_by_xpath("//header[@role='banner']")
            #         save_cookies(driver, login_user)
            #         # добавление в базу аккаунта (save in base)
            #         insert_account(
            #             (login_user, password_user, proxy, 0, user, ua, num))
            #     except Exception as e:
            #         error_status = 1
            #         error = str(e)

    # проверка статуса ошибки (check status error)
    if error_status != 1:
        # проверка нужно ли вернуть драйвер для дальнейшего использования (checking if the driver needs
        # to be returned for further use)
        if state == 0:
            driver.quit()
        else:
            return driver
    else:
        driver.quit()
        # запись в лог (save in log)
        add_error_log(['Auth', str(error), user, login])
        return [error_status, error]


#
# -------------------------------------------------
# ОТПРАВКА СООБЩЕНИЙ (MESSAGE SENDING)
# -------------------------------------------------


def check_work_status(log):
    """Проверка статуса отправки (check status sending)"""
    return int(select_account_data(log)[0][4])


def send_message(driver, users_list, text_message, parent, img):
    """Поиск пользователя и отправка сообщений (search user and send message)"""
    # замена статуса работы
    switch_work_status(parent, 1)

    check_send = 1

    c = 0
    while c < len(users_list) and check_send == 1:
        try:
            driver.get('https://twitter.com/messages/compose')
            time.sleep(random.randrange(12, 16))
            # поиск пользователя (search user)
            search = driver.find_element_by_xpath(
                "//input[@data-testid='searchPeople']")
            search.send_keys(users_list[c])

            time.sleep(random.randrange(12, 16))
            user = driver.find_elements_by_xpath(
                "//div[@data-testid='typeaheadResult']")[0]
            user.click()

            time.sleep(random.randrange(12, 16))
            button_next = driver.find_element_by_xpath(
                "//div[@data-testid='nextButton']")
            button_next.click()

            time.sleep(random.randrange(12, 16))

            # ОТПРАВКА ИЗОБРАЖЕНИЯ (SENDING IMG)
            if img is not None:
                img_input = driver.find_element_by_xpath(
                    "//input[@type='file']")
                img_input.send_keys(os.path.abspath(img))

                time.sleep(random.randrange(12, 16))

            # отправка сообщения (sending messaage)
            try:
                input_text_message = driver.find_element_by_xpath(
                    "//div[@role='textbox']")
            except:
                input_text_message = driver.find_element_by_xpath(
                    "//textarea[@data-testid='dmComposerTextInput']")

            # проверка кол-ва вариантов сообщений (checking the number of text variations)
            if c > len(text_message) - 1:
                input_text_message.send_keys(random.choice(text_message))
            else:
                input_text_message.send_keys(text_message[c])

            time.sleep(random.randrange(12, 16))

            send_button = driver.find_element_by_xpath(
                "//div[@data-testid='dmComposerSendButton']")
            send_button.click()

            time.sleep(random.randrange(20, 25))

            # сбор истории сообщений (collection history chat)
            message_list = driver.find_elements_by_xpath(
                "//div[@data-testid='messageEntry']")
            all_message = "[end]".join(
                [i.text for i in message_list])  # переписка с пользователем (chat)

            # прочая информация (other info)
            # ссылка на переписку (link)
            message_link = str(driver.current_url)

            # добавление в базу chats (add to base chats)
            #
            # есть ли в безе данные по данному логину (if login in bd)
            chats_data = select_chats(parent)

            # словарь login: send_status (dict)
            users = {}
            for i in chats_data:
                users[i[1]] = i[4]

            # чек статуса отправки (check status sending)
            if users_list[c] in list(users.keys()):
                # if users[find_user] == 0:
                update_chats_data(parent, users_list[c], all_message)
            else:
                send_status = 1
                insert_chats([users_list[c].replace('\r', ''),
                             parent, all_message, send_status, message_link])

            # УДАЛЕНИЕ ПРОЙДЕННОГО АКАКУНТА ИЗ МАССИВА И ЗАПИСЬ ДАННЫХ ОБРАТНО В БАЗУ
            # (DELETING THE PASSED ACCOUNT FROM THE ARRAY AND WRITING THE DATA BACK TO THE DATABASE)
            update_login_list(parent, "\n".join(users_list[c + 1:]))

            time.sleep(random.randrange(12, 16))
        except Exception as e:
            print(e)
            send_status = 0

            # + в базу чат с отправкой 0 (add to base chat with send equal to 0)
            message_link = str(driver.current_url)
            all_message = None
            insert_chats([users_list[c], parent, all_message,
                         send_status, message_link])
            pass

        # првоерка положения статуса (check status)
        check_send = check_work_status(parent)

        if c == len(users_list) - 1:
            pass
        else:
            time.sleep(random.randrange(3400, 3800))
        c += 1

    # замена статуса работы (replacement status working)
    switch_work_status(parent, 0)
    driver.quit()


def start_sending(login, password, state, proxy, parent, user, ua):
    """Запуск отправки сообщений (start send message)"""

    # получение данных аккаунта (select account data)
    account_data = select_account_data(login)

    # разделение сформированной строки разделителем(набор рандомных сообщений)
    # (splitting the formed string with a delimiter)
    message_list = account_data[0][5].split('[end]')
    users_list = account_data[0][6].split('\n')
    # номер (number)
    num = account_data[0][11]

    # изображение (img)
    img = account_data[0] = account_data[0][10]

    try:
        send_message(log_in(login, password, state, proxy, user,
                     ua, num), users_list, message_list, parent, img)

        update_message_list(login, None)
        update_login_list(login, None)
        update_img_account(parent, login, None)
    except Exception as e:
        switch_work_status(parent, 0)
        error_status = 1
        # запись в лог (save in log)
        add_error_log(['Sending message', str(e), user, login])
        return [error_status, str(e)]


#
# -------------------------------------------------
# АВТООТВЕТ (AUTOANSWER)
# -------------------------------------------------


def check_auto_work(log):
    """Проверка статуса автоответа (check status autoanswer)"""
    return int(select_account_data(log)[0][7])


def new_message_check(login, password, proxy, text_message, user, ua, num):
    """Проверка новых сообщений (check new message)"""
    try:
        driver = log_in(login, password, 1, proxy, user, ua, num)
        try:
            check_on = 1

            switch_auto_answer_status(login, 1)

            arr_user = []

            while check_on == 1:
                # пользователи которые ответили (login: [ссылка на чат, текст последнего сообщения])
                # users who replied
                arr_users_replied = {}

                driver.get('https://twitter.com/messages')
                time.sleep(random.randrange(12, 16))

                html = driver.page_source

                content = bs(html, 'html.parser')

                # все сообщения (all messages)
                message_list = content.find('div', {'aria-label': 'Timeline: Messages'}).find_all('div',
                                                                                                  {'role': 'tab'})

                # последнее сообщение в базе (last message in base)
                for i in message_list:
                    login_user = i.find('div', {'dir': 'ltr'}).find(
                        'span').text.replace('@', '')
                    text = i.find_all(
                        'div', {'dir': 'auto'})[-2].find('span').text

                    if text != 'You sent a photo':
                        chat_info = select_chat_parent_login(login, login_user)
                        if chat_info[0][3] is not None:
                            if chat_info[0][3].split('[end]')[-1] != text:
                                # print(text)
                                if login_user not in arr_user:
                                    arr_user.append(login_user)
                                    arr_users_replied[login_user] = [
                                        chat_info[0][5], text]

                if len(arr_users_replied) != 0:
                    # print(arr_users_replied)
                    # ЗАПУСК АВТООТВЕТА (START AUTOANSWER)

                    send_answer(driver, login, arr_users_replied, text_message)

                time.sleep(random.randrange(400, 1800))

                # чек (check)
                check_on = check_auto_work(login)
                # check_on = 0
                # switch_auto_answer_status(login, 0)

            driver.quit()

        except Exception as e:
            driver.quit()
            status_error = 1
            return status_error, e

    except Exception as e:
        status_error = 1
        return status_error, e


def send_answer(driver, parent, arr_users, text_message):
    """Автоответ (Autoanswer)"""

    # print(text_message)
    c = 0
    while c < len(arr_users):
        try:
            driver.get(arr_users[list(arr_users.keys())[c]][0])
            time.sleep(random.randrange(12, 14))

            # отправка сообщения (send message)
            try:
                input_text_message = driver.find_element_by_xpath(
                    "//div[@role='textbox']")
            except:
                input_text_message = driver.find_element_by_xpath(
                    "//textarea[@data-testid='dmComposerTextInput']")

            # проверка кол-ва вариантов сообщений (check the number of message options)
            if c > len(text_message) - 1:
                input_text_message.send_keys(random.choice(text_message))
            else:
                input_text_message.send_keys(text_message[c])

            time.sleep(random.randrange(12, 16))

            send_button = driver.find_element_by_xpath(
                "//div[@data-testid='dmComposerSendButton']")
            send_button.click()

            time.sleep(random.randrange(12, 16))

            # сбор истории сообщений (collection)
            message_list = driver.find_elements_by_xpath(
                "//div[@data-testid='messageEntry']")
            all_message = "[end]".join(
                [i.text for i in message_list])  # переписка с пользователем (chat)

            # прочая информация (other info)
            # ссылка на переписку (link)
            message_link = str(driver.current_url)

            # добавление в базу chats (save in base)
            #
            # есть ли в базе данные по данному логину (log in bd)
            chats_data = select_chats(parent)

            # словарь login: send_status
            users = {}
            for i in chats_data:
                users[i[1]] = i[4]

            # чек статуса отправки (check)
            if list(arr_users.keys())[c] in list(users.keys()):
                # if users[find_user] == 0:
                update_chats_data(parent, list(
                    arr_users.keys())[c], all_message)
            else:
                send_status = 1
                insert_chats([list(arr_users.keys())[c], parent,
                             all_message, send_status, message_link])

        except:
            pass

        time.sleep(random.randrange(900, 2000))

        c += 1


def start_auto_answer(login, password, proxy, text_message, user, ua, num):
    """Звпуск метода автоответа (Start autoanswer method)"""

    message_list = text_message.split('[end]')
    status = new_message_check(
        login, password, proxy, message_list, user, ua, num)
    if status[0] == 1:
        switch_auto_answer_status(login, 0)
        # запись в лог (save in log)
        add_error_log(['Autoanswer', str(status[1]), user, login])
        return [1, str(status[1])]
