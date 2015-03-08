# coding=utf8

import re
from ..utils.fileutils import fn2k

def normalize_tssjs_error_output(self, errors):
    """
        Takes the de-jsoned output of the tss.js error command and creates
        some dicts for easy access
    """


def tssjs_to_errorview(self, errors):
    """
        Takes the de-jsoned output of the tss.js error command and creates the content for the error view.
        It also creates a relation between each line in the error view and the file and position of the error.

        Returns text, \
                line_to_file[line] = filename,\
                line_to_pos[line] = ((l,c),(l,c))

    """
    line_to_file = {}
    line_to_pos = {}

    previous_file = ''
    line = 0

    for e in errors:
        filename = e['file'].split('/')[-1]
        if previous_file != filename:
            text.append("\n\nOn File : %s \n" % filename)
            line += 3
            previous_file = filename

        text.append("\n%i >" % e['start']['line'])
        text.append(re.sub(r'^.*?:\s*', '', e['text'].replace('\r','')))
        line += 1

        a = (e['start']['line']-1, e['start']['character']-1)
        b = (e['end']['line']-1, e['end']['character']-1)
        line_to_pos[line] = (a,b)
        line_to_file[line] = e['file']


    if len(errors) == 0:
        text.append("\n\nno errors")

    text.append('\n')
    text = ''.join(text)

    return text, line_to_file, line_to_pos


def tssjs_to_highlighter(self, errors, file_name):
    """
        Creates a list of error and warning regions for all errors.

        Returns error_regions, warning_regions
    """
    error_regions = []
    warning_regions = []

    key = fn2k(file_name)
    self.errors[key] = {}

    for e in errors:
        if fn2k(e['file']) == key:

            a = view.text_point(e['start']['line']-1, e['start']['character']-1)
            b = view.text_point(e['end']['line']-1, e['end']['character']-1)

            self.errors[key][(a,b)] = e['text']

            if e['category'] == 'Error':
                error_regions.append(sublime.Region(a,b))
            else:
                warning_regions.append(sublime.Region(a,b))
