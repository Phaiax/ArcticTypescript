# coding=utf8

import sublime
import json

from ..display.Message import MESSAGE
from ..display.T3SViews import T3SVIEWS

from .AsyncCommand import AsyncCommand

from ..utils import make_hash, Debug, max_calls
from ..utils.fileutils import is_dts, fn2l, realfn
from ..utils.viewutils import get_file_infos
from ..utils.CancelCommand import CancelCommand


# --------------------------- TypescriptToolsWrapper ------------------------------------ #

class TypescriptToolsWrapper(object):
    """ This Class translates the available commands to the corresponding string
        command for the typescript-tools from clausreinke   """


    def __init__(self, project):
        self.project = project
        self.added_files = {} # added_files[filename] = hash
        self.executed_with_most_recent_file_contents = []
        self.is_killing = False


    # RELOAD PROCESS
    @max_calls()
    def reload(self, callback=None):
        AsyncCommand('reload', self.project) \
            .set_id('reload') \
            .set_result_callback(lambda r: callback is None or callback()) \
            .append_to_both_queues()
        self.project.errors.start_recalculation()


    # GET INDEXED FILES
    @max_calls()
    def get_tss_indexed_files(self, callback):
        AsyncCommand('files', self.project) \
            .do_json_decode_tss_answer() \
            .set_result_callback(callback) \
            .append_to_fast_queue()

    # DUMP FILE (untested)
    @max_calls()
    def dump(self, filename, output, callback):
        dump_command = 'dump {0} {1}'.format( output, fn2l(realfn(filename)) )
        AsyncCommand(dump_command, self.project) \
            .set_result_callback(callback) \
            .append_to_fast_queue()

    # Evaluate Javascript (refer to utils/debug.py)
    @max_calls()
    def eva(self, js_cmd):
        def cb(strres):
            import json
            js = json.loads(strres)
            # Sometimes this is to much output. Activate and adapt this if you are evaluating '_this'
            #del js['fileNameToScript']['c:/Users/danie_000/AppData/Roaming/Sublime Text 3/Packages/ArcticTypescript/bin/node_modules/typescript/bin/lib.d.ts']
            #del js['snapshots']['c:/Users/danie_000/AppData/Roaming/Sublime Text 3/Packages/ArcticTypescript/bin/node_modules/typescript/bin/lib.d.ts']
            print(json.dumps(js, indent=3))
            self.last_eva = js
        eva = 'eva {0}'.format(js_cmd)
        AsyncCommand(eva, self.project) \
            .set_result_callback(cb) \
            .append_to_slow_queue()

    # TYPE
    @max_calls()
    def type(self, filename, line, col, callback):
        """ callback({ tss type answer }, filename=, line=, col=) """

        type_command = 'type {0} {1} {2}'.format( str(line+1), str(col+1), fn2l(realfn(filename)) )

        AsyncCommand(type_command, self.project) \
            .set_id("type_command") \
            .set_callback_kwargs(filename=filename, line=line, col=col) \
            .do_json_decode_tss_answer() \
            .set_result_callback(callback) \
            .append_to_fast_queue()


    # DEFINITION
    @max_calls()
    def definition(self, filename, line, col, callback):
        """ callback({ tss type answer }, filename=, line=, col=) """

        definition_command = 'definition {0} {1} {2}'.format( str(line+1), str(col+1), fn2l(realfn(filename)) )

        AsyncCommand(definition_command, self.project) \
            .set_id("definition_command") \
            .set_callback_kwargs(filename=filename, line=line, col=col) \
            .do_json_decode_tss_answer() \
            .set_result_callback(callback) \
            .append_to_fast_queue()


    # REFERENCES
    @max_calls()
    def references(self, filename, line, col, callback):
        """ callback({ tss type answer }, filename=, line=, col=) """

        references_command = 'references {0} {1} {2}'.format( str(line+1), str(col+1), fn2l(realfn(filename)) )

        AsyncCommand(references_command, self.project) \
            .set_id("references_command") \
            .set_callback_kwargs(filename=filename, line=line, col=col) \
            .do_json_decode_tss_answer() \
            .set_result_callback(callback) \
            .append_to_fast_queue()

    # STRUCTURE
    @max_calls()
    def structure(self, filename, sender_view_id, callback):
        """ callback({ tss type answer }, filename=, sender_view_id=) """
        return # structure command has been dropped

        structure_command = 'structure {0}'.format(fn2l(realfn(filename)))

        AsyncCommand(structure_command, self.project) \
            .set_id("structure_command for view %i" % sender_view_id) \
            .set_callback_kwargs(filename=filename, sender_view_id=sender_view_id) \
            .do_json_decode_tss_answer() \
            .set_result_callback(callback) \
            .append_to_fast_queue()


    # ASK FOR COMPLETIONS
    @max_calls()
    def complete(self, filename, line, col, is_member_str, callback):
        """ callback("tss type answer as string") """

        completions_command = 'completions {0} {1} {2} {3}'.format(is_member_str, str(line+1), str(col+1), fn2l(realfn(filename)))

        Debug('autocomplete', "Send async completion command for line %i , %i" % (line+1, col+1))

        AsyncCommand(completions_command, self.project) \
            .set_id("completions_command") \
            .procrastinate() \
            .set_result_callback(callback) \
            .set_callback_kwargs(filename=filename, line=line, col=col, is_member_str=is_member_str) \
            .append_to_fast_queue()


    # UPDATE FILE
    @max_calls()
    def update(self, view):
        """ updates the view.buffer's content to the buffer in tss.js """

        # only update if the file contents have changed since last update call on this file
        filename, lines, content = get_file_infos(view)
        if self.need_update(filename, content):
            update_command = 'update nocheck {0} {1}\n{2}'.format(str(lines+1), fn2l(realfn(filename)), content)

            AsyncCommand(update_command, self.project) \
                .set_id('update %s' % filename) \
                .append_to_both_queues()

            self.on_file_contents_have_changed()


    # ADD FILE
    @max_calls()
    def add(self, filename, lines, content):

        update_command = 'update nocheck {0} {1}\n{2}'.format(str(lines+1), fn2l(realfn(filename)), content)

        AsyncCommand(update_command, self.project) \
            .set_id('add %s' % filename) \
            .append_to_both_queues()

        self.need_update(filename, content) # save current state
        self.on_file_contents_have_changed()


    @max_calls()
    def need_update(self, filename, unsaved_content):
        """ Returns True if <unsaved_content> has changed since last call to need_update(). """
        newhash = make_hash(unsaved_content)
        oldhash = self.added_files[filename] if filename in self.added_files else "nohash"
        if newhash == oldhash:
            Debug('tss+', "NO UPDATE needed for file : %s" % filename)
            return False
        else:
            Debug('tss+', "UPDATE needed for file %s : %s" % (newhash, filename) )
            self.added_files[filename] = newhash
            return True


    def on_file_contents_have_changed(self):
        """
            Every command that wants to only be executed when file changes have been made
            can use self.executed_with_most_recent_file_contents to remember a previous execution.
            After any change, this array will be cleared
        """
        self.executed_with_most_recent_file_contents = []

    def files_changed_after_last_call(self, cmd_hint):
        """
            Returns True if there have been any file changes after last call
            to this function.
        """
        if cmd_hint in self.executed_with_most_recent_file_contents:
            return False
        self.executed_with_most_recent_file_contents.append(cmd_hint)
        return True


    # ERRORS
    @max_calls()
    def errors(self, callback=None):
        """ callback format: callback(result) """

        # TODO: this may prevent initial error display or if user triggers manually
        if not self.files_changed_after_last_call('errors'):
            return

        T3SVIEWS.ERROR.on_calculation_initiated()

        AsyncCommand('showErrors', self.project) \
            .set_id('showErrors') \
            .procrastinate() \
            .activate_debounce() \
            .set_result_callback(lambda errors: [callback(errors), T3SVIEWS.ERROR.on_calculation_finished()] ) \
            .set_executing_callback(lambda: T3SVIEWS.ERROR.on_calculation_executing()) \
            .set_replaced_callback(lambda by: T3SVIEWS.ERROR.on_calculation_replaced()) \
            .append_to_slow_queue()


    # KILL PROCESS (if no more files in editor)
    @max_calls()
    def kill(self, finished_callback):

        if not self.project.is_initialized() or self.is_killing:
            return

        self.is_killing = True


        def on_quit(msg=""):
            if hasattr(self, 'finished_callback_called'):
                return
            self.finished_callback_called = True
            finished_callback()

        # send quit and kill process afterwards
        AsyncCommand('quit', self.project) \
            .set_id('quit') \
            .set_result_callback(on_quit) \
            .append_to_both_queues()

        sublime.set_timeout(on_quit, 5000)

        #TODO: this function is old and not updated
        # - project class should kill processes, but before executing this,
        #   so a Quit command can be send to tss.js
        # - maybe: get_tss_indexed_files can be used to prevent project from
        #          closing, if there are opened views with belonging .ts files,
        #          but if these views are not in projcet.views.
        #          But in this case it would be better to add those views to
        #          projcet.views using tsserver.get_tss_indexed_files


        # removed
