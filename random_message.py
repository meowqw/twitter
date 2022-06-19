import re
import random
import numpy


# формат сообщений
# <переменная, переменная> тело текста <переменная, переменная>
#


def message_processing(text):
    """Метод для генерации разных сообщений для отправки"""
    arr_message = []
    arr_section = (re.findall(r"\<(.*?)\>", text))
    stop_count = numpy.prod([int(len(i.split(','))) for i in arr_section])
    c = 0
    while c < stop_count:
        message = text
        for i in range(len(arr_section)):
            message = message.replace(f'<{arr_section[i]}>', random.choice(arr_section[i].split(', ')))
        if message not in arr_message:
            arr_message.append(message)
        else:
            c += -1

        c += 1
    return arr_message




