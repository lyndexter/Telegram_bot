import csv

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, Chat


class User:
    def __init__(self):
        api_id = 0#write id without quotes
        api_hash = "type your hash"
        phone = 'your phone number'
        client = TelegramClient(phone, api_id, api_hash)
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone)
            client.sign_in(phone, input('Enter the code: '))

        last_date = None
        chunk_size = 200
        self.result = client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))

        self.all_participants = {}
        chats = []
        groups = []
        chats.extend(self.result.chats)

        for chat in chats:
            try:
                # if chat.megagroup == True:
                # print(chat.title)
                if chat.participants_count < 35 and (
                        chat.participants_count is not None and type(
                    chat) == Chat and chat.participants_count > 0 or
                        chat.megagroup):
                    print(type(chat))
                    # print(chat.title)
                    # print(chat.participants_count)
                    groups.append(chat)
            except:
                continue

        for group in groups:
            # print("group:", group.title)
            self.all_participants[group.title] = client.get_participants(
                group, aggressive=True)
            # for user in self.all_participants[group.title]: print("   ",
            # user.username)

        # for participants in all_participants: print(participants)

    def get_participant(self, chat_title, sender_name):

        participants = self.all_participants[chat_title]
        user_names = [participant.username for participant in
                      participants if participant.username is not None]

        try:
            user_names.remove("goofybollbot")
            user_names.remove(sender_name)
        except:
            print("No some username")

        user_name_with_indetificator = ["@" + participant for participant in
                                        user_names if participant is not None]
        return user_name_with_indetificator


if __name__ == '__main__':
    user = User()
    # user.get_participant()
