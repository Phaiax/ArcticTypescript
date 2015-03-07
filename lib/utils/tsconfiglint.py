# coding=utf8

import sublime
import json
import os
import re

from .debug import Debug
from .CancelCommand import catch_CancelCommand, CancelCommand
from .fileutils import read_file
from .pathutils import package_path
from .viewutils import get_content

from .options import allowed_compileroptions, allowed_settings, \
					 compileroptions_validations, settings_validations


empty_tsconfig = {
	"compilerOptions": {},
	"files": []
}




def is_tsconfig(view):
	return view and view.file_name() \
		and os.path.basename(view.file_name()) == "tsconfig.json"


@catch_CancelCommand
def check_tsconfig(view):
	""" Reads the tsconfig.json and checks for errors """

	if not is_tsconfig(view):
		return

	if not view.is_valid() or view.is_loading():
		return

	Debug('tsconfig', 'tsconfig modified, check')
	TsconfigLinter(view)


class TsconfigLinter(object):


	def __init__(self, view):
		self.view = view
		self.error_regions = []
		self.tsconfig = None
		self.msg, self.line, self.col, self.char = None, None, None, None
		self.numerrors = 0
		self.linted = False

		self._read_file()
		self._check_empty()
		if not self._check_jsonsyntax():
			if self._check_root_dicts():
				self._check_key_spellings()
				self._check_unknown_keys()
				self._validate_values()
				seff._check_files_are_strings()

		self._add_regions()
		self.linted = True


	def _read_file(self):

		self.content = get_content(self.view) #read_file(view.file_name())
		self.len = len(self.content)

		if self.content is None:
			self.numerrors += 1
			raise CancelCommand()

	def _check_empty(self):
		if self.content == "":
			Debug('tsconfig', 'put default empty base structure to tsconfig.json')
			self.view.run_command('append', {'characters':
					json.dumps(empty_tsconfig, indent=4)})
			raise CancelCommand()

	def _check_jsonsyntax(self):
		try:
			self.tsconfig = json.loads(self.content)
		except ValueError as e:
			Debug('tsconfig', 'json error %s %s' % (type(e), e))

			self._parse_jsonerror(e.args[0])

			if self.msg is None:
				Debug('tsconfig.json', 'json error %s' % e)
				self.numerrors += 1
				raise CancelCommand()

			self._lint_char(self.char)
			self.numerrors += 1
			Debug('tsconfig.json', "%s (Line %i Column %i)" % (self.msg, self.line, self.col))

			return True

		except Exception as e:
			Debug('tsconfig', 'unexpected json.loads() error %s %s' % (type(e), e))
			self.numerrors += 1
			raise CancelCommand()
		return False


	def _lint_char(self, char, length=0):
		if length == 0:
			self.error_regions.append(sublime.Region(
								char - 2 if char >= 2 		   else 0,
								char + 2 if char <= self.len - 2 else self.len))
		else:
			self.error_regions.append(sublime.Region(char, char + length))


	def _check_key_spellings(self):

		# check for spelling
		self._expect_key_of_obj_to_be_y(self.tsconfig, "compilerOptions")
		self._expect_key_of_obj_to_be_y(self.tsconfig, "files")
		self._expect_key_of_obj_to_be_y(self.tsconfig, "filesGlob")
		self._expect_key_of_obj_to_be_y(self.tsconfig, "ArcticTypescript")


	def _check_root_dicts(self):
		if type(self.tsconfig) != dict:
			self._lint_char(0, self.len - 1)
			self.numerrors += 1
			Debug('tsconfig.json', "root structure must be an object: { }")
			return False


		valid = self._execute_validator(dict, self.tsconfig, 'compilerOptions'), \
				self._execute_validator(list, self.tsconfig, 'files'), \
				self._execute_validator(list, self.tsconfig, 'filesGlob')\
				self._execute_validator(dict, self.tsconfig, 'ArcticTypescript')

		return all(valid)

	def _check_unknown_keys(self):

		if "compilerOptions" in self.tsconfig:
			for option in self.tsconfig["compilerOptions"].keys():
				if option not in allowed_compileroptions:
					self.numerrors += 1
					Debug('tsconfig.json', "unknown key '%s' in compilerOptions" % option)
					self._lint_key(option)

		if "ArcticTypescript" in self.tsconfig:
			for option in self.tsconfig["ArcticTypescript"].keys():
				if option not in allowed_settings:
					self.numerrors += 1
					Debug('tsconfig.json', "unknown key '%s' in ArcticTypescript" % option)
					self._lint_key(option)


	def _validate_values(self):

		if "compilerOptions" in self.tsconfig:
			for key, validator in compileroptions_validations.items():
				self._execute_validator(validator, self.tsconfig["compilerOptions"], key)

		if "ArcticTypescript" in self.tsconfig:
			for key, validator in settings_validations.items():
				self._execute_validator(validator, self.tsconfig["ArcticTypescript"], key)



	def _execute_validator(self, validator, dict_with_uservalue, key):
		if key not in dict_with_uservalue:
			return True
		uservalue = dict_with_uservalue[key]
		# type
		if validator == str:
			if type(uservalue) != str:
				self.numerrors += 1
				Debug('tsconfig.json', "value of '%s' has to be a string" % key)
				self._lint_value_of_key(key)
				return False

		if validator == list:
			if type(uservalue) != list:
				self.numerrors += 1
				Debug('tsconfig.json', "value of '%s' has to be a list" % key)
				self._lint_value_of_key(key)
				return False

		if validator == bool:
			if type(uservalue) != bool:
				self.numerrors += 1
				Debug('tsconfig.json', "value of '%s' has to be true or false" % key)
				self._lint_value_of_key(key)
				return False

		if validator == dict:
			if type(uservalue) != dict:
				self.numerrors += 1
				Debug('tsconfig.json', "value of '%s' has to be an object: { }" % key)
				self._lint_value_of_key(key)
				return False

		# regex
		if type(validator) == str:
			if type(uservalue) != str:
				self._lint_value_of_key(key)
				self.numerrors += 1
				Debug('tsconfig.json', "value of '%s' has to be a string" % key)
				return False
			else:
				m = re.match(validator, uservalue)
				if m is None:
					self.numerrors += 1
					Debug('tsconfig.json', "value of '%s' should match regex %s" %
						(key, validator))
					self._lint_value_of_key(key)
					return False

		# list of string values
		if type(validator) == list:
			if type(uservalue) != str:
				self.numerrors += 1
				Debug('tsconfig.json', "value of '%s' has to be a string" % key)
				self._lint_value_of_key(key)
				return False
			else:
				if uservalue not in validator:
					self.numerrors += 1
					Debug('tsconfig.json', "value of '%s' should be one of %s" %
						(key, validator))
					self._lint_value_of_key(key)
					return False
		return True


	def _check_files_are_strings(self):
		if "files" in self.tsconfig:
			for file_ in self.tsconfig["files"]:
				if type(file_) is not str:
					self.numerrors += 1
					self._lint_value_of_key("files")
					Debug('tsconfig.json', "all files have to be strings")
					break

		if "filesGlob" in self.tsconfig:
			for glob_ in self.tsconfig["filesGlob"]:
				if type(glob_) is not str:
					self.numerrors += 1
					self._lint_value_of_key("filesGlob")
					Debug('tsconfig.json', "all filesGlobs have to be strings")
					break



	def _add_regions(self):

		self.view.add_regions('tsconfig-error', self.error_regions,
						 'invalid', 'dot', sublime.DRAW_NO_FILL)


	def _expect_key_of_obj_to_be_y(self, obj, y):
		key_found = False
		for k in obj.keys():
			if k.lower() == y.lower():
				key_found = True

				if k == y:
					return

				self.numerrors += 1
				Debug('tsconfig.json', "key '%s' is spelled wrong" %
						(key, validator))

				self._lint_key(k)
		return key_found


	def _lint_key(self, keyname):
		quote_style_1 = self.content.find("'%s'" % keyname)
		quote_style_2 = self.content.find('"%s"' % keyname)

		if quote_style_1 != -1:
			self._lint_char(quote_style_1 + 1, len(keyname))

		if quote_style_2 != -1:
			self._lint_char(quote_style_2 + 1, len(keyname))


	def _lint_value_of_key(self, keyname):
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

		self._lint_char(p + 1, 3)




	def _parse_jsonerror(self, error):
		try:
			self.msg, line, col, char = re.match(
			'([^:]*): line ([\d]+) column ([\d]+) \(char ([\d]+)\)', error).groups()
		except Exception:
			return

		self.line = int(line)
		self.col = int(col)
		self.char = int(char)

		if str(self.line) != line \
				or str(self.col) != col \
				or str(self.char) != char:
			self.msg, self.line, self.col, self.char = None, None, None, None





#<class 'ValueError'> Expecting property name enclosed in double quotes: line 2 column 25 (char 26)
#<class 'ValueError'> Expecting ':' delimiter: line 2 column 27 (char 28)
#<class 'ValueError'> Expecting object: line 2 column 28 (char 29)
#<class 'ValueError'> Expecting property name enclosed in double quotes: line 2 column 31 (char 32)
#<class 'ValueError'> Expecting object: line 3 column 15 (char 48)
