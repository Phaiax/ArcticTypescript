# coding=utf8

import sublime
import os
import sys

from ..utils.fileutils import read_and_decode_json_file, file_exists, \
                              is_ts, is_dts, read_file
from ..utils.pathutils import find_tsconfigdir
from ..utils.disabling import is_plugin_temporarily_disabled
from ..utils.CancelCommand import CancelCommand
from ..utils.options import allowed_compileroptions, allowed_settings
from ..utils import get_deep, get_first, random_str, Debug

from .ProjectWizzard import ProjectWizzard
from .ErrorsHighlighter import ErrorsHighlighter
from .Errors import Errors
from .Completion import Completion

from ..server.Processes import Processes
from ..server.TypescriptToolsWrapper import TypescriptToolsWrapper

from ..commands.Compiler import Compiler
from ..commands.Refactor import Refactor

from ..display.T3SViews import T3SVIEWS
from ..display.Message import MESSAGE

from ..tsconfiglint.TsconfigLinter import TsconfigLinter

from .globals import OPENED_PROJECTS



def get_or_create_project_and_add_view(view, wizzard=True):
    """
        Returns the project object associated with the file in view.
        Does return None if this file is not a .ts file or from other reasons
    """

    if (view is None
        or view.buffer_id() == 0
        or view.file_name() == ""
        or view.file_name() is None): # closed
        return None
    if view.is_loading():
        return None
    if is_plugin_temporarily_disabled(view):
        return None
    if not is_ts(view):
        return None
    if read_file(view.file_name()) is None:
        return None

    tsconfigdir = find_tsconfigdir(view.file_name())
    if tsconfigdir is None:
        if wizzard:
            Debug('project', "Project without tsconfig.json. Start Wizzard")
            PWizz = ProjectWizzard(view, lambda: get_or_create_project_and_add_view(view))
            PWizz.new_tsconfig_wizzard("No tsconfig.json found. Use this wizzard to create one.")
        return None
    tsconfigfile = os.path.join(tsconfigdir, "tsconfig.json")

    opened_project_with_same_tsconfig = \
         get_first(OPENED_PROJECTS.values(), lambda p: p.tsconfigdir == tsconfigdir)

    if opened_project_with_same_tsconfig is not None:
        Debug('project+', "Already opened project found.")
        opened_project_with_same_tsconfig.open(view)
        return opened_project_with_same_tsconfig
    else:
        # New ts project
        try:
            Debug('notify', "Try open project: %s" % tsconfigdir)

            # Lint tsconfig.json before opening
            can_open_project = True
            try:
                linter = TsconfigLinter(file_name=tsconfigfile)
            except CancelCommand:
                can_open_project = False
            if len(linter.harderrors) > 0:
                can_open_project = False

            if can_open_project:
                new_project = OpenedProject(view)
                if not hasattr(new_project, 'id'):
                    return None
                return new_project
            else:
                show_tsconfig_failed_wizzard(tsconfigfile)
                return None
        except CancelCommand:
            if get_or_create_project_and_add_view(view):
                get_or_create_project_and_add_view(view).close_project()
            return None

def close_all_projects():
    for p in OPENED_PROJECTS.copy().values():
        p.close_project()


def project_by_id(project_id):
    if project_id in OPENED_PROJECTS:
        return OPENED_PROJECTS[project_id]
    return None


def opened_project_by_tsconfig(tsconfigfile):
    if not tsconfigfile:
        return None
    tsconfigfile = os.path.normcase(tsconfigfile)
    for p in OPENED_PROJECTS.values():
        if os.path.normcase(p.tsconfigfile) == tsconfigfile:
            return p
    return None


def show_tsconfig_failed_wizzard(tsconfigfile):
    PWizz = ProjectWizzard(sublime.active_window().active_view(), lambda: None)
    PWizz.handle_tsconfig_error(tsconfigfile, ["tsconfig.json error. Close Project."])


