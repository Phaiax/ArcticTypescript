# coding=utf8

from threading import Thread

import sublime
import os
import json

from ..utils import package_path, max_calls
from ..utils.fileutils import fn2k, is_ts

# ----------------------------------- ERROR HIGHTLIGHTER -------------------------------------- #

class ErrorsHighlighter(object):

    # Constants
    underline = sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_EMPTY_AS_OVERWRITE


    def __init__(self, project):
        self.project = project
        self._icon_paths()


    def _icon_paths(self):
        """ defines paths for icons """
        if os.name == 'nt':
            self.error_icon = ".."+os.path.join(package_path.split('Packages')[1], 'icons', 'bright-illegal')
            self.warning_icon = ".."+os.path.join(package_path.split('Packages')[1], 'icons', 'bright-warning')
        else:
            self.error_icon = "Packages"+os.path.join(package_path.split('Packages')[1], 'icons', 'bright-illegal.png')
            self.warning_icon = "Packages"+os.path.join(package_path.split('Packages')[1], 'icons', 'bright-warning.png')


    @max_calls(name='Errors.highlight')
    def highlight_all_open_files(self):
        """ update hightlights (red underline) in all files, using the errors in project """

        self.errors = {}

        # iterate through all open views, to remove all remaining outdated underlinings
        for window in sublime.windows():
            for view in window.views():
                if is_ts(view):
                    error_regions, warning_regions, error_texts = \
                        self.project.errors.tssjs_to_highlighter(view)

                    self.errors[fn2k(view.file_name())] = error_texts

                    # apply regions, even if empty (that will remove every highlight in that file)
                    view.add_regions('typescript-error' , error_regions , 'invalid' , self.error_icon, self.underline)
                    view.add_regions('typescript-warnings' , warning_regions , 'invalid' , self.warning_icon, self.underline)


    previously_error_under_cursor = False

    @max_calls(name='ErrorHighlighter.display_error_in_status_if_cursor')
    def display_error_in_status_if_cursor(self, view):
        """
            Displays the error message in the sublime status
            line if the cursor is above an error (in source code).
            For the click on the error list, see T3SVIEWS.ERROR.on_click()
        """
        try:
            error = self._get_error_at(view.sel()[0].begin(), view.file_name())
        except:
            # no selection in view
            return
        if error is not None:
            sublime.status_message(error)
            self.previously_error_under_cursor = True
        elif self.previously_error_under_cursor: # only clear once
            sublime.status_message('')
            self.previously_error_under_cursor = False


    def _get_error_at(self, pos, filename):
        """ Returns the error at pos in filename """
        if fn2k(filename) in self.errors:
            for (start, end), error_msg in self.errors[fn2k(filename)].items():
                if pos >= start and pos <= end:
                    return error_msg

        return None


