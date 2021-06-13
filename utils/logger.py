import logging


class Logger:

    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %('
                                   'message)s')
        self.logger = logging.getLogger("MessageHandler")

    def log_message(self, message):
        user_name = message.from_user.username
        if message.from_user.username is None:
            user_name = "{} {}".format(message.from_user.first_name,
                                       message.from_user.last_name)

        self.logger.info(
            "{} - {} - {}: {}".format(message.chat.title, message.chat.id,
                                      user_name,
                                      message.text))
