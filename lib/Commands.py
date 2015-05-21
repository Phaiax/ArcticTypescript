# coding=utf8

from threading import Thread
import sublime
import sublime_plugin
import os
import re
import traceback

from .display.T3SViews import T3SVIEWS
from .display.Message import MESSAGE

from .system.Project import get_or_create_project_and_add_view, project_by_id
from .system.globals import OPENED_PROJECTS

from .utils.fileutils import read_file, fn2k
from .utils.viewutils import get_file_infos, get_content_of_view_at
from .utils.uiutils import get_prefix
from .utils.CancelCommand import catch_CancelCommand, CancelCommand
from .utils import Debug, max_calls


# ################################# AUTO COMPLETION ############################

class TypescriptCompletion(sublime_plugin.TextCommand):
    def run(self, edit):
        project = get_or_create_project_and_add_view(self.view)
        if project:
            project.completion.trigger(self.view, force_enable=True)


# ################################# RELOAD #####################################

class TypescriptReloadProject(sublime_plugin.TextCommand):

    def run(self, edit):
        project = get_or_create_project_and_add_view(self.view)
        if project:
            sublime.active_window().run_command('save_all')
            project.reopen_project()
            #project.tsserver.reload(lambda: )


# ################################# SHOW INFOS #################################

class TypescriptType(sublime_plugin.TextCommand):

    @catch_CancelCommand
    def run(self, edit):
        project = get_or_create_project_and_add_view(self.view)
        if project:
            project.assert_initialisation_finished()

            pos = self.view.sel()[0].begin()
            (_line, _col) = self.view.rowcol(pos)
            _view = self.view

            def async_react(types, filename, line, col):
                if types == None: return
                if 'kind' not in types: return

                # Only display type if cursor has not moved
                view = sublime.active_window().active_view()
                pos = view.sel()[0].begin()
                (_line, _col) = view.rowcol(pos)
                if col != _col or line != _line: return
                if view != _view: return

                kind = get_prefix(types['kind'])
                if types['docComment'] != '':
                    liste = types['docComment'].split('\n')+[types['type']]
                else:
                    liste = [types['type']]

                view.show_popup_menu(liste, None)

            # start async request
            project.tsserver.type(self.view.file_name(), _line, _col, callback=async_react)


# ################################# GO TO DEFINITION ###########################

class TypescriptDefinition(sublime_plugin.TextCommand):

    @catch_CancelCommand
    def run(self, edit):
        project = get_or_create_project_and_add_view(self.view)
        if project:
            project.assert_initialisation_finished()

            pos = self.view.sel()[0].begin()
            (_line, _col) = self.view.rowcol(pos)
            _view = self.view

            def async_react(definition, filename, line, col):
                if definition == None: return
                if 'file' not in definition: return

                # Only display type if cursor has not moved
                view = sublime.active_window().active_view()
                pos = view.sel()[0].begin()
                (_line, _col) = view.rowcol(pos)
                if col != _col or line != _line: return
                if view != _view: return

                view = sublime.active_window().open_file(definition['file'])
                self.open_view(view, definition)

            project.tsserver.definition(self.view.file_name(),
                                        _line, _col,
                                        callback=async_react)

    def open_view(self, view, definition):
        if view.is_loading():
            sublime.set_timeout(lambda: self.open_view(view, definition), 100)
            return
        else:
            start_line = definition['min']['line']
            end_line = definition['lim']['line']
            left = definition['min']['character']
            right = definition['lim']['character']

            a = view.text_point(start_line-1, left-1)
            b = view.text_point(end_line-1, right-1)
            region = sublime.Region(a, b)

            Debug('focus', 'Z focus view %i' % view.id())
            sublime.active_window().focus_view(view)
            view.show_at_center(region)

            sel = view.sel()
            sel.clear()
            sel.add(a)

            view.add_regions('typescript-definition', [region],
                             'comment', 'dot', sublime.DRAW_NO_FILL)


# ################################# REFACTORING ############################

