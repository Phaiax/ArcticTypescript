# coding=utf8

from .debug import Debug

# CANCEL COMMAND EXCEPTION
class CancelCommand(Exception):
	""" Throw this exception in a command. The decorator
		catch_CancelCommand will catch it and cancel silently """
	pass

# CANCEL COMMAND EXCEPTION CATCHER DECORATOR
def catch_CancelCommand(func):
	""" Decorate every command with this one. It will check for
		the plugin disabled flag and catch CancelCommand exceptins. """

	def catcher(*kargs, **kwargs):
		if is_plugin_temporarily_disabled():
			return # do not execute command
		try:
			func(*kargs, **kwargs)
		except CancelCommand:
			Debug('command', "A COMMAND WAS CANCELED")
			pass
	return catcher