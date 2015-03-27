# coding=utf8

import sublime
from ..utils.debounce import debounce

class Message(object):

    messages =[]

    def show(self, message, hide=False, with_panel=True):
        self.messages = []
        self.messages.append(message)

        if with_panel:
            window = sublime.active_window()
            window.run_command("hide_overlay")
            window.show_quick_panel(self.messages, self.hide)
        sublime.status_message(message)

        if hide:
            debounce(self.hide, 1, 'message' + str(id(MESSAGE)))


    def repeat(self, message, with_panel=True):
        self.messages = []
        self.messages.append(message)


        if with_panel:
            window = sublime.active_window()
            window.run_command("hide_overlay")
            window.show_quick_panel(self.messages, self.hide)

        sublime.status_message(message)


    def hide(self,index=None):
        sublime.active_window().run_command("hide_overlay")
        sublime.status_message('')

# --------------------------------------- INITIALISATION -------------------------------------- #

MESSAGE = Message()