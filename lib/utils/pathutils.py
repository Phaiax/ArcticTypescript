# coding=utf8

import os
import sys

from .fileutils import file_exists

# PACKAGE PATH
package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


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


# GET TSS PATH
def get_tss_path():
	""" Return path to tss.js """
	return os.path.join(package_path, 'bin', 'tss.js')


def default_node_path(node_path):

	if node_path == 'none':
		print('ArcticTypescript: The setting node_path is set to "none". That is depreciated. Remove the setting.')

	if node_path == 'none' or node_path == "" or node_path == None:
		return '/usr/local/bin/node' if sys.platform == "darwin" else 'nodejs'
	else:
		return node_path
