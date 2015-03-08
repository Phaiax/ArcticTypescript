# coding=utf8

from subprocess import Popen, PIPE
from threading import Thread
try:
    from queue import Queue
except ImportError:
    from Queue import Queue

import sublime
import os
import json

from ..utils import package_path, Debug
from ..utils.osutils import get_kwargs
from ..utils.pathutils import default_tsc_path, default_node_path, expand_variables

from ..display.Panel import PANEL

# ----------------------------------------- UTILS --------------------------------------- #




# --------------------------------------- COMPILER -------------------------------------- #

class Compiler(Thread):

    def __init__(self, project, window_for_panel, triggered_for_file):
        self.triggered_for_file = triggered_for_file
        self.window_for_panel = window_for_panel
        self.project = project
        self.p = None
        self.cancel_build = False
        Thread.__init__(self)

    def run(self):
        if self.p is not None:
            Debug('error', "Only use Compiler Object once!")

        self.cwd = os.path.abspath(self.project.tsconfigdir)
        node_path, compile_cmd = self._make_commandline()
        self.kwargs = get_kwargs()

        self._prepare_pre_and_post_commands()

        PANEL.clear(self.window_for_panel)

        if self.post_pre_authorized:
            for pre_cmd in self.pre_processing_commands:
                pre_cmd = expand_variables(str(pre_cmd), self.project, use_cache=True)
                self._run_command(pre_cmd, shell=True)

        self._run_command(compile_cmd)

        self.project.show_compiled_file()

        if self.post_pre_authorized:
            for post_cmd in self.post_processing_commands:
                post_cmd = expand_variables(str(post_cmd), self.project, use_cache=True)
                self._run_command(post_cmd, shell=True)

        self._show_output("<<< Finished")

    def _prepare_pre_and_post_commands(self):
        # PRE-Processing-commands
        self.pre_processing_commands = self.project.get_setting("pre_processing_commands", use_cache=True)
        self.post_processing_commands = self.project.get_setting("post_processing_commands", use_cache=True)

        if isinstance(self.pre_processing_commands, str):
            self.pre_processing_commands = [self.pre_processing_commands]
        if isinstance(self.post_processing_commands, str):
            self.post_processing_commands = [self.post_processing_commands]

        self._authorize_shell_execution()


    def _authorize_shell_execution(self):
        total_commands = self.pre_processing_commands + self.post_processing_commands

        if self.cancel_build:
            self.post_pre_authorized = False
            return

        if self.project.authorized_commands == total_commands:
            self.post_pre_authorized = True
            Debug('build', 'Post/Pre allowed before')
            return

        if self.project.forbidden_commands == total_commands:
            self.post_pre_authorized = False
            Debug('build', 'Post/Pre forbidden before')
            return

        # commands have changed, so ask again

        messages = [
            ['Security alert: Allow execution of the following commands IN A SHELL?'] + total_commands,
            ['> YES'],
            ['> NO, only build']
        ]

        max_lines = 0
        for m in messages:
            max_lines = max(max_lines, len(m))
        for m in messages:
            while len(m) < max_lines:
                m.append('')

        self.answer_pending = Queue()

        def on_done(i):
            Debug('build', 'User answered: %i' % i)
            if i == 1: # YES
                self.project.authorized_commands = total_commands
                self.project.forbidden_commands = []
            elif i == 2: # NO
                self.project.authorized_commands = []
                self.project.forbidden_commands = total_commands
            else:
                Debug('build', '> Cancel Build')
                self.cancel_build = True
            self.answer_pending.put("")

        Debug('build', 'Ask for authoritation of post/pre commands')
        sublime.active_window().show_quick_panel(messages, on_done)
        # Wait until user has choosen
        self.answer_pending.get() # blocking until answered
        Debug('build', 'Continue with Compiler Thread')

        self._authorize_shell_execution() # check again, this time it should not ask


    def _run_command(self, cmd, shell=False):
        if self.cancel_build:
            return
        Debug('build', 'BUILD EXECUTE: %s' % str(cmd))
        if isinstance(cmd, str):
            self._show_output(">>> %s\n" % cmd.replace("\n", "\\n"))
        else:
            self._show_output(">>> %s\n" % cmd)

        self.p = Popen(cmd, stdin=PIPE, stdout=PIPE, cwd=self.cwd, shell=shell, **self.kwargs)
        self._run_forward_compiler_output()


    def _make_commandline(self):
        """ generates the commandline to start either tss.js or tsserver.js,
            depending on the project settings """
        node_path = default_node_path(self.project.get_setting('node_path'))
        tsc_path = default_tsc_path(self.project.get_setting('tsc_path'),
                                    self.project)

        cmdline = [node_path, tsc_path, "--project", "."]

        return node_path, cmdline


    def _run_forward_compiler_output(self):
        for line in iter(self.p.stdout.readline, b''):
                Debug('build+', 'BUILD RESULTS: %s' % line)
                try:
                    line = line.decode('UTF-8')
                    line = line.replace('\r', '')
                except ValueError as v:
                    break
                self._show_output(line)
        Debug('build+', 'BUILD RESULTS: all lined read')
        self.p.stdout.close()
        self._show_output("\n")


    def kill(self):
        self.cancel_build = True
        if self.p:
            try:
                Debug('build+', 'BUILD: Kill process!')
                self.p.terminate()
                self.p.kill()
                self._show_output("<<< Process has been terminated. Waiting for Compiler Thread to finish\n")
                self.p.communicate() # release readline() block
                Debug('build+', 'BUILD: process killed')
            except Exception as e:
                Debug('error', "Failure while killing compiler thread: %s" % e)


    def _show_output(self, line):
        PANEL.show(self.window_for_panel)
        PANEL.update(line)
        #window.run_command('typescript_build_view',
        #                   {"filename":line['output'].replace('[end]','\n')})

