import telethon
import re
from telethon import TelegramClient
from natsort import natsorted
from asyncio import run
from datetime import datetime, timedelta

api_id = 'someid'
api_hash = 'somehash'
chat = 'somechat'
phone = 'somephone'
name = 'somename'

DEBUG_MODE = True

list_a = []
list_tf = []
list_t = []
list_f = []

meta_list = [list_a, list_tf, list_t, list_f]

#required_post_date = input('Введите дату в формате ДД.ММ.ГГГГ: ')
required_post_date = '10.09.2023'
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


async def messages_func(name, api_id, api_hash):
    async with TelegramClient(name, api_id, api_hash) as client:
        async for message in client.iter_messages(chat, reverse=True, offset_date=given_date_utc):
            if isinstance(message, telethon.tl.patched.Message) and 'search_string_1' in message.message and not 'search_string_2' in message.message and given_date_gmt.date() == (message.date + timedelta(hours=3)).date():
                current_post_id = message.id
                current_post_time = message.date
                next_post_time = current_post_time + timedelta(days=2)
                break
        async for message in client.iter_messages(chat, reverse=True, offset_date=given_date_utc):
            if isinstance(message, telethon.tl.patched.Message) and 'search_string_1' in message.message and not 'search_string_2' in message.message and next_date_gmt.date() == (message.date + timedelta(hours=3)).date():
                next_post_time = message.date
                break
        async for message in client.iter_messages(chat, reply_to=int(current_post_id)):
            if len(message.message) > 0:
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
        list_a_sorted = sort_list(list_a)
        list_tf_sorted = sort_list(list_tf)
        list_t_sorted = sort_list(list_t)
        list_f_sorted = sort_list(list_f)
        if len(list_a_sorted) > 0:
            if DEBUG_MODE:
                print(f"==> Отчёты за {(current_post_time + timedelta(hours=3)).replace(tzinfo=None)} от участников ({len(list_a_sorted)}):")
            else:
                await client.send_message(entity='target_channel', message=f" ==> Отчёты за {(current_post_time + timedelta(hours=3)).replace(tzinfo=None)} от участников ({len(list_a_sorted)}):")
            for item_a in list_a_sorted:
                multiline_str_a = "\n".join(["{1}".format(i + 1, person_a) for i, person_a in enumerate(list_a_sorted)])
            if DEBUG_MODE:
                print(multiline_str_a)
            else:
                await client.send_message(entity='target_channel', message=multiline_str_a)
        if len(list_tf_sorted) > 0:
            if DEBUG_MODE:
                print(f"==> Отчёты, не прошедшие и по формату и по дате ({len(list_tf_sorted)}):")
            else:
                await client.send_message(entity='target_channel', message=f" ==> Отчёты, не прошедшие и по формату и по дате ({len(list_tf_sorted)}):")
            for item_tf in list_tf_sorted:
                multiline_str_tf = "\n".join(["{1}".format(i + 1, person_tf) for i, person_tf in enumerate(list_tf_sorted)])
            if DEBUG_MODE:
                print(multiline_str_tf)
            else:
                await client.send_message(entity='target_channel', message=multiline_str_tf)
        if len(list_t_sorted) > 0:
            if DEBUG_MODE:
                print(f"==> Отчёты, не прошедшие по дате ({len(list_t_sorted)}):")
            else:
                await client.send_message(entity='target_channel', message=f" ==> Отчёты, не прошедшие по дате ({len(list_t_sorted)}):")
            for item_t in list_t_sorted:
                multiline_str_t = "\n".join(["{1}".format(i + 1, person_t) for i, person_t in enumerate(list_t_sorted)])
            if DEBUG_MODE:
                print(multiline_str_t)
            else:
                await client.send_message(entity='target_channel', message=multiline_str_t)
        if len(list_f_sorted) > 0:
            if DEBUG_MODE:
                print(f"==> Отчёты, не прошедшие по формату ({len(list_f_sorted)}):")
            else:
                await client.send_message(entity='target_channel', message=f" ==> Отчёты, не прошедшие по формату ({len(list_f_sorted)}):")
            for item_f in list_f_sorted:
                multiline_str_f = "\n".join(["{1}".format(i + 1, person_f) for i, person_f in enumerate(list_f_sorted)])
            if DEBUG_MODE:
                print(multiline_str_f)
            else:
                await client.send_message(entity='target_channel', message=multiline_str_f)
run(messages_func(name, api_id, api_hash))
