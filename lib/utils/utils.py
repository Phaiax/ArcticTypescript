# coding=utf8

import sublime
import time
import hashlib


# ##################################################### VERSION ############


version = int(sublime.version())


# ##################################################### BYTE/STRING utils ##


def encode(message):
    return bytes(message,'UTF-8')


def make_hash(value):
    """ Returns md5 hash of <value>. """
    return hashlib.md5(encode(value)).hexdigest()


def random_str():
    """ Returns a random string, made out of the current time """
    return make_hash(str(time.time()))


def replace_variables(value, variables):
    if hasattr(sublime, 'expand_variables'): # ST3, Build 3068
        # stringify dict
        for k in variables.keys():
            variables[k] = str(variables[k]);
        return sublime.expand_variables(value, variables)
    else:
        # sort keys after length, to get $file_path before $file
        keys = list(variables.keys())
        keys.sort(key=len, reverse=True)
        for k in keys:
            key = "${%s}" % k
            if key in value:
                value = value.replace(key, str(variables[k]))
    return value


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

        if obj is None:
            raise KeyError()
    except:
        raise KeyError(str(selector))