class OpenedProject(object):
    """
        Manages ErrorViews, OutlineViews, the TSS process
        and open windows which belong to a Project.
        This class should replace all current global variables.
    """

    def __init__(self, startview):

        self.processes = None
        self.compiler = None
        self.errors = None
        self.highlighter = None
        self.tsserver = None
        self.completion = None

        if not startview.is_valid() or startview.window() is None:
            return

        self.id = random_str()
        OPENED_PROJECTS[self.id] = self

        self.project_file_name = startview.window().project_file_name()
        self.windows = [] # All windows with .ts files
        self.error_view = {} #key: window.window_id, value: view
        self.views = [] # All views with .ts files
        self.tsconfigdir = find_tsconfigdir(startview.file_name())
        self.tsconfigfile = os.path.join(self.tsconfigdir, "tsconfig.json")
        self.is_compiling = False
        self.authorized_commands = []
        self.forbidden_commands = []

        self.ArcticTypescript_sublime_settings = sublime.load_settings('ArcticTypescript.sublime-settings')

        self.open(startview)

        self._initialize_project()


    # ###############################################    INIT   ################


    def _initialize_project(self):
        self._lint_tsconfig_wizzard_on_harderrors()
        self._start_typescript_services()


    def _start_typescript_services(self):
        self.processes = Processes(self) ## INIT SERVICES


    def on_services_started(self):
        """ Will be called if self.processes has started the services """
        self.tsserver = TypescriptToolsWrapper(self)
        self.errors = Errors(self)
        self.completion = Completion(self)
        self.highlighter = ErrorsHighlighter(self)
        Debug('notify', 'Initializion finished')

        self.collect_untracked_views_and_update_content(self._on_collected_views)

    def _on_collected_views(self):
        # Start Error recalculation if error view is open
        if T3SVIEWS.ERROR._search_existing_view():
            self.views[0].run_command('typescript_error_panel')


    def is_initialized(self):
        return hasattr(self, 'processes') \
                 and self.processes is not None \
                 and self.processes.is_initialized() \
                 and hasattr(self, 'highlighter') \
                 and self.highlighter is not None


    def assert_initialisation_finished(self):
        """ Raises CancelCommand if initializion is not finished.
            Use decorator @catch_CancelCommand for easy use """
        if not self.is_initialized():
            sublime.status_message('You must wait for the initialisation to finish (%s)' % filename)
            raise CancelCommand()


    def collect_untracked_views_and_update_content(self, on_finished):
        """ Searches for opened ts views which belong to this project,
            add them to this project, transfer the current workspace
            view content to the tsserver and call on_finished afterwards. """

        def _collect_and_update_runner(fileslist):
            fileslist_normcased = [os.path.normcase(f) for f in fileslist]

            for w in sublime.windows():
                for v in w.views():
                    if not is_ts(v):
                        continue
                    v_tsconfigdir = find_tsconfigdir(v.file_name())
                    v_tsconfigfile = os.path.join(v_tsconfigdir, "tsconfig.json")
                    v_tsconfigfile = os.path.normcase(v_tsconfigfile)

                    # belong to same tsconfig AND is already registered in tsconfig[files]
                    # or referenced by other files in tsconfig[files] = fileslist
                    if v_tsconfigfile == os.path.normcase(self.tsconfigfile) \
                            and os.path.normcase(v.file_name()) in fileslist_normcased:
                        self.open(v)
                        self.tsserver.update(v)

            on_finished()

        self.tsserver.get_tss_indexed_files(_collect_and_update_runner)



    # ###############################################    OPEN/CLOSE   ##########


    def open(self, view):
        """ Should be called if a new view is opened, and this view belongs
            to the same tsconfig.json file """
        if view not in self.views:
            Debug('project+', "View %s added to project %s" % (view.file_name(), self.tsconfigfile))
            self.views.append(view)
            view.settings().set('auto_complete', self.get_setting("auto_complete"))
            view.settings().set('extensions', ['ts'])

        window = view.window()
        if window is None:
            Debug('notify', "ArcticTypescript: Window is None, why??")
            return
        if window not in self.windows:
            Debug('project+', "New Window added to project %s" % (self.tsconfigfile, ))
            self.windows.append(view.window())


    def _lint_tsconfig_wizzard_on_harderrors(self):
        self.tsconfigfile

    def close(self, view):
        """ Should be called if a view has been closed. Also accepts views which do not
            belong to this project
            Closes project if no more windows are open. """
        if view in self.views:
            self.views.remove(view)
            Debug('project+', "View %s removed from project %s" % (view.file_name(), self.tsconfigfile))
            for window in self.windows: # view.window() = None, so iterate all
                self._remove_window_if_not_needed(window)


    # ###############################################    KILL   ################


    def _remove_window_if_not_needed(self, window):
        """ Removes window from this projects window list,
            if this window does not contain any opened ts file.
            Closes project if no more windows are open.
            TODO: what happenes if the user moves views from one window to another """
        if not self._are_projectviews_opened_in_window(window):
            self.windows.remove(window)
            Debug('project+', "Window removed from project %s" % (self.tsconfigfile, ))
        if len(self.windows) == 0:
            self.close_project()


    def _are_projectviews_opened_in_window(self, window):
        """ checks if any views from this projects ts files are opened in window """
        window_views = window.views()
        for v in self.views:
            if v in window_views:
                return True
        return False


    def close_project(self, on_closed=None):
        """ Closes project, kills tsserver processes, removes all highlights, ... """
        Debug('project', "Project %s will be closed now" % (self.tsconfigfile, ))
        Debug('notify', "Close project %s" % self.tsconfigfile)
        self.on_project_closed = on_closed
        if self.errors: # remove error highlights
            self.errors.lasterrors = []
            self.highlighter.highlight_all_open_files()
        if self.compiler:
            self.compiler.kill()
        if self.tsserver:
            self.tsserver.kill(lambda: self._tsserverkilled())
        else:
            self._tsserverkilled()


    def _tsserverkilled(self):
        if self.processes:
            self.processes.kill()
        self.views = []
        self.windows = []
        OPENED_PROJECTS.pop(self.id)
        if self.on_project_closed:
            self.on_project_closed()


    def reopen_project(self):
        view0 = self.views[0]
        def reopen():
            get_or_create_project_and_add_view(view0)
            MESSAGE.show('Reloading finished', True)
        MESSAGE.show('Reloading project')
        self.close_project(reopen)



    # ###############################################    SETTINGS   ############


    def get_compileroption(self, optionkey, use_cache=False):
        """
            Compileroptions are always located in tsconfig.json.
            allowed_compileroptions define the allowed options
            Use use_cache if you are making multiple request at once
        """
        if optionkey not in allowed_compileroptions:
            Debug('notify', "Requested unknown compiler option: %s. Will always be None."
                  % optionkey)
        return get_deep(self._get_tsconfigsettings(use_cache),
                        'compilerOptions:' + optionkey)


    def get_first_file_of_tsconfigjson(self, use_cache=False):
        try:
            return get_deep(self._get_tsconfigsettings(use_cache), 'files:0')
        except KeyError:
            return None


    def get_common_path_prefix_of_files(self, use_cache=False):
        """ Returns the common dir which all files of tsconfig.json["files"]
            have in commmon: "src" for ["src/main.ts", "src/test.ts"] """
        try:
            files = get_deep(self._get_tsconfigsettings(use_cache), 'files')

            if len(files) > 0:
                common_prefix = os.path.dirname(files[0])
                for f in files:
                    dir_ = os.path.dirname(f)
                    # shorten prefix until it is matched
                    while len(common_prefix) > 0:
                        if dir_.startswith(common_prefix):
                            break
                        else:
                            common_prefix = common_prefix[:-1]
                return common_prefix
        except KeyError:
            pass

        return ""


    def _get_tsconfigsettings(self, use_cache=False):
        """ No cacheing by default """
        if use_cache and hasattr(self, 'tsconfigcache'):
            return self.tsconfigcache
        if file_exists(self.tsconfigfile):
            try:
                self.tsconfigcache = read_and_decode_json_file(self.tsconfigfile)
            except Exception as e:
                Debug('notify', "Error reading tsconfig.json: %s. Close Project." % e)
                show_tsconfig_failed_wizzard(self.tsconfigfile)
                self.close_project()
                raise CancelCommand
        else:
            self.tsconfigcache = {}
        return self.tsconfigcache


    def get_setting(self, settingskey, use_cache=False):
        """
            Allowed settings are defined in allowed_settings.
            Settings can be located in multiple files with these priorities:
            A setting in 1. overrides a setting in 3.
            1.  *   tsconfig.json['ArcticTypescript'][KEY]
            2.      Sublime-Settings: http://www.sublimetext.com/docs/3/settings.html
            2.0       Distraction Free Settings
            2.1       Packages/User/<syntax=TypeScript>.sublime-settings['ArcticTypescript'][KEY]
            2.2       Packages/<syntax=TypeScript>/<syntax=TypeScript>.sublime-settings['ArcticTypescript'][KEY]
            2.3 *     <ProjectSettings>.sublime-settings['settings']['ArcticTypescript'][KEY]
            2.4 *     Packages/User/Preferences.sublime-settings['ArcticTypescript'][KEY]
                      You can open this file via Menu -> Preferences -> "Settings - User"
            2.5       Packages/Default/Preferences (<platform>).sublime-settings['ArcticTypescript'][KEY]
            2.6       Packages/Default/Preferences.sublime-settings['ArcticTypescript'][KEY]
            3.      Sublime config dir/Packages/User/ArcticTypescript.sublime-settings[KEY]
                    You can open this file via Menu
                    -> Preferences -> Package Settings -> ArcticTypescript -> "Settings - User"


            Where should i put the settings? (recommendation):
                * Use 2.4. or 3. for personal settings across all typescript projects
                * Use 2.3 for personal, project specific settings
                * Use 1. if you are not part of a team
                         or for settings for everyone
                         or for project specific settings if you don't have created a sublime project

        """
        if settingskey not in allowed_settings:
            Debug('notify', "Requested unknown setting: %s. Will always be None."
                  % settingskey)
            return None

        # 1. tsconfig.json['ArcticTypescript'][KEY]
        try:
            return get_deep(self._get_tsconfigsettings(use_cache),
                        'ArcticTypescript:' + settingskey)
        except KeyError:
            pass

        # 2.  Sublime-Settings: http://www.sublimetext.com/docs/3/settings.html
        #     <ProjectSettings>.sublime-settings['settings']['ArcticTypescript'][KEY]
        try:
            return get_deep(self.views[0].settings().get('ArcticTypescript'), settingskey)
        except KeyError:
            pass

        # 3.  Sublime config dir/Packages/User/ArcticTypescript.sublime-settings[KEY]
        # Sublime will merge the defaults from the package file
        try:
            settingskeys = settingskey.split(':')
            firstkey = settingskeys.pop(0)
            if not self.ArcticTypescript_sublime_settings.has(firstkey):
                raise KeyError()
            setting = self.ArcticTypescript_sublime_settings.get(firstkey)
            return get_deep(setting, settingskeys)
        except KeyError:
            pass


        Debug('project', "No default setting for %s could not be found for project %s." % (settingskey, self.tsconfigfile, ))
        raise Exception("Arctic Typescript Bug: Valid setting requested, but default value can not be found.")


    # ###############################################    COMPILE   #############


    def compile_once(self, window_for_panel, triggered_for_file):

        if self.is_compiling and self.compiler is not None:
            if self.compiler.is_alive():
                sublime.status_message('Still compiling. Use Goto Anything > "ArcticTypescript: Terminate All Builds" to cancel.')
                self.compiler._show_output("")
            else:
                self.is_compiling = False

        if not self.is_compiling:
            self.is_compiling = True
            self.compiler = Compiler(self, window_for_panel, triggered_for_file)
            self.compiler.daemon = True

            sublime.status_message('Compiling')
            self.compiler.start()


    def extract_variables(self, use_cache=False):
        file_name = sublime.active_window().active_view().file_name()
        ext = os.path.basename(file_name).split('.', 1)[1:]
        project_file = self.project_file_name
        for window in self.windows:
            if window and window.project_file_name():
                project_file = window.project_file_name()
        project_ext = os.path.basename(project_file).split('.', 1)[1:]

        variables = {
            #The directory of the current file, e.g., C:\Files.
            "file_path": os.path.dirname(file_name),
            #The name portion of the current file, e.g., Chapter1.txt.
            "file_name": os.path.basename(file_name),
            #The extension portion of the current file, e.g., txt.
            "file_extension": ext[0] if ext else "",
            #The name-only portion of the current file, e.g., Document.
            "file_base_name": os.path.basename(file_name).split('.', 1)[0],
            #The full path to the current file, e.g., C:\Files\Chapter1.txt.
            "file": file_name,
            #The full path to the Packages folder.
            "packages": sublime.packages_path(),
            #The directory of the current project file.
            "project_path": os.path.dirname(project_file),
            #The name portion of the current project file.
            "project_name": os.path.basename(project_file),
            #The extension portion of the current project file.
            "project_extension": project_ext[0] if ext else "",
            #The name-only portion of the current project file.
            "project_base_name": os.path.basename(project_file).split('.', 1)[0],
            #The full path to the current project file.
            "project": project_file,
            # linux, darwin, nt
            "platform": sys.platform,
            # tsconfig dir
            "tsconfig_path": self.tsconfigdir,
            "tsconfig": self.tsconfigfile
        }

        variables.update(self._get_tsconfigsettings(use_cache)['compilerOptions'])

        for key in allowed_settings:
            variables[key] = self.get_setting(key, use_cache=True)

        return variables

    def show_compiled_file(self):
        """ Displays the compiled result. Displays out if out is specified.
        Otherwise the file which corresponds to view, if view is a ts file. """

        try:
            out = self.get_compileroption("out", use_cache=True)
            if out:
                display_file = os.path.join(self.tsconfigdir, out)
                self._typescript_build_view_command(display_file)
                return
        except KeyError:
            pass

        try:
            outdir = self.get_compileroption("outDir", use_cache=True)
            if outdir:
                if self.compiler and self.compiler.triggered_for_file:
                    tsfile = self.compiler.triggered_for_file
                else:
                    tsfile = os.path.join(self.tsconfigdir, self.get_first_file_of_tsconfigjson(use_cache=True))

                # rel path from tsconfigdir to view.file_name
                relpath = os.path.relpath(os.path.normcase(tsfile),
                                start=self.tsconfigdir)
                #relpath = "src/views/uimain.ts"

                # all common prefixes from the [files] in tsconfig.json are discared
                discard = self.get_common_path_prefix_of_files(use_cache=True)
                # discard = "src"

                if relpath.startswith(discard):
                    relpath = relpath[len(discard):]

                if relpath.startswith("/"):
                    relpath = relpath[1:]

                if relpath.endswith(".ts"):
                    relpath = relpath[:-2] + "js"

                display_file = os.path.join(self.tsconfigdir, outdir, relpath)
                self._typescript_build_view_command(display_file)
                return
        except KeyError:
            pass



    def _typescript_build_view_command(self, display_file):
        sublime.active_window().active_view().run_command('typescript_build_view',
                         { "project_id": self.id,
                           "display_file": display_file })


    # ###############################################    REFACTOR   #############

    def do_refactor(self, refs, old_name, new_name, edit_token):
        #if not self.refactor or not self.refactor.is_alive():
        self.refactor = Refactor(self, refs, old_name, new_name, edit_token)
        self.refactor.start()


