# coding=utf8

import sublime
import time

from .Base import Base
from ...utils import Debug, max_calls

class Error(Base):


    def __init__(self, t3sviews):
        super(Error, self).__init__('Typescript : Errors List', t3sviews)
        self.line_to_file = {}
        self.line_to_pos = {}
        self.text = ""


    # enable
    def enable(self, edit_token=None):
        super(Error, self).enable()
        if edit_token is not None:
            # set text if already known
            super(Error, self).set_text(edit_token, self.text)
            self.update_message()


    # SET TEXT
    def set_text(self, edit_token, project=None, text=None):
        """
            Sets the text to the text saved in project.errors.
        """
        # this will process the errors, even if the view is closed
        if project is not None:
            if not project.errors.failure:
                self.text = self.create_message()[1] + \
                    project.errors.text
                self.line_to_pos = project.errors.line_to_pos
                self.line_to_file = project.errors.line_to_file
            else:
                self.text = "\n\n\n%s" % project.errors.failure
                self.line_to_pos = {}
                self.line_to_file = {}
        elif text is not None:
            self.text = text
            self.line_to_pos = {}
            self.line_to_file = {}
        super(Error, self).set_text(edit_token, self.text)


    # ON CLICK
    @max_calls(name='Error.on_click')
    def on_click(self,line):
        if line in self.line_to_pos and line in self.line_to_file:
            view = sublime.active_window().open_file(self.line_to_file[line])
            self._focus_error_in_view(view, self.line_to_pos[line])


    def goto_error(self, n):
        try:
            line = list(self.line_to_file.items())[n][0]
        except:
            return
        view = sublime.active_window().open_file(self.line_to_file[line])
        self._focus_error_in_view(view, self.line_to_pos[line], set_cursor=True)


    def _focus_error_in_view(self, view, point, set_cursor=True):
        if view.is_loading():
            sublime.set_timeout(lambda: self._focus_error_in_view(view, point, set_cursor), 100)
            return
        else:
            a = view.text_point(*point[0])
            b = view.text_point(*point[1])
            region = sublime.Region(a,b)

            Debug('focus', 'Error click -> _focus_error_in_view %i, %s' % (view.id(), view.file_name()))
            view.window().focus_view(view)

            Debug('focus', "show_at_center, Region @pos %i, (%s -> %s)" % (region.begin(), point[0], point[1]))
            view.show_at_center(region)

            draw = sublime.DRAW_NO_FILL
            view.add_regions('typescript-error-hint', [region], 'invalid', 'dot')

            # redraw region in 50ms because selection modification will remove it
            sublime.set_timeout(lambda: view.add_regions('typescript-error-hint', [region], 'invalid', 'dot'), 50)

            if set_cursor:
                sel = view.sel()
                sel.clear()
                sel.add(a)


    def on_overtook_existing_view(self):
        """ empty view on plugin start """
        self._view_reference.run_command("typescript_error_panel_set_text",
                                         {"text": ""} )
        pass


    # MANAGING ERROR CALCULATION STATUS MESSAGES
    last_bounce_time = 0

    calculation_is_running = False
    execution_started_time = 0
    finished_time = 0
    last_execution_duration = 0


    def on_calculation_initiated(self):
        Debug('errorpanel', "Calc init")
        self.last_bounce_time = time.time()
        self.update_message()


    def on_calculation_replaced(self):
        Debug('errorpanel', "Calc replaced")
        self.last_bounce_time = time.time()
        self.update_message()


    def on_calculation_executing(self):
        Debug('errorpanel', "Calc executing")
        self.execution_started_time = time.time()
        self.calculation_is_running = True
        self.update_message()


    def on_calculation_finished(self):
        Debug('errorpanel', "Calc finished")
        self.finished_time = time.time()
        self.last_execution_duration = self.finished_time - self.execution_started_time
        self.calculation_is_running = False
        self.update_message()


    def is_unstarted_calculation_pending(self):
        return self.last_bounce_time > self.execution_started_time


    @max_calls()
    def update_message(self):
        """ update the message displayed on top of the error view """
        need_recall, msg = self.create_message()
        if need_recall:
            sublime.set_timeout(lambda: self.update_message(), 1000)
        ## calls set_error_calculation_status_message() with an edit_token
        if self._is_view_still_open():
            Debug('errorpanel', "Error view: %s %a: %s" % (self._view_reference.name(), self._view_reference.file_name(), msg[0:20]))
            self._view_reference.run_command('typescript_set_error_calculation_status_message', {"message": msg})


    def create_message(self):
        """ returns (need_recall, msg) """
        need_recall = False # only issue timeout to this function once

        msg = "//   "
        if self.last_execution_duration > 0: # there was a previous calculation

            # /"""""""""""""\
            msg += "/".ljust(int(self.last_execution_duration) + 1, "\"") + "\\"

            # indicate 'oldness' of calculation: (5s ago)
            oldness = int(time.time() - self.finished_time)
            if oldness < 10:
                msg += " (%is ago) " % oldness
                need_recall = True
            else:
                msg += " (long ago) "

        if self.calculation_is_running: # calculating: /""""""""
            calculation_time = time.time() - self.execution_started_time
            msg += "/".ljust(int(calculation_time) + 1, "\"")
            need_recall = True

        # after this calculation another calculation will be started: ...
        if self.is_unstarted_calculation_pending():
            msg += " ..."
        return (need_recall, msg)


    def set_error_calculation_status_message(self, edit_token, message):
        if not self._is_view_still_open():
            return
        Debug('errorpanel+', "message: %s" % (message))
        self.is_updating = True
        self._view_reference.set_read_only(False)
        self._view_reference.replace(edit_token, self._view_reference.full_line(0), message + "\n")
        self._view_reference.set_read_only(True)
        self.is_updating = False








