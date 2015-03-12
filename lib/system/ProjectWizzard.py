# coding=utf8

import sublime
import json
import os

from ..utils import package_path, Debug
from ..utils.disabling import set_plugin_temporarily_disabled, \
                               set_plugin_temporarily_enabled, \
                               is_plugin_temporarily_disabled


# ------------------------------------- PROJECT WIZZARD ----------------------------------------- #

class ProjectWizzard(object):


    def __init__(self, view, finished_callback):
        self.finished_callback = finished_callback
        self.window = view.window()
        if not self.window: # workaround
            self.window = view.window()
        self.view = view
        self.tsconfigfolder = None
        self.module = None
        self.outfile = None
        self.outdir = None
        self.target = "es5"
        self.sourcemap = True
        self.files = []
        Debug('project+', 'Disable ArcticTypescript while in WizzardMode')
        set_plugin_temporarily_disabled() # Disable global until wizzard is cancled or finished
        assert is_plugin_temporarily_disabled()


    def _prepare(self, message, action_default=None, action_cancel=None):
        """ Prepare quick_dialog """
        self.messages = []
        self.actions = []
        self.action_cancel = action_cancel
        self.action_default = action_default
        if message:
            if isinstance(message, str):
                message = [message]
            self.messages.append(message)
            self.actions.append(None)
        #Debug('project+', 'Hide Overlay')
        #self.window.run_command("hide_overlay")


    def _show_and_action(self):
        """ Show quick dialog and execute action """
        # every message must consist of the same number of lines
        max_lines = 0
        for m in self.messages:
            max_lines = max(max_lines, len(m))
        for m in self.messages:
            while len(m) < max_lines:
                m.append('')
        def on_select(i):
            #self.window.run_command("hide_overlay")
            if i == -1:
                Debug('project+', '-1: Quick panel canceled')
                sublime.set_timeout(self._cleanup, 50)
                if self.action_cancel is not None:
                    sublime.set_timeout(self.action_cancel, 50)
            elif i >= 0:
                if self.actions[i] is not None:
                    sublime.set_timeout(self.actions[i], 50)
                elif self.action_default is not None:
                    sublime.set_timeout(self.action_default, 50)
                Debug('project+', 'Nr %i selected' % i)
        self.window.show_quick_panel(self.messages, on_select)


    def handle_tsconfig_error(self, tsconfigfile, message=""):
        """ User will be asked to create a tsconfig.json file """
        self._prepare(message)

        self.messages.append(['> Open your tsconfig.json and Edit it'])
        self.actions.append(lambda: [self.window.open_file(tsconfigfile), self._cleanup()])

        self.messages.append(['> Show tsconfig.json example'])
        self.actions.append(lambda: [self.window.open_file(package_path + '/examples/basic_browser_project/tsconfig.json'), self._cleanup()])

        self.messages.append(['> Documentation: README ', 'see Chapter Settings'])
        self.actions.append(lambda: [self.window.open_file(package_path + '/README.md'), self._cleanup()])

        self._show_and_action()


    def new_tsconfig_wizzard(self, message=""):
        """ User will be asked to create a new tsconfig.json file """
        self._prepare(message, action_default=lambda: self.new_tsconfig_wizzard(message))

        self.messages.append(['Choose an option from below:'])
        self.actions.append(None)

        self.messages.append(['> Create a tsconfig.json file',
                              '(You will be asked questions at the bottom of the window.)'])
        self.actions.append(lambda: self._create_tsconfigjson())

        self.messages.append(['> I don\'t understand please show me the README file'])
        self.actions.append(lambda: [self.window.open_file(package_path + '/README.md'), self._cleanup()])

        self.messages.append(['> Disable ArcticTypescript for this folder'])
        self.actions.append(lambda: [set_plugin_temporarily_disabled(folder=self.view), self._cleanup()])

        Debug('project+', 'Show first quickpanel')
        self._show_and_action()


    def _create_tsconfigjson(self):
        """ Location for the tsconfig.json file """
        Debug('project+', 'Ask for tsconfig.json location')
        self.window.show_input_panel("Location for tsconfig.json (use your project folder)",
                                     os.path.dirname(self.view.file_name()),
                                     lambda folder: self._set_folder_and_go_on(folder),
                                     None, # on change
                                     lambda: [self._cleanup(),
                                               set_plugin_temporarily_disabled(folder=self.view),
                                              sublime.message_dialog(
                                        "ArcticTypescript disabled for this file's folder")]
                                    )


    def _set_folder_and_go_on(self, tsconfigfolder):
        tsconfigfolder = os.path.abspath(tsconfigfolder)
        is_direct_parent =  os.path.relpath(tsconfigfolder,
                                            os.path.dirname(self.view.file_name())) \
                            .replace('../', '').replace('..', '').replace('.', '') \
                            == ""
        if is_direct_parent:
            self.tsconfigfolder = tsconfigfolder
            self.tspath = os.path.abspath(os.path.join(self.tsconfigfolder, 'tsconfig.json'))
            self._ask_output_type()
        else:
            sublime.status_message("#### You have to choose a parent folder! ####")
            self._create_tsconfigjson()


    def _ask_output_type(self, message=""):
        """ Singlefile output or multiple files (AMD or commonjs style) """
        self._prepare(message, action_default=lambda: self._ask_output_type(message))

        self.messages.append(['Choose compiler behaviour:'])
        self.actions.append(None)

        self.messages.append(['> Compile to single file',
                              'use /// <reference path="ab.ts" /> with',
                              '  module { export } to spread code'])
        self.actions.append(lambda: [self._set_module(None), self._ask_output_file(), Debug('project', 'Single file selected')])

        self.messages.append(['> Commonjs: Compile to multiple files for NODEJS',
                              'not for browser use',
                              'use import a = require(\'utils\'); and export ... to spread code' ])
        self.actions.append(lambda: [self._set_module('commonjs'), self._ask_output_directory(), Debug('project', 'Commonjs selected')])

        self.messages.append(['> AMD: Compile to multiple files for requirejs',
                              'for BROWSER use, but also for Nodejs and Rhino',
                              'use import a = require(\'utils\'); and export ... to spread code' ])
        self.actions.append(lambda: [self._set_module('amd'), self._ask_output_directory('built/js/'), Debug('project', 'AMD selected')])

        Debug('project+', 'Show compiler behaviour quickpanel')
        self._show_and_action()


    def _set_module(self, module):
        self.module = module


    def _ask_output_file(self):
        """ For single file output, ask for the output filename """
        Debug('project+', 'Ask for output file')
        self.window.show_input_panel("Relative output location for the compiled .js FILE: %s/" % self.tsconfigfolder,
                                     "built/out.js",
                                     lambda outfile: [self._set_out(outfile), self._ask_for_files()],
                                     None, # on change
                                     lambda: [self._cleanup(),
                                               set_plugin_temporarily_disabled(folder=self.view),
                                              sublime.message_dialog(
                                                "ArcticTypescript disabled for this file's folder")]
                                    )


    def _set_out(self, outfile):
        self.outfile = outfile


    def _ask_output_directory(self, default="built/"):
        """ For multiple file output, ask for the output directory """
        Debug('project+', 'Ask for output directory')
        self.window.show_input_panel("Relative output FOLDER for all compiled js files: %s/" % self.tsconfigfolder,
                                     default,
                                     lambda outdir: [self._set_outdir(outdir), self._ask_for_files()],
                                     None, # on change
                                     lambda: [self._cleanup(),
                                               set_plugin_temporarily_disabled(folder=self.view),
                                               sublime.message_dialog(
                                                "ArcticTypescript disabled for this file's folder")])


    def _set_outdir(self, outdir):
        self.outdir = outdir


    def _ask_for_files(self, dialog=True):
        """ Ask to define all files which are the roots of the reference tree """
        if dialog:
            sublime.message_dialog("Please name all files which should be compiled, relative to %s/ \n \n You don't need to specify files which are refrenced using /// <reference> or import a = require('a');\n\n So only name the files which are on top of your reference tree.\n\n Press <Esc> or enter nothing to finish." % self.tsconfigfolder)

        firstfile = os.path.relpath(self.view.file_name(), self.tsconfigfolder)
        Debug('project+', 'Ask for files')
        self.window.show_input_panel("(%i) Please name all files which should be compiled, relative to %s/"
                                        % (len(self.files), self.tsconfigfolder),
                                     firstfile if dialog else "",
                                     lambda file: self._file_entered(file),
                                     None, # on change
                                     lambda: self._file_entered(""))


    def _file_entered(self, filename):
        if filename == "":
            self._finish()
        else:
            self.files.append(filename)
            self._ask_for_files(False)


    def _finish(self):
        """ make and write tsconfig.json. Call finished_callback """
        Debug('project+', 'Wizzard finished: Create and write tsconfig.json')
        content = { "compilerOptions" : {}, "files" : {}}
        if self.module is None:
            content['compilerOptions']['out'] = self.outfile
            content['compilerOptions']['target'] = self.target
            content['compilerOptions']['sourceMap'] = self.sourcemap
        elif self.module == "commonjs" or self.module == "amd":
            content['compilerOptions']['outDir'] = self.outdir
            content['compilerOptions']['target'] = self.target
            content['compilerOptions']['sourceMap'] = self.sourcemap
            content['compilerOptions']['module'] = self.module

        content['files'] = self.files

        self.write_json_to_tsconfigfile(content)

        if self.finished_callback:
            self.finished_callback()

        sublime.active_window().open_file(self.tspath)
        sublime.message_dialog("For more compilerOptions, see tsc --help.\n\n To configure ArcticTypescript, see README.md")

        self._cleanup()


    def _cleanup(self):
        Debug('project+', 'Enable ArcticTypescript again')
        set_plugin_temporarily_enabled()


    def write_json_to_tsconfigfile(self, content_obj):
        """ Write the python object content_obj into tsconfig.json """
        content_str = json.dumps(content_obj, sort_keys=True, indent=4)
        file_ref = open(self.tspath, "w")
        file_ref.write(content_str);
        file_ref.close()


