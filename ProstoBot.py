import re

from datetime import date

import json
import telebot
from telebot import types

from utils import telebot_source
from utils.User import User
from utils.logger import Logger
from utils.source import *
from utils.stopwatch import StopWatch
from utils.timer import Timer

bot_token = 'bot_tocken'
bot = telebot.TeleBot(bot_token)

logger = Logger()
timers = {}
stopwatches = {}
echo = None
result = []
user = User()


@bot.message_handler(commands=['start'])
def start_message(message):
    logger.log_message(message)

    print(message)
    bot.send_message(message.chat.id,
                     'Ти думаєш я тупий бот\nЯ і без тебе вмію запускатись')


@bot.message_handler(commands=['stop'])
def stop_message(message):
    logger.log_message(message)

    bot.send_message(message.chat.id,
                     'Ти пробував мене зупинити ' + u'\U0001F621')


@bot.message_handler(commands=['help'])
def help_message(message):
    logger.log_message(message)

    bot.send_message(message.chat.id, 'Тут мав бути текст ' + u'\U0001F605')


@bot.message_handler(commands=['stopwatch'])
def create_stopwatch(message):
    logger.log_message(message)

    bot.delete_message(message.chat.id, message.message_id)

    if message.chat.id not in stopwatches:
        stopwatch = StopWatch(bot, message.chat.id)
        stopwatches[message.chat.id] = stopwatch
    else:
        stopwatch = stopwatches[message.chat.id]

    stopwatch.start()


@bot.message_handler(commands=['timer'])
def create_timer(message):
    logger.log_message(message)

    bot.delete_message(message.chat.id, message.message_id)

    global echo

    if message.chat.id not in timers \
            or timers[message.chat.id].end_time is None:

        echo = bot.send_message(message.chat.id,
                                'Введіть час для таймера в секундах')
        timer = Timer(bot, message.chat.id)
        timers[message.chat.id] = timer
        bot.register_next_step_handler(message=echo, callback=start_timer)
    else:
        telebot_source.send_message_and_clear(bot, message.chat.id,
                                              "timer is running now stop "
                                              "it to start new")


def start_timer(message):
    logger.log_message(message)

    global echo
    bot.delete_message(echo.chat.id, echo.message_id)
    bot.delete_message(message.chat.id, message.message_id)

    timer = timers[message.chat.id]
    try:
        time_interval = int(message.text)
        timer.start(time_interval)
    except ValueError:
        echo = bot.send_message(message.chat.id,
                                'Ви ввели неправильний час. Введіть час для '
                                'таймера')
        bot.register_next_step_handler(message=echo, callback=start_timer)


@bot.message_handler(commands=['zoom'])
def get_zoom_links(message):
    logger.log_message(message)

    source_links = read_csv("resource/zoom.csv")
    links, key = get_today_links(source_links)
    markup = create_markup(links)

    bot.send_message(message.chat.id, "Lectures", reply_markup=markup)
    if key:
        bot.send_message(message.chat.id, "{}: {}".format(key[0], key[1]))


@bot.message_handler(commands=['links'])
def get_links(message):
    logger.log_message(message)

    links = read_csv("resource/source.csv")
    markup = types.InlineKeyboardMarkup()
    for link in links:
        markup.add(types.InlineKeyboardButton(text=link[0],
                                              callback_data=link[0],
                                              url=link[1]))

    bot.send_message(message.chat.id, "Links", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    logger.log_message(message)
    pattern_word = lambda word: re.compile(
        '(([^а-яА-Я]|^){word}([^а-яА-Я]|$))'.format(word=word), re.IGNORECASE)
    pattern_all = re.compile('@all')
    pattern_zoom = re.compile('_zoom_')

    if pattern_all.search(message.text):
        user_names = user.get_participant(message.chat.title,
                                          message.from_user.username)
        bot.send_message(message.chat.id, " ".join(user_names))

    if pattern_zoom.search(message.text):
        links = read_csv("resource/zoom.csv")
        markup = create_markup(links)
        bot.send_message(message.chat.id, "Lectures", reply_markup=markup)

    # swear_list = read_csv("resource/swear_dict.csv")
    # for game in swear_list:
    #     if re.search(pattern_word(game[0]), message.text):
    #         bot.delete_message(message.chat.id, message.message_id)
    #         bot.restrict_chat_member(message.chat.id, message.from_user.id,
    #                                  until_date=time.time() + 60)
    #
    # game_list = read_csv("resource/games.csv")
    # for game in game_list:
    #     if re.search(pattern_word(game[0]), message.text):
    #         bot.send_message(message.chat.id,
    #                          "Йой що знову {}?\nЦе вже надоїло".format(
    #                          game[0]))


def create_markup(links):
    markup = types.InlineKeyboardMarkup()
    for index_link in range(0, len(links), 2):
        if len(links) > index_link + 1:
            markup.row(types.InlineKeyboardButton(text=links[index_link][0],
                                                  url=links[index_link][1],
                                                  callback_data="ddd"),
                       types.InlineKeyboardButton(
                           text=links[index_link + 1][0],
                           url=links[index_link + 1][1], callback_data="ddd"))
        else:
            markup.row(types.InlineKeyboardButton(text=links[index_link][0],
                                                  url=links[index_link][1],
                                                  callback_data="ddd"))

    return markup


def get_today_links(source_links):
    links = []
    today = date.today().weekday()
    key = ""

    for link in source_links:
        try:
            for index in range(2, len(link)):
                if int(link[index]) == today:
                    links.append(link)
        except:
            try:
                if links[-1][0] == link[0]:
                    key = (link[0], link[index])
                # links.append([link[index], ""])
                continue
            except:
                continue

    return links, key


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    call.message.from_user = call.from_user
    call.message.text = call.data
    logger.log_message(call.message)

    if call.data == "stop_stopwatch":
        if call.message.chat.id not in stopwatches:
            return
        stopwatch = stopwatches[call.message.chat.id]
        stopwatch.stop()
        stopwatches.pop(call.message.chat.id)
    elif call.data == "stop_timer":
        if call.message.chat.id not in timers:
            return
        timer = timers[call.message.chat.id]
        timer.stop()
        timers.pop(call.message.chat.id)


bot.polling(none_stop=True, interval=0)