class TypescriptRefactor(sublime_plugin.TextCommand):

    @catch_CancelCommand
    def run(self, edit_token):
        project = get_or_create_project_and_add_view(self.view)
        if project:
            project.assert_initialisation_finished()

            if not project.get_setting('enable_refactoring'):
                return

            # Position of activation.
            pos = self.view.sel()[0].begin()
            (line, col) = self.view.rowcol(pos)
            _view = self.view

            project.tsserver.references(self.view.file_name(), line, col, callback=self.async_react)

    @catch_CancelCommand
    def async_react(self, refs, filename, line, col):
        if refs is None or len(refs) == 0:
            return

        view = sublime.active_window().active_view()
        project = get_or_create_project_and_add_view(view)

        if not project:
            return

        if self.selection_has_changed(filename, line, col):
            return

        Debug('refactor', refs)
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


        refactor_member = self.get_entire_member_name(refs)
        if not refactor_member:
            return

        Debug('refactor', refactor_member)

        sublime.active_window().show_input_panel(
            'Refactoring %s (found %i times) to:' % (refactor_member, len(refs)),
            refactor_member,
            lambda new_name: sublime.run_command("typescript_apply_refactor",
                {"project":project, "refs":refs, "old_name":refactor_member, "new_name":new_name}), # require edit token
            None, # change
            None) # camcel
            ## TODO: keine Objekte ins run_command -> verweise bze hashes und die refs temporär im project abspeicern

    def selection_has_changed(self, orig_filename, orig_line, orig_col):
        """ Return True if active selection has changed """

        view = sublime.active_window().active_view()
        if orig_filename != view.file_name():
            return True

        current_pos = view.sel()[0].begin()
        (current_line, current_col) = view.rowcol(current_pos)

        if orig_col != current_col or orig_line != current_line:
            return True

        return False


    def get_entire_member_name(self, references):
        """ returns the complete member name of the refactored member """
        ref = references[0]
        return ref['lineText'][ref['min']['character']-1:ref['lim']['character']-1]



class TypescriptApplyRefactor(sublime_plugin.TextCommand):
    def run(self, edit_token, project, refs, old_name, new_name):
        project.do_refactor(refs, refactor_member, new_name, edit_token)


# ################################# OPEN OUTLINE PANEL #########################

# (via shortkey / public command)
class TypescriptStructure(sublime_plugin.TextCommand):
    """ this command opens and focus the structure/outline view """
    @catch_CancelCommand
    @max_calls(name='TypescriptStructure')
    def run(self, edit_token):
        project = get_or_create_project_and_add_view(self.view)
        if project:
            return # typescript tools dropped support for this
            Debug('structure', 'open view if not already open')
            project.assert_initialisation_finished()

            T3SVIEWS.OUTLINE.enable()
            T3SVIEWS.OUTLINE.bring_to_top(back_to=self.view)

            self.view.run_command('typescript_update_structure', {"force": True})


# ################################# REFRESH OUTLINE ############################

class TypescriptUpdateStructure(sublime_plugin.TextCommand):
    @catch_CancelCommand
    @max_calls(name='TypescriptUpdateStructure')
    def run(self, edit_token, force=False):
        project = get_or_create_project_and_add_view(self.view)
        if project:
            typescript_update_structure(self.view, force)


def typescript_update_structure(view, force):
    return
    project.assert_initialisation_finished()

    def async_react(members, filename, sender_view_id):
        ## members is the already json-decoded tss.js answer
        Debug('structure', 'STRUCTURE async_react for %s in start view %s, now view %s'
                % (filename, view.id(), sublime.active_window().active_view().id()) )

        if sublime.active_window().active_view().id() != sender_view_id or view.id() != sender_view_id:
            Debug('structure', 'STRUCTURE async_react canceled because of view change')
            return

        view.run_command('typescript_outline_view_set_text', {"members": members} )


    if T3SVIEWS.OUTLINE.is_active() and (force or not T3SVIEWS.OUTLINE.is_current_ts(view)):
        Debug('structure', 'STRUCTURE for %s in view %s, active view is %s'
            % (view.file_name(), view.id(), sublime.active_window().active_view().id()))
        TSS.structure(view.file_name(), view.id(), async_react)


