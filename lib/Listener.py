# coding=utf8

import sublime
import sublime_plugin

from .display.T3SViews import T3SVIEWS

from .system.Project import OpenedProject, get_or_create_project_and_add_view

from .utils import Debug, max_calls
from .utils.viewutils import run_command_on_any_ts_view
from .utils.fileutils import file_exists


# ------------------------------------------- EVENTS ------------------------------------------ #


@max_calls()
def on_init(root):
	pass
	#TSS.removeEventListener('init', root, on_init)
	#FILES.init(root, on_files_loaded)

@max_calls()
def on_files_loaded():
	pass
	# we don't know if a ts view is activated, start conditions
	#run_command_on_any_ts_view('typescript_update_structure', {"force": True})
	#run_command_on_any_ts_view('typescript_recalculate_errors')


@max_calls()
def on_kill(root):
	pass
	#TSS.removeEventListener('kill', root, on_kill)
	#FILES.remove_by_root(root)
	#ERRORS.on_close_typescript_project(root)
	#T3SVIEWS.hide_all()




# ----------------------------------------- LISTENERS ---------------------------------------- #

class TypescriptEventListener(sublime_plugin.EventListener):

	# CLOSE FILE
	@max_calls(name='Listener.on_close')
	def on_close(self, view):
		project = get_or_create_project_and_add_view(view, wizzard=False)
		if project:
			project.close(view)


	# FILE ACTIVATED
	@max_calls()
	def on_activated(self, view):
		get_or_create_project_and_add_view(view)


	# ON CLONED FILE
	@max_calls()
	def on_clone(self, view):
		get_or_create_project_and_add_view(view)


	# ON SAVE
	@max_calls()
	def on_post_save(self, view):
		return
		project = get_or_create_project_and_add_view(view)
		if project:
			# TODO
			filename, num_lines, content = get_file_infos(view)
			if LISTE.has(filename):
				TSS.update(filename, num_lines, content)
				FILES.update(filename, num_lines, content, True)

			view.run_command('typescript_update_structure', {"force": True})
			ERRORS.start_recalculation(view.file_name())

			if get_root(filename) and SETTINGS.get('build_on_save', get_root(filename)):
				sublime.active_window().run_command('typescript_build',{"characters":False})


	# ON CLICK
	@max_calls(name='listener.on_selection_modified')
	def on_selection_modified(self, view):
		return
		project = get_or_create_project_and_add_view(view)
		if project:

			ERRORSHIGHLIGHTER.display_error_in_status_if_cursor(view)
			view.erase_regions('typescript-definition')
			view.erase_regions('typescript-error-hint')


	# ON VIEW MODIFIED
	@max_calls()
	def on_modified(self, view):
		return
		project = get_or_create_project_and_add_view(view)
		if project:

			filename, num_lines, content = get_file_infos(view)
			if LISTE.has(filename):
				TSS.update(filename, num_lines, content)
				FILES.update(filename, num_lines, content)

			#view.run_command('typescript_update_structure', {"force": True})
			#typescript_update_structure(view, True)
			COMPLETION.trigger(view, TSS)

			if get_root(filename) and not SETTINGS.get('error_on_save_only', get_root(filename)):
				ERRORS.start_recalculation(view.file_name())


	# ON QUERY COMPLETION
	def on_query_completions(self, view, prefix, locations):
		return
		project = get_or_create_project_and_add_view(view)
		if project:
			pos = view.sel()[0].begin()
			(line, col) = view.rowcol(pos)
			Debug('autocomplete', "on_query_completions(), sublime wants to see the results, cursor currently at %i , %i (enabled: %s, items: %i)" % (line+1, col+1, COMPLETION.enabled_for['viewid'], len(COMPLETION.get_list()) ) )
			if is_ts(view) and not is_dts(view):
				if COMPLETION.enabled_for['viewid'] == view.id():
					COMPLETION.enabled_for['viewid'] = -1 # receive only once
					return (COMPLETION.get_list(), sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)


	# ON QUERY CONTEXT (execute commandy only on .ts files)
	def on_query_context(self, view, key, operator, operand, match_all):
		return
		if key == "ArcticTypescript":
			project = get_or_create_project_and_add_view(view)
			if project:
				view = sublime.active_window().active_view()
				return is_ts(view)


