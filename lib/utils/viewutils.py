# coding=utf8

import sublime


# GET VIEW CONTENT
def get_content(view):
	return view.substr(sublime.Region(0, view.size()))

def get_content_of_line_at(view, pos):
	return view.substr(sublime.Region(view.line(pos-1).a, pos))




# GET LINES
def get_lines(view):
	(lines, col) = view.rowcol(view.size())
	return lines


# GET FILE INFO
def get_file_infos(view):
	return (view.file_name(), get_lines(view), get_content(view))

# RUN COMMAND
def run_command_on_any_ts_view(command, args=None):
	v = get_any_ts_view()
	if v is not None:
		v.run_command(command, args)

# TS VIEW
def get_any_ts_view():
	v = sublime.active_window().active_view()
	if is_ts(v) and not is_dts(v):
		return v
	for w in sublime.windows():
		for v in w.views():
			if is_ts(v) and not is_dts(v):
				return v

def get_any_view_with_root(root):
	return
	from .system.Liste import get_root
	v = sublime.active_window().active_view()
	if is_ts(v) and not is_dts(v) and get_root(v.file_name()) == root:
		return v
	for w in sublime.windows():
		for v in w.views():
			if is_ts(v) and not is_dts(v) and get_root(v.file_name()) == root:
				return v


