import time, threading
from utils import telebot_source

interval = 5


class Timer:

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.echo = None
        self.stop_event = threading.Event()
        self.end_time = None
        self.time_interval = None
        self.markup = telebot_source.get_stop_button("stop_timer")

    def start(self, time_interval):
        if self.end_time is not None:
            self.bot.send_message(self.chat_id,
                                  "timer is running now stop it to start new")
            return
        self.time_interval = time_interval
        self.end_time = time.perf_counter() + time_interval
        self.echo = self.bot.send_message(self.chat_id,
                                          "Залишилось часу {} s".format(
                                              time_interval),
                                          reply_markup=self.markup)

        thread = threading.Thread(target=self.set_interval, daemon=True)
        thread.start()
        thread_stop = threading.Thread(target=self.check_end_time,
                                       daemon=True)
        thread_stop.start()

    def set_interval(self):
        next_time = time.perf_counter() + interval
        while not self.stop_event.wait(next_time - time.perf_counter()):
            next_time += interval
            self.bot.edit_message_text(chat_id=self.chat_id,
                                       message_id=self.echo.message_id,
                                       text="Залишилось часу {:.0f} s".format((
                                               self.end_time -
                                               time.perf_counter())),
                                       reply_markup=self.markup)

    def check_end_time(self):
        while not self.stop_event.wait(self.end_time - time.perf_counter()):
            self.bot.edit_message_text(chat_id=self.chat_id,
                                       message_id=self.echo.message_id,
                                       text="Час вийшов")
            self.stop_event.set()
        self.end_time = None

    def stop(self):
        self.stop_event.set()
        elapsed_time = time.perf_counter() - self.end_time + self.time_interval
        self.bot.edit_message_text(
            "Ви зупинили таймер, пройшло часу {:.2f}".format(
                elapsed_time), self.chat_id, self.echo.message_id)
        self.end_time = None
