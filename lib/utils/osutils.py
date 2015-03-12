# coding=utf8

import os
import subprocess

# GET PROCESS KWARGS
def get_kwargs(stderr=True):
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if stderr:
            #errorlog = open(os.devnull, 'w')
            return {'stderr':subprocess.DEVNULL, 'startupinfo': startupinfo}
        return {'startupinfo': startupinfo}
    else:
        return {}