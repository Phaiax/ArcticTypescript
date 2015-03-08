
import os
import glob
import json
from subprocess import Popen, PIPE, TimeoutExpired
from .TsconfigLinter import check_tsconfig

# from pathlib import Path
from ..utils.debug import Debug
from ..utils.pathutils import get_expandglob_path, default_node_path
from ..utils.osutils import get_kwargs
from ..utils.osutils import get_kwargs
from ..utils.disabling import set_tsglobexpansion_disabled, set_tsglobexpansion_enabled, is_tsglobexpansion_disabled

# This mimics the filesGlob behaviour of atom-typescript
#
# It processes filesGlob and writes the result to files
# Therby:
#    - one by one: glob -> union, !glob -> difference
#    - The patterns can be: "(sync) glob / minimatch / RegExp"
#        -
#
# https://github.com/TypeStrong/atom-typescript/blob/master/lib/main/tsconfig/tsconfig.ts
# https://github.com/anodynos/node-glob-expand/blob/master/source/code/expand.coffee

## TODO: TEST glob for **.ts -> causes InvalidPattern Exception



def expand_filesglob(linter):
    if is_tsglobexpansion_disabled():
        return

    if linter is None or not linter or not linter.linted:
        return

    if len(linter.harderrors) > 0:
        return

    if len(linter.softerrors) != linter.numerrors:
        return

    if linter.content == "":
        return

    if "filesGlob" not in linter.tsconfig:
        return
    project_dir = os.path.dirname(linter.view.file_name())

    #sel = _get_selection(linter.view)
    globs = linter.tsconfig['filesGlob']
    file_list = _expand_globs_with_javascript(project_dir, linter)
    # reload file
    linter.view.run_command("revert")
    Debug("tsconfig.json", "fileGlobs expaned")

    check_tsconfig(linter.view)

    #_load_selection(linter.view, sel)

    if file_list is None:
        return


    # pure js solution because python shuffles the dicts keys in each iteration

    # create new content for tsconfig
    # new_tsconf = linter.tsconfig.copy()
    # new_tsconf['files'] = file_list
    # new_content = json.dumps(new_tsconf, indent=4)

    #_replace_contents(linter.view, new_content)


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
            expand_glob_process = Popen(cmdline,
                                     stdin=PIPE, stdout=PIPE,
                                     cwd=cwd, **kwargs)

            result_str, _err = expand_glob_process.communicate(timeout=10)

            result = json.loads(str(result_str.decode('UTF-8')))


            if "error" in result and isinstance(result['error'], str):
                Debug('error', 'expandglob.js: %s' % result['error'])
            elif "error" in result and "files" in result \
                     and result['error'] == False:
                return result['files']

        except TimeoutExpired:
            expand_glob_process.kill()
            outs, errs = expand_glob_process.communicate()
            Debug('notify', 'expandglob.js: Timeout')
        except Exception as e:
            Debug('notify', 'expandglob: %s' % e)

        finally:
            pass
        return None



    except FileNotFoundError:
        Debug('error', "\n".join(["Could not find nodejs.",
                "I have tried this path: %s" % node_path,
                "Please install nodejs and/or set node_path in the project or plugin settings to the actual executable.",
                "If you are on windows and just have installed node, you first need to logout and login again."]))
        return None



#def _expand_globs_with_python(globs, project_dir):
#    files_list = []
#    old_cwd = os.path.abspath(os.curdir)
#
#    try:
#        os.chdir(project_dir)
#
#        for g in globs:
#            if g[0:1] != "!": # union
#                files_list.extend(_do_glob_variants(g))
#            else: # difference
#                files_to_remove = _do_glob_variants(g[1:])
#                files_list = [f for f in files_list if f not in files_to_remove]
#
#        # remove folders
#        file_list = [f for f in files_list if os.path.isfile(os.path.normcase(f))]
#
#
#    except:
#        pass
#    finally:
#        os.chdir(old_cwd)


def _get_selection(view):
    # store current cursor selection
    old_sel = view.sel()
    old_sel_regions = [old_sel[i] for i in range(0, len(old_sel))]
    print(old_sel_regions)
    return old_sel_regions


#def _replace_contents(view, new_content):
#    # replace content
#    set_tsglobexpansion_disabled()
#    view.run_command('select_all')
#    view.run_command('left_delete')
#    view.run_command('append', {'characters': new_content})
#    view.run_command('save')
#    set_tsglobexpansion_enabled()


def _load_selection(view, old_sel_regions):
    # reset selection
    sel = view.sel()
    sel.clear()
    sel.add_all(old_sel_regions)



#def _do_glob_variants(g):
#    # assume cwd is set
#    paths = []
#
#    p = Path('.')
#
#    _do_glob(g, paths)
#
#    g2 = g.replace('**', '**/*')
#    _do_glob(g2, paths)
#
#    g3 = g.replace('**', '*')
#    _do_glob(g3, paths)
#
#    g4 = g.replace('**/', '')
#    _do_glob(g3, paths)
#
#    g5 = g.replace('/**', '')
#    _do_glob(g3, paths)
#
#    # remove duplicates
#    paths = list(set(paths))
#
#    return paths
#
#
#def _do_glob(g, paths=None):
#    try:
#        new_paths = [sp.as_posix() for sp in p.glob(g) if sp.is_file()]
#    except ValueError as e:
#        pass
#
#    if paths is not None:
#        paths.extend(new_paths)
#    return new_paths
#
#    # glob.glob(g)



