import telethon
import re
from telethon import TelegramClient
from natsort import natsorted
from asyncio import run
from datetime import datetime, timedelta
from config import *


list_a = []
list_tf = []
list_t = []
list_f = []
list_np = []

meta_list = [list_a, list_tf, list_t, list_f, list_np]
resulting_list = []
result = []

given_date_gmt = datetime.strptime(required_post_date, "%d.%m.%Y")
given_date_utc = given_date_gmt - timedelta(hours=3)
next_date_gmt = given_date_gmt + timedelta(days=1)
next_date_utc = given_date_utc + timedelta(days=1)


def list_fill(list_name, text):
    list_name.append(text.replace('\n', ' ').replace('\r', ''))


def sort_list(list_name):
    sorted_list = list(set(list_name))
    sorted_list = (natsorted(list_name, key=lambda y: y.lower()))
    return sorted_list


def find_post(client, offset_date, date_condition):
    print(f"> Перебираю записи")
    for message in client.iter_messages(source_chat, reverse=True, offset_date=offset_date):
        # if message.id == 1629:
        #     print(message)
        #     print(isinstance(message, telethon.tl.patched.Message))
        #     print(search_string_1 in message.message)
        #     print(date_condition.date() == (
        #             message.date + timedelta(hours=3)).date())
        #     print(date_condition.date())
        #     print((message.date + timedelta(hours=3)).date())
        if not message.message:
            print(f"==> Найдена запись с id {message.id} без параметра message! Пропускаю её")
            #print(f"==> Найдена запись с id {message} без параметра message! Пропускаю её")
            continue
        if isinstance(message,
                      telethon.tl.patched.Message) and (search_string_1 in message.message or search_string_1_alt in message.message) and not search_string_2 in message.message and date_condition.date() == (
                message.date + timedelta(hours=3)).date():
            print(f"==> Обнаружена запись с id {message.id} и датой {(message.date + timedelta(hours=3)).date()}. search_string_1={search_string_1 in message.message} и search_string_2={search_string_2 in message.message}")
            print(f"==> Подходит по параметрам, выхожу из цикла")
            found_post_id = message.id
            found_post_time = message.date
            next_post_time_default = found_post_time + timedelta(days=2)
            break
    return found_post_id, found_post_time, next_post_time_default


def form_list(given_list, formatted_cpt, text, resulting_list):
    list_sorted = sort_list(given_list)
    if len(list_sorted) > 0:
        resulting_list.append(f"==> {formatted_cpt} {text} ({len(list_sorted)}):")
        print(f"==> Найдено {len(list_sorted)} комментариев")
        for item_a in list_sorted:
            multiline_str_a = "\n".join(["{1}".format(i + 1, person_a) for i, person_a in enumerate(list_sorted)])
        resulting_list.append(multiline_str_a)
    else:
        print(f"==> Найдено 0 комментариев")
    return resulting_list


async def send_comments(name, api_id, api_hash, res):
    async with TelegramClient(name, api_id, api_hash) as client:
        for x in range(0, len(res)):
            if DEBUG_MODE:
                print(res[x])
            else:
                await client.send_message(entity=target_chat, message=res[x])


def messages_func(name, api_id, api_hash):
    with TelegramClient(name, api_id, api_hash) as client:
        print(f'Ищу запись за {given_date_gmt.date()}')
        current_post_id, current_post_time, next_post_time = find_post(client, given_date_utc, given_date_gmt)
        formatted_cpt = (current_post_time + timedelta(hours=3)).replace(tzinfo=None)
        print(f"Ищу запись за {next_date_gmt.date()}")
        next_post_time = find_post(client, given_date_utc, next_date_gmt)[1]
        print(f"Время завтрашней записи={next_post_time}")
        print(f"Записи найдены, теперь ищу комментарии")
        for message in client.iter_messages(source_chat, reply_to=int(current_post_id)):
            if len(message.message) > 0:
                if type(message.reply_to.reply_to_top_id) == int:
                    list_fill(list_np, message.message)
                else:
                    if re.search(r'\d', message.message):
                        if message.date < next_post_time:
                            list_fill(list_a, message.message)
                        else:
                            list_fill(list_t, message.message)
                    else:
                        if message.date < next_post_time:
                            list_fill(list_f, message.message)
                        else:
                            list_fill(list_tf, message.message)
        res = []
        print(f"> Отчеты от участников:")
        res = form_list(list_a, formatted_cpt, 'Отчёты от участников', res)
        print(f"> Отчеты, не прошедшие и по формату и по дате:")
        res = form_list(list_tf, formatted_cpt, 'Отчёты, не прошедшие и по формату и по дате', res)
        print(f"> Отчёты, не прошедшие по дате:")
        res = form_list(list_t, formatted_cpt, 'Отчёты, не прошедшие по дате', res)
        print(f"> Отчёты, не прошедшие по формату:")
        res = form_list(list_f, formatted_cpt, 'Отчёты, не прошедшие по формату', res)
        print(f"> Ответы на комментарии, а не на пост")
        res = form_list(list_np, formatted_cpt, 'Ответы на комментарии, а не на запись', res)
        return res


result = messages_func(name, api_id, api_hash)
print(f"Отсылаю результаты...")
run(send_comments(name, api_id, api_hash, result))
