# coding=utf8

import sublime
import json
import re

from ..utils import max_calls, Debug
from ..utils.fileutils import fn2k


# --------------------------------------- ERRORS -------------------------------------- #

class Errors(object):
    def __init__(self, project):
        self.project = project
        self.lasterrors = []
        self.message = "" # contains exception message if an error occured
        pass

    @max_calls()
    def start_recalculation(self):
        self.project.tsserver.errors(self.on_results)

    @max_calls()
    def on_results(self, errors):
        """ this is the callback from the async process if new errors have been calculated """
        try:
            self.failure = ""
            self.lasterrors = json.loads(errors)
            print(self.lasterrors)
            if type(self.lasterrors) is not list:
                raise Warning("tss.js internal error: %s" % errors)
            self._provide_better_explanations_for_some_errors()
            self._tssjs_to_errorview()

        except BaseException as e: # Also catches JSON exceptions
            self.lasterrors = []
            self.failure = "%s" % e
            Debug('error', 'Internal ArcticTypescript error during show_errors: %s (Exception Message: %s)' % (errors, e))

        self.project.highlighter.highlight_all_open_files()
        sublime.active_window().run_command('typescript_error_panel_set_text',
                                            { "project_id": self.project.id } )


    def _provide_better_explanations_for_some_errors(self):

        # do not use : inside of explanation
        additions = {1148 : '// What to do? Either use /// <reference path="x.ts" /> instead of import x = require("x");, or switch to external modules (Add the compilerOptions module="amd"|"commonjs" and out="some/builddir" to tsconfig.json). Restart ArcticTypescript or sublime.'}

        for e in self.lasterrors:
            for code, add in additions.items():
                if e['code'] == code:
                    e['text'] = e['text'] + ' ' + add


    def _tssjs_to_errorview(self):
        """
            Takes the de-jsoned output of the tss.js error command and creates the content for the error view.
            It also creates a relation between each line in the error view and the file and position of the error.

            Sets    self.text
                    self.line_to_file[line] = filename
                    self.line_to_pos[line] = ((l,c),(l,c))

        """
        line_to_file = {}
        line_to_pos = {}
        text = []

        previous_file = ''
        line = 0

        for e in self.lasterrors:
            filename = e['file'].split('/')[-1]
            if previous_file != filename:
                text.append("\n\nOn File : %s \n" % filename)
                line += 3
                previous_file = filename

            text.append("\n%i >" % e['start']['line'])
            #text.append(re.sub(r'^.*?:\s*', '', e['text'].replace('\r','')))
            text.append(e['text'].replace('\r',''))
            line += 1

            a = (e['start']['line']-1, e['start']['character']-1)
            b = (e['end']['line']-1, e['end']['character']-1)
            line_to_pos[line] = (a,b)
            line_to_file[line] = e['file']


        if len(self.lasterrors) == 0:
            text.append("\n\nno errors")

        text.append('\n')

        self.line_to_file = line_to_file
        self.line_to_pos = line_to_pos
        self.text = ''.join(text)


    def tssjs_to_highlighter(self, view):
        """
            Creates a list of error and warning regions for all errors.

            Returns error_regions, warning_regions, error_texts
        """
        error_texts = {} # key: textpoint start and end, value: description
        error_regions = []
        warning_regions = []

        for e in self.lasterrors:
            if fn2k(e['file']) == fn2k(view.file_name()):

                a = view.text_point(e['start']['line']-1, e['start']['character']-1)
                b = view.text_point(e['end']['line']-1, e['end']['character']-1)

                error_texts[(a,b)] = e['text']

                if e['category'] == 'Error':
                    error_regions.append(sublime.Region(a,b))
                else:
                    warning_regions.append(sublime.Region(a,b))

        return error_regions, warning_regions, error_texts


    @max_calls()
    def on_close_typescript_project(self, root):
        """ Will be called when a typescript project is closed (eg all files closed).
            But there may be other open typescript projects.
            -> for future use :) """
        pass


