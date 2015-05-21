# coding=utf8

import sys
from functools import wraps


# Use this to start a visual debugger (PluginDebugger (a sublime plugin) and
# winpdb must be installed)
# import spdb ; spdb.start()

# Commands for python console
#   import ArcticTypescript.lib as a
# first project:
#   p = a.system.globals.OPENED_PROJECTS.values().__iter__().__next__()
# print indexed files:
#   p.tsserver.get_tss_indexed_files(lambda a:print(a))
#   p.tsserver.dump("c:/users/danie_000/amd_modules_with_tests/src/app.ts", 'C:/users/danie_000/dump3.txt', print)
# error recalculation:
#   p.tsserver.executed_with_most_recent_file_contents = []
#   p.errors.start_recalculation()
# p.tsserver.reload()

# TypescriptToolsWrapper.eva() -> evaluates javascript command in tss.js
#   p.tsserver.eva('_this')
#   p.tsserver.last_eva
# But needs this code in tss.js (add manually below the command checks before using eva() for debugging)
#                else if (m = match(cmd, /^eva ([\s\S]*)$/)) {
#                    if (m[1]) {
#                        var res = eval(m[1]);
#                        res = JSON.stringify(res); //.replace(/\n/g, '<br>').replace(/"/g, '\'');
#                        _this.outputJSON('' + res + '');
#                    }
#                    else
#                        _this.outputJSON('"no input"');
#                }


# ####################### DEFINE LIST OF DISPLAYED DEBUG MESSAGES ##############

# notify, tsconfig.json and error should be enabled in production
print_classifications = ['notify', 'error', 'tsconfig.json']


# ####################### Possible classifications #############################

possible_classifications = [ 'all', 'notify', 'error',
    'tss', 'tss+', 'tss++',
    'command', 'command+',
    'adapter', 'adapter+',
    'files',
    'build', 'build+',
    'structure',
    'refactor',
    'autocomplete',
    'errorpanel', 'errorpanel+',
    'focus', 'max_calls',
    'layout',
    'goto',
    'project', 'project+',
    'tsconfig', 'tsconfig.json']


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