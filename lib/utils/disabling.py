# coding=utf8

import sublime
import os

from .debug import Debug

from ..system.globals import plugin_disabled_for_folders

# ############## Allows Disabling of ArcticTypescript ######################


# has a global variable in globals.py


def is_plugin_globally_disabled():
	return "*global" in plugin_disabled_for_folders

def is_plugin_temporarily_disabled(folder=None):
	""" Returns True if the plugin is disabled globally or for folder.
		Folder can be a view """
	if is_plugin_globally_disabled() or folder is None:
		return is_plugin_globally_disabled()
	if folder is not None and isinstance(folder, sublime.View):
		if folder.file_name() is None:
			return is_plugin_globally_disabled()
		folder = os.path.dirname(folder.file_name())
	folder = os.path.normcase(folder)
	return folder in plugin_disabled_for_folders


def set_plugin_temporarily_enabled(folder=None):
	""" Disables the plugin globally or for folder.
		Folder can be a view """
	if folder is None and is_plugin_globally_disabled():
		plugin_disabled_for_folders.remove("*global")
	else:
		if isinstance(folder, sublime.View):
			folder = os.path.dirname(folder.file_name())
		folder = os.path.normcase(folder)
		Debug('project', 'Enable ArcticTypescript for %s' % folder)
		if folder in plugin_disabled_for_folders:
			plugin_disabled_for_folders.remove(folder)


def set_plugin_temporarily_disabled(folder=None):
	""" Enables the plugin globally or for folder.
		Folder can be a view """
	if folder is None and not is_plugin_globally_disabled():
		plugin_disabled_for_folders.append("*global")
	else:
		if isinstance(folder, sublime.View):
			folder = os.path.dirname(folder.file_name())
		folder = os.path.normcase(folder)
		Debug('project', 'Disable ArcticTypescript for %s' % folder)
		if folder not in plugin_disabled_for_folders:
			plugin_disabled_for_folders.append(folder)