# OPEN and WRITE TEXT TO OUTLINE VIEW
class TypescriptOutlineViewSetText(sublime_plugin.TextCommand):
    @max_calls(name='TypescriptOutlineViewSetText')
    def run(self, edit_token, members):
        try:
            Debug('structure', 'STRUCTURE update outline view panel')
            T3SVIEWS.OUTLINE.set_text(edit_token, members, self.view)
        except (Exception) as e:
            sublime.status_message("Outline panel : %s" % e)
            Debug('error', "Outline panel: %s" % e)


# ################################# ERROR PANEL ############################

# OPEN ERROR PANEL (via shortkey / public command)
class TypescriptErrorPanel(sublime_plugin.TextCommand):

    @catch_CancelCommand
    @max_calls(name='TypescriptErrorPanel')
    def run(self, edit_token):
        project = get_or_create_project_and_add_view(self.view)
        if project:
            project.assert_initialisation_finished()

            T3SVIEWS.ERROR.enable(edit_token)
            T3SVIEWS.ERROR.bring_to_top(back_to=self.view)

            project.errors.start_recalculation()


# ################################# REFRESH ERRORS ############################


class TypescriptErrorGoto(sublime_plugin.TextCommand):
    @max_calls(name='TypescriptErrorGoto')
    def run(self, edit_token, n):
        project = get_or_create_project_and_add_view(self.view)
        if project:
            Debug('goto', "%i" % n)
            T3SVIEWS.ERROR.goto_error(n)


class TypescriptErrorPanelSetText(sublime_plugin.TextCommand):
    @max_calls(name='TypescriptErrorPanelSetText')
    def run(self, edit_token, project_id=None, text=None):
        if project_by_id(project_id):
            try:
                T3SVIEWS.ERROR.set_text(edit_token,
                                        project=project_by_id(project_id))
            except (Exception) as e:
                msg = "Internal Arctic Typescript error in error panel : %s" % e
                sublime.status_message(msg)
                Debug('error', msg)
        else:
            T3SVIEWS.ERROR.set_text(edit_token, text=text)


class TypescriptSetErrorCalculationStatusMessage(sublime_plugin.TextCommand):
    @max_calls(name='TypescriptSetErrorCalculationStatusMessage')
    def run(self, edit_token, message):
        T3SVIEWS.ERROR.set_error_calculation_status_message(edit_token, message)


# ################################# COMPILE ####################################

class TypescriptBuild(sublime_plugin.TextCommand):

    @catch_CancelCommand
    def run(self, edit, characters):
        project = get_or_create_project_and_add_view(self.view)
        if project:
            filename = self.view.file_name()

            if not project.get_setting('activate_build_system'):
                Debug('notify', "Build system is disabled.")
                return

            project.assert_initialisation_finished()

            self.window = sublime.active_window()
            if characters != False:
                self.window.run_command('save')

            project.compile_once(self.window, filename)


class TypescriptTerminateBuilds(sublime_plugin.TextCommand):

    @catch_CancelCommand
    def run(self, edit):
        for project in OPENED_PROJECTS.values():
            if project.compiler is not None:
                project.compiler.kill()


# ################################# COMPILE RESULT VIEW ########################

class TypescriptBuildView(sublime_plugin.TextCommand):

    def run(self, edit_token, project_id, display_file):
        project = project_by_id(project_id)
        if project:
            if not project.get_setting('show_build_file'):
                return

            T3SVIEWS.COMPILE.enable()
            T3SVIEWS.COMPILE.bring_to_top(back_to=self.view)

            if os.path.exists(display_file):
                data = read_file(display_file)
                T3SVIEWS.COMPILE.set_text(edit_token, data)
            else:
                T3SVIEWS.COMPILE.set_text(edit_token, display_file)

