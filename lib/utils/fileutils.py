# coding=utf8

import os
import codecs
import hashlib
import json



# IS A TYPESCRIPT DEFINITION FILE
def is_dts(view):
    return view.file_name() and view.file_name().endswith('.d.ts')


# IS A TYPESCRIPT FILE
def is_ts(view):
    if view is None:
        return False
    fn = view.file_name()
    fn2 = view.file_name()
    fn3 = view.file_name()
    if fn is None or fn2 is None:
        return False
    if fn is None or fn2 is None or fn3 is None:
        pass
        #import spdb ; spdb.start()
    return fn.endswith('.ts') and not fn.endswith('.d.ts')


# READ FILE
def read_file(filename):
    """ returns None or file contents if available """
    filename = os.path.normcase(filename) # back to \\ in nt
    if os.path.isfile(filename):
        try:
            if os.name == 'nt':
                return open(filename, 'r', encoding='utf8').read()
            else:
                return codecs.open(filename, 'r', 'utf-8').read()
        except IOError:
            pass
    return None


# MAKE MD5 of disk contents of file
def hash_file(filename, blocksize=65536):
    f = open(filename)
    buf = f.read(blocksize)
    hasher = hashlib.md5()
    while len(buf) > 0:
        hasher.update(encode(buf))
        buf = f.read(blocksize)
    f.close()
    return hasher.hexdigest()


def read_and_decode_json_file(filename):
    """ returns None or json-decoded file contents as object,list,... """
    f = read_file(filename)
    return json.loads(f) if f is not None else None

# FILE EXISTS
def file_exists(filename):
    """ returns weather the file exists """
    return os.path.isfile(os.path.normcase(filename))



# FILENAME transformations
def filename2linux(filename):
    """ returns filename with linux slashes. Also makes normcase before!
        (Windows: normcase: /->\\ and lowercase), then back to / """
    return os.path.normcase(filename).replace('\\','/')


def filename2key(filename):
    """ returns the unified version of filename which can be used as dict key """
    return filename2linux(realfn(filename)).lower()


def fn2k(filename):
    """ shortcut for filename2key """
    return filename2key(filename)


def fn2l(filename):
    """ shortcut for filename2linux """
    return filename2linux(filename)


def realfn(filename):
    """ Returns the filename while resolving relative paths. (Tsserver is using
        those resolved paths now.) """
    return os.path.realpath(filename)
