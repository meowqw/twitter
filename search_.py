import db


def search_by_text(login, text):
    chats = []
    account_login_arr = [i[1] for i in db.select_all_data_account(login)]
    for i in account_login_arr:
        for chat in db.select_chats(i):
            if chat[3] is not None:
                if text in chat[3]:
                    chats.append(chat)

    return chats

