# coding=utf8

import os
import glob
import json
from subprocess import Popen, PIPE, TimeoutExpired
from .TsconfigLinter import check_tsconfig

# from pathlib import Path # not avalilable in python 3.3 (only 3.4)
from ..utils.debug import Debug
from ..utils.pathutils import get_expandglob_path, default_node_path
from ..utils.osutils import get_kwargs
from ..utils.disabling import set_tsglobexpansion_disabled, set_tsglobexpansion_enabled, is_tsglobexpansion_disabled


# Expanding is now done via javascript expandglob.js
# There are too many differences between the glob implementations, and pathutils
# are not available for now
# Second reason for pure js solution: python shuffles the dicts keys in each iteration
#
# [1] https://github.com/TypeStrong/atom-typescript/issues/172
# [2] https://github.com/TypeStrong/atom-typescript/blob/master/docs/tsconfig.md
# [3] https://github.com/TypeStrong/atom-typescript/blob/master/lib/main/tsconfig/tsconfig.ts
# [4] https://github.com/anodynos/node-glob-expand/blob/master/source/code/expand.coffee


def expand_filesglob(linter):
    """
        This mimics the filesGlob behaviour of atom-typescript [2]
        If tsconfig.json has no HardErrors, it executes bin/expandglob.js
        and reloads linter.view from disk.
        This operates on the file contents, so the file should have been saved
        before.
        Returns immediately if not linted or linter is None
        Returns True if the filesGlob has been expanded
        Returns False if there was a linter error, so no expansion has been done
    """

    # Expanding?

    if is_tsglobexpansion_disabled():
        return False

    if linter is None or not linter or not linter.linted:
        return False

    if len(linter.harderrors) > 0:
        return False

    if len(linter.softerrors) != linter.numerrors:
        return False

    if linter.content == "":
        return False

    if "filesGlob" not in linter.tsconfig:
        return True # Should reopen project, so return True here

    # Expand!
    project_dir = os.path.dirname(linter.view.file_name())
    file_list = _expand_globs_with_javascript(project_dir, linter)
    Debug("tsconfig.json", "fileGlobs expaned")

    # reload file
    linter.view.run_command("revert")

    # lint again, so the soft errors are still displayed
    check_tsconfig(linter.view)

    return True


def _expand_globs_with_javascript(project_dir, linter):
    """ use the nodejs script bin/expandglob.js to expand the glob entries in
        the already saved file tsconfig.json in project_dir.
        Returns the files list, but also CHANGES THE DISK CONTENTS.
        We use javascript here, because python shuffles the dicts keys in each
        iteration """

    try:
        node_path = None
        if "ArcticTypescript" in linter.tsconfig:
            if "node_path" in linter.tsconfig["ArcticTypescript"]:
                node_path = linter.tsconfig["ArcticTypescript"]["node_path"]

        node_path = default_node_path(node_path)

        expandglob_path = get_expandglob_path()
        cwd = os.path.abspath(project_dir)

        cmdline = [node_path, expandglob_path]

        kwargs = get_kwargs()

        try:
            # EXECUTE
            expand_glob_process = Popen(cmdline,
                                     stdin=PIPE, stdout=PIPE,
                                     cwd=cwd, **kwargs)
            # FETCH and terminate
            result_str, _err = expand_glob_process.communicate(timeout=10)

            # PARSE
            result = json.loads(str(result_str.decode('UTF-8')))

            # CHECK (only for error Display)
            if "error" in result and isinstance(result['error'], str):
                Debug('error', 'expandglob.js: %s' % result['error'])
            #elif "error" in result and "files" in result \
            #         and result['error'] == False:
            #    return result['files']

        except TimeoutExpired:
            expand_glob_process.kill()
            outs, errs = expand_glob_process.communicate()
            Debug('notify', 'expandglob.js: Timeout')

        except Exception as e:
            Debug('notify', 'expandglob: %s' % e)

    except FileNotFoundError:
        Debug('error', "\n".join(["Could not find nodejs.",
                "I have tried this path: %s" % node_path,
                "Please install nodejs and/or set node_path in the project or plugin settings to the actual executable.",
                "If you are on windows and just have installed node, you first need to logout and login again."]))
        return None

