# coding=utf8

import sublime
import json
import os
import re

from ..utils.debug import Debug
from ..utils.CancelCommand import catch_CancelCommand, CancelCommand
from ..utils.fileutils import read_file
from ..utils.pathutils import package_path
from ..utils.viewutils import get_content

from ..utils.options import allowed_compileroptions, \
                            allowed_settings, \
                             compileroptions_validations, \
                             settings_validations

from ..utils.disabling import set_tsglobexpansion_disabled, \
                              set_tsglobexpansion_enabled, \
                              is_tsglobexpansion_disabled


empty_tsconfig = {
    "compilerOptions": {},
}



# ##########################################################################
# ###################         MAIN: lints entry point             ##########
# ##########################################################################


@catch_CancelCommand
def check_tsconfig(view):
    """ Tests view for being a tsconfig.json.
        Reads the tsconfig.json and checks for errors.
        Show Errors using Regions.
        Set a error map [<(a,b), msg>] into views settings. """

    if not _is_valid_and_enabled(view):
        return

    Debug('tsconfig', 'tsconfig modified, check')

    linter = TsconfigLinter(view)

    return linter


# ##########################################################################
# #############         MAIN: display error in status             ##########
# ##########################################################################


def show_lint_in_status(view):
    """ Uses the error map stored in view.settings() to display
        status messages if the cursor is above an error """

    if not _is_valid_and_enabled(view):
        return

    if view.settings().has('tsconfig-lints'):
        error_locations = view.settings().get('tsconfig-lints', [])

        current_errors = []
        current_selection = view.sel()[0]

        for pos, error in error_locations:
            error_region = sublime.Region(pos[0], pos[1])
            if current_selection.intersects(error_region):
                current_errors.append(error)

        if len(current_errors):
            view.set_status('tsconfig-errors', ' | '.join(current_errors))
        else:
            view.erase_status('tsconfig-errors')


# ######################################################################
# ###############                   HELPERS                   ##########
# ######################################################################


def _is_valid_and_enabled(view):
    """ Returns True if tslint should be activated """
    if not view.is_valid() or view.is_loading():
        return False

    if not _is_tsconfig(view):
        return False

    if is_tsglobexpansion_disabled():
        return False

    return True


def _is_tsconfig(view):
    """ Returns True if view is a tsconfig.json file """
    if view is None or not view:
        return False
    fn = view.file_name() # only call once!
    if fn is None or not fn:
        return False
    return os.path.basename(fn) == "tsconfig.json"


# ##########################################################################
# ###################         CLASS: TsconfigLinter               ##########
# ##########################################################################


