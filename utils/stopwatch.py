import time, threading
from utils import telebot_source

interval = 5


class StopWatch:

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.echo = None
        self.stop_event = threading.Event()
        self.start_time = None
        self.markup = telebot_source.get_stop_button("stop_stopwatch")

    def start(self):
        if self.start_time is not None:
            telebot_source.send_message_and_clear(self.bot, self.chat_id,
                                                  "stopwatch is running now "
                                                  "stop it to start new")
            return

        self.start_time = time.perf_counter()
        self.echo = self.bot.send_message(self.chat_id, "Пройшло часу 0 s",
                                          reply_markup=self.markup)
        thread = threading.Thread(target=self.set_interval, daemon=True)
        thread.start()

    def set_interval(self):
        next_time = time.perf_counter() + interval
        while not self.stop_event.wait(next_time - time.perf_counter()):
            next_time += interval
            self.echo = self.bot.edit_message_text("Пройшло часу {:.0f} "
                                                   "s".format(
                time.perf_counter() - self.start_time), self.chat_id,
                self.echo.message_id,
                reply_markup=self.markup)

    def stop(self):
        self.stop_event.set()
        elapsed_time = time.perf_counter() - self.start_time
        self.bot.edit_message_text(
            'Пройшло часу: {:.2f} s'.format(elapsed_time),
            self.chat_id,
            self.echo.message_id)
        self.start_time = None
