# coding=utf8

import sublime
import sublime_plugin

import os

from .display.T3SViews import T3SVIEWS

from .system.Project import OpenedProject, get_or_create_project_and_add_view

from .utils import Debug, max_calls
from .utils.viewutils import run_command_on_any_ts_view
from .utils.fileutils import file_exists
from .utils.CancelCommand import catch_CancelCommand, CancelCommand





# ----------------------------------------- LISTENERS ---------------------------------------- #

class TypescriptEventListener(sublime_plugin.EventListener):

    # CLOSE FILE
    @max_calls(name='Listener.on_close')
    def on_close_async(self, view):
        project = get_or_create_project_and_add_view(view, wizzard=False)
        if project:
            project.close(view)


    # FILE ACTIVATED
    @max_calls()
    @catch_CancelCommand
    def on_activated_async(self, view):
        project = get_or_create_project_and_add_view(view)
        #if project:
        #    if T3SVIEWS.COMPILE.is_active():
        #        project.show_compiled_file()


    # ON CLONED FILE
    @max_calls()
    @catch_CancelCommand
    def on_clone_async(self, view):
        project = get_or_create_project_and_add_view(view)
        #if project:
            #if T3SVIEWS.COMPILE.is_active():
            #    project.show_compiled_file()


    # ON SAVE
    @max_calls()
    @catch_CancelCommand
    def on_post_save_async(self, view):
        project = get_or_create_project_and_add_view(view)
        if project and project.is_initialized():
            project.tsserver.update(view)

            # Old: it has tested, if file is already tracked by the tsserver
            #filename, num_lines, content = get_file_infos(view)
            #if LISTE.has(filename):
            #    TSS.update(filename, num_lines, content)
            #    FILES.update(filename, num_lines, content, True)

            view.run_command('typescript_update_structure', {"force": True})
            project.errors.start_recalculation()

            if project.get_setting('build_on_save'):
                sublime.active_window().run_command('typescript_build',
                                                    {"characters": False})


    # ON CLICK
    @max_calls(name='listener.on_selection_modified')
    @catch_CancelCommand
    def on_selection_modified_async(self, view):
        project = get_or_create_project_and_add_view(view)
        if project and project.is_initialized():
            project.highlighter.display_error_in_status_if_cursor(view)
            view.erase_regions('typescript-definition')
            view.erase_regions('typescript-error-hint')


    # ON VIEW MODIFIED
    @max_calls()
    @catch_CancelCommand
    def on_modified_async(self, view):
        project = get_or_create_project_and_add_view(view)
        if project and project.is_initialized():


            project.tsserver.update(view)

            # Old: it has tested, if file is already tracked by the tsserver
            #if LISTE.has(filename):
            #    TSS.update(filename, num_lines, content)
            #    FILES.update(filename, num_lines, content)

            # Stucture update (removed) TODO: replace with navbar stuff
            #view.run_command('typescript_update_structure', {"force": True})
            #typescript_update_structure(view, True)

            project.completion.trigger(view)

            if not project.get_setting('error_on_save_only'):
                project.errors.start_recalculation()




    # ON QUERY COMPLETION
    @catch_CancelCommand
    def on_query_completions(self, view, prefix, locations):
        project = get_or_create_project_and_add_view(view)
        if project and project.is_initialized():
            pos = view.sel()[0].begin()
            (line, col) = view.rowcol(pos)
            Debug('autocomplete', "on_query_completions(), sublime wants to see the results, cursor currently at %i , %i (enabled: %s, items: %i)" % (line+1, col+1, project.completion.enabled_for['viewid'], len(project.completion.get_list()) ) )

            if project.completion.enabled_for['viewid'] == view.id():
                project.completion.enabled_for['viewid'] = -1 # receive only once
                return (project.completion.get_list(), sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)


    # ON QUERY CONTEXT (execute commandy only on opened .ts files)
    @catch_CancelCommand
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "ArcticTypescript":
            project = get_or_create_project_and_add_view(view)
            if project and project.is_initialized():
                return True
        if key == "ArcticTypescriptBuild":
            project = get_or_create_project_and_add_view(view)
            if project and project.is_initialized():
                if project.get_setting('activate_build_system'):
                    return True
        return False


