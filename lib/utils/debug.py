# coding=utf8

import sys
from functools import wraps


# ####################### DEFINE LIST OF DISPLAYED DEBUG MESSAGES ##############

print_classifications = ['project', 'project+']


# ####################### Possible classifications #############################

possible_classifications = [ 'all',
	'tss', 'tss+', 'tss++',
	'command', 'command+',
	'adapter', 'adapter+',
	'files',
	'build', 'build+',
	'structure',
	'autocomplete',
	'errorpanel', 'errorpanel+',
	'focus', 'max_calls',
	'layout',
	'goto',
	'project', 'project+']


# ####################### DEBUG logger #########################################


def Debug(classification, text):
	if 'all' in print_classifications or classification in print_classifications:
		print("ArcticTypescript: %s: %s" % (classification.ljust(8), text))
	if classification not in possible_classifications:
		print("ArcticTypescript: debug: got unknown debug message classification: %s. " \
			"Consider adding this to possible_classifications" % classification)
	sys.stdout.flush()


# ####################### log number of calls to funcitons #####################
# HELPER to hunt down memory leak

def max_calls(limit = 1500, name=""):
	"""Decorator which allows its wrapped function to be called `limit` times"""
	def decorator(func):
		# Disable limit:
		return func
		@wraps(func)
		def wrapper(*args, **kwargs):
			calls = getattr(wrapper, 'calls', 0)
			calls += 1
			setattr(wrapper, 'calls', calls)
			fname = name if name != "" else func.__name__

			if calls == limit + 1:
				Debug('max_calls', "LIMIT !! ## !!: Fkt %s has %i calls, stop" % (fname, calls - 1))

			if calls >= limit + 1:
				return None

			Debug('max_calls', "CALL: Fkt %s has %i calls -> +1" % (fname, calls - 1))

			return func(*args, **kwargs)
		setattr(wrapper, 'calls', 0)
		return wrapper
	return decorator