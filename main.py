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

meta_list = [list_a, list_tf, list_t, list_f]
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
    for message in client.iter_messages(source_chat, reverse=True, offset_date=offset_date):
        if isinstance(message,
                      telethon.tl.patched.Message) and search_string_1 in message.message and not search_string_2 in message.message and date_condition.date() == (
                message.date + timedelta(hours=3)).date():
            found_post_id = message.id
            found_post_time = message.date
            next_post_time_default = found_post_time + timedelta(days=2)
            break
    return found_post_id, found_post_time, next_post_time_default


def form_list(given_list, formatted_cpt, text, resulting_list):
    list_sorted = sort_list(given_list)
    if len(list_sorted) > 0:
        resulting_list.append(f"==> {formatted_cpt} {text} ({len(list_sorted)}):")
        for item_a in list_sorted:
            multiline_str_a = "\n".join(["{1}".format(i + 1, person_a) for i, person_a in enumerate(list_sorted)])
        resulting_list.append(multiline_str_a)
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
        current_post_id, current_post_time, next_post_time = find_post(client, given_date_utc, given_date_gmt)
        formatted_cpt = (current_post_time + timedelta(hours=3)).replace(tzinfo=None)
        next_post_time = find_post(client, given_date_utc, next_date_gmt)[1]
        for message in client.iter_messages(source_chat, reply_to=int(current_post_id)):
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
        res = []
        res = form_list(list_a, formatted_cpt, 'Отчёты от участников', res)
        res = form_list(list_tf, formatted_cpt, 'Отчёты, не прошедшие и по формату и по дате', res)
        res = form_list(list_t, formatted_cpt, 'Отчёты, не прошедшие по дате', res)
        res = form_list(list_f, formatted_cpt, 'Отчёты, не прошедшие по формату', res)
        return res


result = messages_func(name, api_id, api_hash)
run(send_comments(name, api_id, api_hash, result))
