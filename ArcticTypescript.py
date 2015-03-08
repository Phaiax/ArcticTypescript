# coding=utf8

import sublime

if int(sublime.version()) >= 3000:

    # DISABLE until API is ready
    from .lib.utils.disabling import set_plugin_temporarily_enabled, \
                                      set_plugin_temporarily_disabled
    set_plugin_temporarily_disabled()

    # PREPARE for mac
    from .lib.utils.pathutils import add_usr_local_bin_to_path_on_osx
    add_usr_local_bin_to_path_on_osx()

    # IMPORT COMMANDS and LISTENERS
    from .lib.Commands import *
    from .lib.Listener import TypescriptEventListener
    from .lib.tsconfiglint.TsconfigListener import TsconfigEventListener
    from .lib.display.T3SViews import TypescriptEventListener2
    from .lib.system.Project import get_or_create_project_and_add_view, \
                                    close_all_projects


    def plugin_loaded():
        """ This will be called by sublime if the API is ready """
        # ENABLE since API is ready
        set_plugin_temporarily_enabled()

        # Activate Typescript if current view is a .ts file
        view = sublime.active_window().active_view()
        sublime.set_timeout(lambda: get_or_create_project_and_add_view(view), 300)

        # Testing (Only executes if we have opened the TDDTesting project)
        # Use filepattern to select tests. Examples: '*foo*', 'test_foo.py'
        run_tests(filepattern='*utils*') #


    def plugin_unloaded():
        """ This will be called by sublime if this plugin will be unloaded """
        set_plugin_temporarily_disabled()
        close_all_projects()
        # TODO: Kill processes


    def run_tests(filepattern=''):
        """ Run tests if this project is named TDDTesting """
        testproject = "ArcticTypescript/tests/TDDTesting/TDDTesting.sublime-project"
        projectfile = sublime.active_window().project_file_name()
        package_pattern = 'ArcticTypescript'
        if filepattern != '':
            package_pattern = "%s:%s" % (package_pattern, filepattern)
        if projectfile is not None and projectfile.endswith(testproject):
            sublime.set_timeout(lambda:sublime.run_command(
                        'unit_testing',
                        {'output': 'panel', 'package': package_pattern}), 300)

else:
    sublime.error_message("ArcticTypescript does not support Sublime Text 2")
