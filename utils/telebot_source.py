from telebot import types
import time, threading

interval = 2


def get_stop_button(data):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="Stop", callback_data=data))
    return markup


def send_message_and_clear(bot, chat_id, text):
    echo = bot.send_message(chat_id, text)

    thread = threading.Thread(target=clear_message, daemon=True,
                              args=(bot, chat_id, echo))
    thread.start()


def clear_message(bot, chat_id, echo):
    stop_event = threading.Event()
    end_time = time.perf_counter() + interval
    while not stop_event.wait(end_time - time.perf_counter()):
        bot.delete_message(chat_id=chat_id, message_id=echo.message_id)
        stop_event.set()
