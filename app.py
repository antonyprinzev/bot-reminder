# -*- coding: UTF-8 -*-.

import vk_api
from vk_api.vk_api import VkApiMethod
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
import time
from random import randrange
from copy import copy
import logging
import logging.config
from database import Timetable

# TODO database insert command
# TODO sending user reminding message
# TODO creating new remind/note
# TODO str 96

def process_text(text):
    """Leads the text to a single mind
    """
    text = text.replace(" ", "")  # Deletes from text all spaces
    text = text.lower()

    return text


class Bot(object):
    def __init__(self, vk_session):
        self.vk_session = vk_session
        self.vk = self.vk_session.get_api()

        self.vk_methods = VkApiMethod(self.vk_session)

        self.longpoll = VkLongPoll(self.vk_session)

        self.messages_callback = {
            "мои напоминания": self.show_timetable,
            "напомнить": self.plan_an_event
        }

        self.messages_answers = {
        }

        self.unknown_message = "Извини, я тебя не понимаю. Напиши мне" \
                               "'мои напоминания' или 'напомнить'"

        self.messages_callback = {process_text(key): value
                                  for key, value
                                  in self.messages_callback.items()}

        self.messages_answers = {process_text(key): value
                                 for key, value
                                 in self.messages_answers.items()}

        self.events_to_plan = []
        self.event_pattern = {"peer_id": False, "time": False,
                              "message_text": False}

    def listen(self):
        """Listens for events (incoming messages).
        """
        for event in self.longpoll.check():
            if event.type == VkEventType.MESSAGE_NEW and event.text \
                    and event.to_me:

                if process_text(event.text) in self.messages_answers:
                    self.send_message(event.peer_id,
                                      self.messages_answers[process_text(event.text)])

                elif process_text(event.text) in self.messages_callback:
                    self.messages_callback[process_text(event.text)]()

                else:
                    self.send_message(event.peer_id, self.unknown_message)

    def send_message(self, peer_id, msg_text):
        """Sends text message to user.
        """
        try:
            self.vk.messages.send(
                peer_id=peer_id,
                message=msg_text,
                random_id=randrange(0, 10**6)
            )

        except Exception as exception:
            self.emergency(exception)

    def plan_an_event(self, peer_id, message):
        """TODO plan: look at notebook"""
        for event in self.events_to_plan:
            if peer_id in event:
                break

        else:
            self.events_to_plan.append(copy(self.event_pattern))
            self.events_to_plan[-1]["peer_id"] = peer_id

    def add_event_to_timetable(self, time_, message):
        pass

    def show_timetable(self):
        pass

    def emergency(self, exception):
        """Shows, that an error was raised. Sends administrator a message,
        saves exception description to logs.
        """
        # TODO logger, admin id
        self.send_message(
            admin_id,
            "Всё сломалось! "
            "Вот тип ошибки: "
            "{err_type}\n Вот сообщение ошибки:{err_msg}".format(
             err_type=type(exception).__name__,
             err_msg=exception.__str__())
        )


class Manager(object):
    def __init__(self, vk_token):
        self.timetable = Timetable("databases/timetable.db")

        self.vk_session = vk_api.VkApi(token=vk_token)
        self.bot = Bot(self.vk_session)

        self.time_counter_min = False
        self.time_counter_sec = False

    def hold(self):
        """Main manager function, in which all processes are held.
        """
        # If hold function was called first time, fills time-counter variable
        if not self.time_counter_min or not self.time_counter_sec:
            self.time_counter_min = time.localtime().tm_min
            self.time_counter_sec = time.localtime().tm_sec

        if time.localtime().tm_sec - self.time_counter_sec:
            self.time_counter_sec = time.localtime().tm_sec

            self.bot.listen()

        # Refreshes time-counter variable if one minute passed
        if time.localtime().tm_min - self.time_counter_min >= 1:
            self.time_counter_min = time.localtime().tm_min

            # Checks if any event was planned
            events = self.check_timetable()

            if events:
                for event in events:
                    self.bot.send_message(event["peer_id"], event["msg_text"])

    def check_timetable(self):
        """ Checks if any event was planned for now.
        :return: Boolean variable
        """
        # Gets local time from computer
        time_now = time.localtime()
        time_now = list(map(str, [time_now.tm_mon, time_now.tm_day,
                                  time_now.tm_hour, time_now.tm_min]))
        time_now = ":".join(time_now)

        timetable = self.timetable.get_all()
        actual_events = []

        for event in timetable:
            if event["time"] == time_now:
                actual_events.append(event)

        return actual_events if len(actual_events) != 0 else False


if __name__ == "__main__":
    vk_token = "a2db7366b4c5e98be370a6cb6d209d03728de749346491ad445e7fd36273e98e37497e32c779ee56e6264"

    manager = Manager(vk_token)
    manager.hold()
