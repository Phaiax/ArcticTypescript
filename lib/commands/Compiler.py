# coding=utf8

from subprocess import Popen, PIPE
from threading import Thread
try:
	from queue import Queue
except ImportError:
	from Queue import Queue

import sublime
import os
import json

from ..utils import package_path, Debug
from ..utils.osutils import get_kwargs
from ..utils.pathutils import get_tsc_path

from ..display.Panel import PANEL

# ----------------------------------------- UTILS --------------------------------------- #

def show_output(window,line):
	PANEL.show(window)
	PANEL.update(line['output'].replace('[end]','\n'))
	window.run_command('typescript_build_view',{"filename":line['output'].replace('[end]','\n')})

def show_view(window,line):
	window.run_command('typescript_build_view',{"filename":line['filename'].replace('\n','')})



# --------------------------------------- COMPILER -------------------------------------- #

class Compiler(Thread):

	def __init__(self, project, window_for_panel):
		window_for_panel = window
		self.project = project
		Thread.__init__(self)

	def run(self):
		Debug('build', 'BUILD INITIALIZED')

		node_path, cwd, cmdline = self._make_commandline()
		kwargs = get_kwargs()

		PANEL.clear(window_for_panel)


		Debug('build', 'EXECUTE: %s' % str(cmd))
		p = Popen(cmd, stdin=PIPE, stdout=PIPE, **kwargs)


		reader = CompilerReader(window_for_panel, p.stdout, Queue())
		reader.daemon = True
		reader.start()


	def _make_commandline(self):
		""" generates the commandline to start either tss.js or tsserver.js,
			depending on the project settings """
		node_path = default_node_path(self.project.get_setting('node_path'))
		tsc_path = get_tsc_path()

		cwd = os.path.abspath(self.project.tsconfigdir)
		rootfile = self.project.get_first_file_of_tsconfigjson()
		cmd = [node, os.path.join(package_path,'bin','build.js'), settings, self.root, self.filename]

		cmdline = [node_path, tss_path, "--project", cwd, rootfile]

		return node_path, cwd, cmdline



class CompilerReader(Thread):

	def __init__(self,window,stdout,queue):
		window_for_panel = window
		self.stdout = stdout
		self.queue = queue
		Thread.__init__(self)

	def run(self):
		Debug('build+', 'BUILD RESULTS READER THREAD started')
		for line in iter(self.stdout.readline, b''):
			Debug('build+', 'BUILD RESULTS: %s' % line)
			try:
				line = json.loads(line.decode('UTF-8'))
			except ValueError as v:
				print('ArcticTypescript ERROR: NON JSON ANSWER from build.js: %s' % line.decode('UTF-8'))
				print('ArcticTypescript: compiler error')
				break
			if 'output' in line:
				show_output(window_for_panel,line)
			elif 'filename' in line:
				show_view(window_for_panel,line)
			else:
				print('ArcticTypescript: compiler error')
		Debug('build+', 'BUILD RESULTS READER THREAD finished')
		self.stdout.close()

