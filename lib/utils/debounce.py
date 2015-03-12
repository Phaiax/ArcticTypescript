# coding=utf8

import threading

from ..system.globals import debounced_timers


DEFAULT_DEBOUNCE_DELAY = 0.2 # Will also be used for AsyncCommand debounce


# DEBOUNCE CALL
def debounce(fn, delay=DEFAULT_DEBOUNCE_DELAY, uid=None, *args):
    uid = uid if uid else fn

    if uid in debounced_timers:
        debounced_timers[uid].cancel()

    timer = threading.Timer(delay, fn, args)
    timer.start()

    debounced_timers[uid] = timer
