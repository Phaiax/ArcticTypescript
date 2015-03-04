# coding=utf8

import sublime

if int(sublime.version()) >= 3000:
	from .lib.Commands import *
	from .lib.Listener import TypescriptEventListener, init
	from .lib.display.T3SViews import TypescriptEventListener2

	def plugin_loaded():
		sublime.set_timeout(lambda:init(sublime.active_window().active_view()), 300)

		# Testing (Only executes if we have opened the TDDTesting project)
		# Use filepattern to select tests. Examples: '*foo*', 'test_foo.py'
		run_tests(filepattern='*utils*') #


	def plugin_unloaded():
		pass


	def run_tests(filepattern=''):
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
