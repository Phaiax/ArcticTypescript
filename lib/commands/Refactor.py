# coding=utf8

from threading import Thread

import sublime
import os


from ..utils import Debug
from ..utils.fileutils import read_file, file_exists, fn2k


# ----------------------------------------- UTILS --------------------------------------- #

def show_output(window, line):
    PANEL.show(window)
    PANEL.update(line['output'])

def clear_panel(window):
    PANEL.clear(window)


# ##########################################################################
# ########################################## REFACTOR ######################
# ##########################################################################


#{'lineText': '        let total = 0;',
# 'file': '/home/daniel/.config/sublime-text-3/Packages/ArcticTypescript/tests/TDDTesting/main.ts',
# 'min': {'character': 13,
#         'line': 43},
# 'lim': {'character': 18,
#         'line': 43},
# 'ref': {'textSpan': {'start': 760,
#                      'length': 5},
#         'fileName': '/home/daniel/.config/sublime-text-3/Packages/ArcticTypescript/tests/TDDTesting/main.ts',
#         'isWriteAccess': True}}


class Refactor():

    def __init__(self, edit, project, refs, old_name, new_name):
        Thread.__init__(self)
        self.project = project
        self.refs = {r['ref'] for r in refs}
        self.old_name = old_name
        self.new_name = new_name
        self.edit_token = edit_token


    def start(self):
        self.run()

    def run(self):
        self.sort_by_file()
        Debug('refactor', self.refs_by_file)

        for (file_, refs_in) in self.refs_by_file.values():
            self.refactor_file(file_, refs_in)


    def sort_by_file(self):
        """ sort references by file """

        self.refs_by_file = {} # key is the fn2k'ed filename

        for ref in self.refs:
            file_ = fn2k(ref['file'])
            if file_ not in self.refs_by_file:
                self.refs_by_file[file_] = []

            self.refs_by_file[file_].append(ref)


    def refactor_file(self, file_name_keyed, refs_in):



        Debug('refactor', 'got here! :D')
        return


