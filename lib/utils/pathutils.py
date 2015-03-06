# coding=utf8

import os
import sys

from .fileutils import file_exists
from .utils import replace_variables


# PACKAGE PATH
package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def add_usr_local_bin_to_path_on_osx():
	""" Adds /usr/local/bin to path on mac osx, because that is
		where nodejs lives """
	if os.environ.get('PATH') and sys.platform == 'darwin':
		if '/usr/local/bin' in os.environ.get('PATH').split(':'):
			os.environ['PATH'] = os.environ.get('PATH') + ":'/usr/local/bin'"

def find_tsconfigdir(rootdir):
	""" Returns the normalized dir, in which the tsconfig.json file is located"""
	rootdir = os.path.abspath(rootdir)
	try:
		if file_exists(os.path.join(rootdir, "tsconfig.json")):
			return os.path.normcase(rootdir)
	except FileNotFoundError:
		pass

	parentdir = os.path.abspath(os.path.join(rootdir, os.pardir))
	if parentdir == rootdir:
		return None
	else:
		return find_tsconfigdir(parentdir)


def expand_variables(path, project=None, use_cache=False):
	variables = {}
	if project is not None:
		variables.update(project.extract_variables(use_cache))
	return replace_variables(path, variables)


# GET TSS PATH
def get_tss_path():
	""" Return path to tss.js """
	return os.path.join(package_path, 'bin', 'tss.js')


def default_node_path(node_path, project=None):
	if node_path == 'none':
		print('ArcticTypescript: The setting node_path is set to "none". That is depreciated. Remove the setting.')
		node_path = None

	if node_path == "" or node_path is None:
		return "nodejs"
		#return '/usr/local/bin/node' if sys.platform == "darwin" else 'nodejs'
	else:
		return expand_variables(node_path, project)


def default_tsc_path(tsc_path=None, project=None):
	if tsc_path is not None and tsc_path:
		tsc_path = expand_variables(tsc_path, project)
		return tsc_path

	# search node_modules
	if project:
		node_modules_dir = search_node_modules(project.tsconfigdir)
		if node_modules_dir:
			tsc_path = os.path.join(node_modules_dir, ".bin", "tsc")
			if file_exists(tsc_path):
				return os.path.normcase(tsc_path)

	# use ArcticTypescript's tsc
	return os.path.join(package_path, 'bin', 'node_modules', '.bin', 'tsc')



def search_node_modules(rootdir):
	rootdir = os.path.abspath(rootdir)
	try:
		if os.path.isdir(os.path.normcase(os.path.join(rootdir, "node_modules"))):
			return os.path.normcase(rootdir)
	except FileNotFoundError:
		pass

	parentdir = os.path.abspath(os.path.join(rootdir, os.pardir))
	if parentdir == rootdir:
		return None
	else:
		return search_node_modules(parentdir)
