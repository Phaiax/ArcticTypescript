# coding=utf8

import sublime
import time
import hashlib


# ##################################################### VERSION ############


version = int(sublime.version())


# ##################################################### BYTE utils #########


def encode(message):
	return bytes(message,'UTF-8')


def make_hash(value):
	""" Returns md5 hash of <value>. """
	return hashlib.md5(encode(value)).hexdigest()


def random_str():
	""" Returns a random string, made out of the current time """
	return make_hash(str(time.time()))

# ##################################################### LIST utils #########


def get_first(somelist, function):
	""" Returns the first item of somelist for which function(item) is True """
	for item in somelist:
		if function(item):
			return item
	return None


# ################################################### OBJECT utils #########


def get_deep(obj, selector):
	""" Returns the object given by the selector, eg a:b:c:1 for ['a']['b']['c'][1] """
	try:
		if type(selector) is str:
			selector = selector.split(':')

		if len(selector) == 0:
			return obj

		top_selector = selector.pop(0)

		if type(obj) is list:
			top_selector = int(top_selector)
			return get_deep(obj[top_selector], selector)

		if type(obj) is dict:
			return get_deep(obj[top_selector], selector)
	except:
		raise KeyError(str(selector))