class TsconfigLinter(object):
    """ Executes a linting on view.
        View has to be a tsconfig.json file.
        Marks errors and saves an error map in views settings.
        FatalErrors: IO Errors -> raise CancelCommands, the unexpected
        HardErrors: Syntax Errors, Wrong Types
        SoftErrors: Spellings, non existent files, unknown keys.
        Inserts a default structure if the file is empty. """


    def __init__(self, view=None, file_name=None):
        """ Starts linting.
            Raises CancelCommand if a fatal error occures. """

        # Initializing
        self.linted = False
        self.view = view
        self.file_name = file_name


        self.error_regions = []
        self.tsconfig = None
        self.harderrors = [] # would prevent from expanding filesglob
        self.softerrors = [] # would allow expandglob.js to work
        self.numerrors = 0;
        self.msg, self.line, self.col, self.char = None, None, None, None

        # reading
        self._read_file_and_set_paths()
        self._check_empty_and_insert_default()
        # main syntax checks
        if not self._check_jsonsyntax():
            if self._check_root_dicts():
                # syntax is fine -> linting
                self._check_key_spellings()
                self._check_unknown_keys()
                self._validate_values()
                self._check_files_are_strings()
                self._check_files_are_ts_files()
                self._check_files_exist()

        # display errors
        self._add_regions()
        self._store_error_locations_in_views_settings()
        self.linted = True


    # ######################################################################
    # ###############                   HELPERS                   ##########
    # ######################################################################


    def _hard_error(self, msg, pos):
        """ Display and cound hard error """
        self.harderrors.append((pos, msg))
        self.numerrors += 1
        Debug('tsconfig.json', msg)


    def _soft_error(self, msg, pos):
        """ Display and count soft error """
        self.softerrors.append((pos, msg))
        self.numerrors += 1
        # Debug('tsconfig.json', msg)

    def _store_error_locations_in_views_settings(self):
        """ Stores the errors in view.settings()
            Format: [<((a,b), msg)>] """
        if self.view:
            error_locations = []
            error_locations.extend(self.harderrors)
            error_locations.extend(self.softerrors)
            self.view.settings().set('tsconfig-lints', error_locations)


    # ######################################################################
    # ###############            DISPLAY                          ##########
    # ######################################################################


    def _add_regions(self):
        """ Display all found Errors """
        if self.view:
            self.view.add_regions('tsconfig-error', self.error_regions,
                                  'invalid', 'dot', sublime.DRAW_NO_FILL)


    # ######################################################################
    # ###############                   READ CONTENT              ##########
    # ######################################################################


    def _read_file_and_set_paths(self):
        """ Reads content from view into self.content and self.len """
        if self.view:
            self.file_name = self.view.file_name()
            self.content = get_content(self.view)
            self.len = len(self.content)
        elif self.file_name:
            self.content = read_file(self.file_name)
            self.len = len(self.content)
        else:
            Debug('error', "Tsconfiglinter: either view or filename is required");

        self.tsconfigdir = os.path.abspath(os.path.dirname(self.file_name))

        if self.content is None:
            self.numerrors += 1
            Debug('tsconfig', 'Could not read content from view.')
            raise CancelCommand()


    def _check_empty_and_insert_default(self):
        """ Checks if content is empty and inserts default tsonfig.json if so.
            Raises CancelCommand() if empty before. """

        if self.content == "":
            if not is_tsglobexpansion_disabled() and self.view:
                Debug('tsconfig', 'put default base structure to tsconfig.json')
                self.view.run_command('append', {'characters':
                        json.dumps(empty_tsconfig, indent=4)})
            raise CancelCommand()


    # ######################################################################
    # ###############                   JSON                      ##########
    # ######################################################################


    def _check_jsonsyntax(self):
        """ Parse self.content into self.tsconfig.
            Raise CancelCommand on Fatal Error.
            Make HardErrors on syntax errors.
            Return True if parsing has succeeded, even if there were errors. """

        try:
            # DECODE
            self.tsconfig = json.loads(self.content)
        except ValueError as e:
            Debug('tsconfig', 'json error %s %s' % (type(e), e))

            # Parse -> self.msg,line,col,char
            self._parse_jsonerror(e.args[0])

            # Parsing of exception failed
            if self.msg is None:
                Debug('tsconfig.json', 'json error %s' % e)
                self.numerrors += 1
                raise CancelCommand()

            # Display
            self._hard_error("%s (Line %i Column %i)"
                             % (self.msg, self.line, self.col),
                             self._lint_range(self.char))

            return True # Allow detailed linting

        except Exception as e:
            # The Unexpected
            Debug('tsconfig', 'unexpected json.loads() error %s %s'
                               % (type(e), e))
            self.numerrors += 1
            raise CancelCommand()

        return False


    def _parse_jsonerror(self, error):
        """ Parse the exception message:
            extract line, char, col, msg into self.* """

        try:
            self.msg, line, col, char = re.match(
                        '(.*): line ([\d]+) column ([\d]+) \(char ([\d]+)\)',
                        error).groups()
        except Exception:
            self.msg, self.line, self.col, self.char = None, None, None, None
            return

        # str -> int -> str should be the same

        self.line = int(line)
        self.col = int(col)
        self.char = int(char)

        if str(self.line) != line \
                or str(self.col) != col \
                or str(self.char) != char:
            self.msg, self.line, self.col, self.char = None, None, None, None


        # Some Possible JSON Errors:

        # <class 'ValueError'> Expecting property name enclosed in
        #                      double quotes: line 2 column 25 (char 26)
        # <class 'ValueError'> Expecting ':' delimiter: line 2
        #                      column 27 (char 28)
        # <class 'ValueError'> Expecting object: line 2 column 28 (char 29)


    # ######################################################################
    # ###############            LINT BASE STRUCTURE, KEYS        ##########
    # ######################################################################


    def _check_key_spellings(self):
        """ Check Spelling of main dicts: currently only caSe """

        self._expect_key_of_obj_to_be_y(self.tsconfig, "compilerOptions")
        self._expect_key_of_obj_to_be_y(self.tsconfig, "files")
        self._expect_key_of_obj_to_be_y(self.tsconfig, "filesGlob")
        self._expect_key_of_obj_to_be_y(self.tsconfig, "ArcticTypescript")


    def _expect_key_of_obj_to_be_y(self, obj, y):
        """ Checks for wrong spellings (caSe) of y in the keys of obj """

        key_found = False
        for k in obj.keys():
            if k.lower() == y.lower():
                key_found = True

                if k == y:
                    return

                self._soft_error("key '%s' is spelled wrong" % k,
                                self._lint_key(k))
        return key_found


    def _check_root_dicts(self):
        """ Check Type of root dicts == dict.
            Returns True if everything is ok. """

        # root
        if type(self.tsconfig) != dict:
            self._hard_error("root structure must be an object: { }",
                            self._lint_range(0, self.len - 1))
            return False

        # first layer
        valid = self._execute_validator(dict, self.tsconfig, 'compilerOptions'), \
                self._execute_validator(list, self.tsconfig, 'files'), \
                self._execute_validator(list, self.tsconfig, 'filesGlob'), \
                self._execute_validator(dict, self.tsconfig, 'ArcticTypescript')

        return all(valid)

    def _check_unknown_keys(self):
        """ Check for unknown keys in compilerOptions and ArcticTypescript """

        if "compilerOptions" in self.tsconfig:
            for option in self.tsconfig["compilerOptions"].keys():
                if option not in allowed_compileroptions:
                    self._soft_error("unknown key '%s' in compilerOptions"
                                     % option,
                                     self._lint_key(option))

        if "ArcticTypescript" in self.tsconfig:
            for option in self.tsconfig["ArcticTypescript"].keys():
                if option not in allowed_settings:
                    self._soft_error("unknown key '%s' in ArcticTypescript"
                                     % option,
                                     self._lint_key(option))


    # ######################################################################
    # ###############            LINT VALUES                      ##########
    # ######################################################################


    def _validate_values(self):
        """ Validate compilerOptions and ArcticTypescript using the validators
            from utils.options """

        if "compilerOptions" in self.tsconfig:
            for key, validator in compileroptions_validations.items():
                self._execute_validator(validator,
                                        self.tsconfig["compilerOptions"], key)

        if "ArcticTypescript" in self.tsconfig:
            for key, validator in settings_validations.items():
                self._execute_validator(validator,
                                        self.tsconfig["ArcticTypescript"], key)



    def _execute_validator(self, validator, dict_with_uservalue, key):
        """ Execute validation for dict_with_uservalue[key]
            and display error on validation failure.
            HardErrors on type mismatch,
            SoftErrors on regex or [<str>] mismatch.
            Returns True if key does not exists or if it is valid """

        # exists?
        if key not in dict_with_uservalue:
            return True
        uservalue = dict_with_uservalue[key]

        # type
        if validator == str:
            if type(uservalue) != str:
                self._hard_error("value of '%s' has to be a string" % key,
                                 self._lint_value_of_key(key))
                return False

        if validator == list:
            if type(uservalue) != list:
                self._hard_error("value of '%s' has to be a list" % key,
                                self._lint_value_of_key(key))
                return False

        if validator == bool:
            if type(uservalue) != bool:
                self._hard_error("value of '%s' has to be true or false" % key,
                                self._lint_value_of_key(key))
                return False

        if validator == dict:
            if type(uservalue) != dict:
                self._hard_error("value of '%s' has to be an object: { }" % key,
                                self._lint_value_of_key(key))
                return False

        if validator == int:
            if type(uservalue) != int:
                self._hard_error("value of '%s' has to be a integer" % key,
                                self._lint_value_of_key(key))
                return False

        if validator == float:
            if not (type(uservalue) == int or type(uservalue) == float):
                self._hard_error("value of '%s' has to be a number" % key,
                                self._lint_value_of_key(key))
                return False

        # regex
        if type(validator) == str:
            if type(uservalue) != str:
                self._hard_error("value of '%s' has to be a string" % key,
                                self._lint_value_of_key(key))
                return False
            else:
                m = re.match(validator, uservalue)
                if m is None:
                    self._soft_error("value of '%s' should match regex %s" %
                                                (key, validator),
                                    self._lint_value_of_key(key))
                    return False

        # list of string values
        if type(validator) == list:
            if type(uservalue) != str:
                self._hard_error("value of '%s' has to be a string" % key,
                                self._lint_value_of_key(key))
                return False
            else:
                if uservalue not in validator:
                    self._soft_error("value of '%s' should be one of %s" %
                                                (key, validator),
                                    self._lint_value_of_key(key))
                    return False
        return True


    def _check_files_are_strings(self):
        """
            Checks if all files are Strings. > SoftError
            Checks if all filesGlobs are Strings. > HardError (because then
            expandGlob will not work)
        """
        if "files" in self.tsconfig:
            for file_ in self.tsconfig["files"]:
                if type(file_) is not str:
                    self._soft_error("all files have to be strings",
                                    self._lint_value_of_key("files"))
                    break

        if "filesGlob" in self.tsconfig:
            for glob_ in self.tsconfig["filesGlob"]:
                if type(glob_) is not str:
                    self._hard_error("all filesGlobs have to be strings",
                                    self._lint_value_of_key("filesGlob"))
                    break


    # ######################################################################
    # ###############            LINT FILES (exist, extension)    ##########
    # ######################################################################


    def _check_files_exist(self):
        """ Checks if the files exist > SoftError.
            Does nothing if to much files are listed. """

        if "files" in self.tsconfig:
            if len(self.tsconfig["files"]) > 1000:
                return

            for file_ in self.tsconfig["files"]:
                file_path = os.path.join(self.tsconfigdir, file_)
                if not os.path.isfile(file_path):
                    self._soft_error("file %s does not exist or is not a file"
                                     % file_,
                                     self._lint_string_value(file_))

    def _check_files_are_ts_files(self):
        """ Checks for file extension .ts > SoftError """

        if "files" in self.tsconfig:
            for file_ in self.tsconfig["files"]:
                if not file_.endswith('.ts'):
                    self._soft_error("file %s is no .ts file" % file_,
                                    self._lint_string_value(file_))


    # ######################################################################
    # ###############              LINT HELPERS                   ##########
    # ######################################################################


    def _lint_key(self, keyname):
        """ Simple string search for keyname in parenteses, lint that key.
            Returns the position (sublime.Region) of that lint """

        quote_style_2 = self.content.find('"%s"' % keyname)
        if quote_style_2 != -1:
            return self._lint_range(quote_style_2 + 1, len(keyname))

        quote_style_1 = self.content.find("'%s'" % keyname)
        if quote_style_1 != -1:
            return self._lint_range(quote_style_1 + 1, len(keyname))

    def _lint_string_value(self, value):
        """ Simple string search for value in parenteses, lint that value.
            Returns the position (sublime.Region) of that lint """

        quote_style_2 = self.content.find('"%s"' % value)
        if quote_style_2 != -1:
            return self._lint_range(quote_style_2 + 1, len(value))

        quote_style_1 = self.content.find("'%s'" % keyname)
        if quote_style_1 != -1:
            return self._lint_range(quote_style_1 + 1, len(value))


    def _lint_value_of_key(self, keyname):
        """
            Simple string search for keyname in parenteses, lint the
            value of that key.
            Returns the position (sublime.Region) of that lint
        """

        keypos = self.content.find("'%s'" % keyname)
        if keypos == -1:
            keypos = self.content.find('"%s"' % keyname)
        if keypos == -1:
            return

        # set pointer to end of key
        p = keypos + len(keyname) + 2

        # find :
        while self.content[p] != ":" and p < self.len - 1:
            p += 1

        return self._lint_range(p + 1, 3)


    def _lint_range(self, char, length=0):
        """ Lints from position char.
            Returns the position (sublime.Region) of that lint """

        if length == 0:
            region = sublime.Region(
                        char - 2 if char >= 2            else 0,
                        char + 2 if char <= self.len - 2 else self.len)
        else:
            region = sublime.Region(char, char + length)
        self.error_regions.append(region)
        return (region.a, region.b)


