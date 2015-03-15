# coding=utf8

import sublime
import sublime_plugin

import os

from .TsconfigLinter import check_tsconfig, show_lint_in_status
from .tsconfigglobexpand import expand_filesglob
from ..utils.CancelCommand import catch_CancelCommand, CancelCommand
from ..system.Project import opened_project_by_tsconfig

class TsconfigEventListener(sublime_plugin.EventListener):
    """ Listen to file events -> Activate TsconfigLinter.
        check_tsconfig immediately returns if file is no tsconfig.json """

    def on_activated_async(self, view):
        check_tsconfig(view)


    def on_load_async(self, view):
        check_tsconfig(view)


    def on_modified(self, view):
        check_tsconfig(view)


    def on_clone_async(self, view):
        check_tsconfig(view)


    @catch_CancelCommand
    def on_post_save_async(self, view):
        linter = check_tsconfig(view)
        linting_succeeded = expand_filesglob(linter)
        if linting_succeeded:
            project = opened_project_by_tsconfig(linter.file_name)
            if project:
                project.reopen_project()


    def on_selection_modified_async(self, view):
        show_lint_in_status(view)
