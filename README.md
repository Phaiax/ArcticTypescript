ArcticTypescript
================

 * Wizzard for project creation (create .ts file to activate).
 * syntax highlighting
 * auto completion
 * live error highlighting
 * fast access to errors via shortcuts and clicks
 * refactoring (beta)
 * jump to declaration
 * quick info
 * build system *for Typescript 1.5*
 * view build result.js
 * snippets
 * filesGlob support (on_save only)

Errors? See [Common Errors and Solutions][errorfaq] first, then [issue][issues] a bug report.


![Images of ArcticTypescript](https://raw.githubusercontent.com/Phaiax/ArcticTypescript/master/screenshots/animated.gif)

[issues]: https://github.com/Phaiax/ArcticTypescript/issues
[errorfaq]: https://github.com/Phaiax/ArcticTypescript/wiki/Common-Errors-and-Solutions

Commands and Shortcuts
----------------------------------------------------------------------------

| Shortcut                    | Action |
|---                          |--- |
| `Ctrl`+ `Space`             | trigger code completion. |
| `Alt` + `Shift` + `E` `E`   | error view |
| `Alt` + `Shift` + `E` `H`   | jump to 1st error |
| `Alt` + `Shift` + `E` `J`   | jump to 2nd error |
| `Alt` + `Shift` + `E` `K`   | jump to 3rd error |
| `Alt` + `Shift` + `E` `L`   | jump to 4th error |
| `F1`                        | show details about type under cursor |
| `F2`                        | refactor under cursor <br>(beta: enable in settings first) |
| `F4`                        | jump to declaration |
| `F8` or `Ctrl`+`B`          | Build the project. |
| `Shift`+`F5`                | reload (do this if autocompletion<br> is missing something or after <br> tsconfig.json changes) |

 * Goto Anything -> "ArcticTypescript: Terminate All Builds" if build is stuck
 * snippets: see below



Example Projects
----------------------------------------------------------------------------

 * [Brower example without modules][example_basicbrowser]: compile to single file
 * [AMD-Modules][example_amd]: only compiling, no example index.html
 * [AMD-Modules with tests for Browser][example_amdtest] **FEATURED**: index.html for app and test.html for tests
 * [Nodejs][example_commonjs]: only compiling
 * [Nodejs with test][example_commonjstest]: automatic text execution with mocha after build
 * [Simplest concat example][example_singleout]: everything will be compiled to out.js
 * [Simplest example][most_simple]: empty tsconfig.json `{ }`. Every .ts file will be compiled by itself. Not the ideal solution for multiple .ts files. Use [Simplest concat example][example_singleout] instead.

[example_amdtest]: https://github.com/Phaiax/ArcticTypescript/tree/master/examples/amd_modules_with_tests
[example_basicbrowser]: https://github.com/Phaiax/ArcticTypescript/tree/master/examples/basic_browser_project
[example_commonjstest]: https://github.com/Phaiax/ArcticTypescript/tree/master/examples/common_js_modules_with_tests
[example_singleout]: https://github.com/Phaiax/ArcticTypescript/tree/master/examples/single_out_file
[example_amd]: https://github.com/Phaiax/ArcticTypescript/tree/master/examples/using_amd_modules
[example_commonjs]: https://github.com/Phaiax/ArcticTypescript/tree/master/examples/using_commonjs_modules
[most_simple]: https://github.com/Phaiax/ArcticTypescript/tree/master/examples/most_simple




Settings
----------------------------------------------------------------------------

You need to configure typescript using a `tsconfig.json` file. Place this
file in your project folder or at least in some parent folder of your source
files.

Minimal Example `tsconfig.json`:

    {
        "compilerOptions": {
            "out": "out.js",
            "sourceMap": true,
            "target": "es5"
        },
        "files": [
            "main.ts"
        ],
    }


`"files" : []` : Define the files which should be compiled. **At least 1 file is
                 required.** You only need to specify the file from the top / root
                 of your internal reference tree (your main.ts). But it does no
                 harm to specify more files.
                 **Alternative**: use `"filesGlob" : []` (see below)


More `compilerOptions`:

 * `target`              (string) 'es3'|'es5' (default) | 'es6'
 * `module`              (string) 'amd'|'commonjs' (default)
 * `declaration`         (boolean) Generates corresponding `.d.ts` file
 * `out`                 (filepath) Concatenate and emit a single file
 * `outDir`              (folderpath) Redirect output structure to this directory
 * `noImplicitAny`       (boolean) Error on inferred `any` type
 * `removeComments`      (boolean) Do not emit comments in output
 * `sourceMap`           (boolean) Generates SourceMaps (.map files)
 * `removeComments`      (boolean)  Do not emit comments to output.
 * `sourceRoot`          (folder) Optionally specifies the location where debugger
                         should locate TypeScript source files after deployment
 * `mapRoot`             (folder) Optionally Specifies the location where debugger
                         should locate map files after deployment
 * `preserveConstEnums`  (boolean) Do not erase const enum
                         declarations in generated code.
 * `suppressImplicitAnyIndexErrors` (boolean) Suppress noImplicitAny errors for
                        indexing objects lacking index signatures.

All pathes are relative to `tsconfig.json`. These are exactly the options for
the typescript compiler: Refer to `tsc --help`.

Decide between:

 * `out='outfile.js'` : Then use ```/// <reference path="second.ts" />``` to
    spread your code. [Example][example_singleout]
 * `outDir='built/'` and `module='amd'`: Use ```import s = require('second')```
   to spread your code. [Example][example_amd]




### filesGlob ##################################################################

[Atom-TypeScript][atomts] provides a feature called [filesGlob][at-tsconfig].
ArcticTypescript mimics that feature. Create a `filesGlob` list next to
the `files` list. Everytime you **save** `tsconfig.json` the files will be
updated. Example:

    {
        "compilerOptions": { },
        "filesGlob": [
            "./**/*.ts",
            "!./node_modules/**/*.ts"
        ]
    }

[at-tsconfig]: https://github.com/TypeStrong/atom-typescript/blob/master/docs/tsconfig.md




### ArcticTypescript settings ##################################################

You can configure ArcticTypescript as well (type, default):

 * `enable_refactoring`        (boolean, false) Disabled by default (still beta)
 * `activate_build_system`     (boolean, true)
 * `auto_complete`             (boolean, true)
 * `node_path`                 (string, null) If null, then nodejs must be in $PATH
 * `tsc_path`                  (string, null) If null, it will search a
                                              `node_modules` dir with typescript
                                              installed or
                                              use ArcticTypescript's `tsc`
 * `error_on_save_only`        (boolean, false)
 * `build_on_save`             (boolean, false)
 * `show_build_file`           (boolean, false) show the compiled output after build
 * `pre_processing_commands`   ([string], [])
 * `post_processing_commands`  ([string], [])


Where to store these settings:

 * For personal settings across all typescript projects:
    + GUI: Menu -> Preferences -> "Settings - User" -> `['ArcticTypescript'][KEY]`.
      This is the file
      `<sublime config dir>/Packages/User/Preferences.sublime-settings`.
    + GUI Menu -> Preferences -> Package Settings ->
      ArcticTypescript -> "Settings - User" -> `[KEY]`.
      This is the file
      `<sublime config dir>/Packages/User/ArcticTypescript.sublime-settings`.
 * For personal, project specific settings
    + GUI: Menu -> Project -> "Edit Project" -> `['settings']['ArcticTypescript'][KEY]`.
      This is the file
      `<ProjectSettings>.sublime-settings`.
 * If you are not part of a team or for settings for everyone or for project
   specific settings if you don't have created a sublime project
    + `tsconfig.json ['ArcticTypescript'][KEY]`


Example Settings in project file `mytsproject.sublime-settings`:

    {
        "folders":
        [
            {
                "file_exclude_patterns": ["*~"],
                "follow_symlinks": true,
                "path": "."
            }
        ],
        "settings":
        {
            "ArcticTypescript": {
                "pre_processing_commands": ["node .settings/.components"]
                "post_processing_commands": [
                    "node .settings/.silns.js",
                    "r.js.cmd -o .settings/.build.js",
                    "cat ${tsconfig}",
                    "echo a\\\\nbc | cat"
                ]
            }
        }
    }

The working directory for all commands is `${tsconfig_path}`. They will be executed
using `subprocess.Popen(cmd, shell=True)`. shell=True -> You can use pipes, ...

You can use variables for the string values:

 * [Sublime Variables][sublime_variables]
 * All your compilerOptions, e.g. `${outDir}`
 * `${platform}` : sys.platform = "linux" | "darwin" | "nt"
 * `${tsconfig}` : the path to tsconfig.json
 * `${tsconfig_path}` : the folder of tsconfig.json


 [sublime_variables]: http://docs.sublimetext.info/en/latest/reference/build_systems/configuration.html?highlight=file_name#build-system-variables




Snippets
----------------------------------------------------------------------------

Type `<trigger>` and press `TAB` to insert snippet: `<trigger>`: feature

 * `typescriptsnippets` : Print this list into file as **short reference**.
 * .
 * `cls`  : class with constructor
 * `ctor` : constructor
 * `get`  : public getter
 * `set`  : public setter
 * `prop` : public getter and setter
 * `met`  : public class method
 * .
 * `imp`  : `import a = require('b')`
 * `ref`  : `/// <reference path="a" />`
 * .
 * `do`   : do while loop
 * `for`  : `for (…; i++) {…}`
 * `forl` : `for (… .length; i++) {…}`
 * `forb` : `for (…; i--) {…}` backwards loop (faster?)
 * `forin`: for … in … loop
 * .
 * `f`    : `function a(b) {c}`
 * `r0`   : `return false;`
 * `r1`   : `return true;`
 * `ret`  : `return a;`
 * .
 * `ie`   : if … else …
 * `if`   : if …
 * .
 * `log`  : `console.log();`
 * `to`   : `setTimeout(() => {}, 500);`
 * `sw`   : switch … case: … default:
 * `thr`  : `throw "";`






Installation
----------------------------------------------------------------------------

You need [Sublime Text 3][sublime3],
[Package Control for Sublime 3][pc_install], [node.js][nodejs],
and optionally [Typescript][typescript]
(ArcticTypescript also provides a compiler).


Install ArcticTypescript: Open Sublime
--> Goto Anything
--> `Package Control: Install Package`
--> `ArcticTypescript`

Install the [AutoFileName][autofilename] plugin for completion of
`/// <reference path="xxx" />`

[sublime3]: http://www.sublimetext.com/3
[pc_install]: https://packagecontrol.io/installation#st3
[nodejs]: http://nodejs.org/
[typescript]: http://www.typescriptlang.org/
[autofilename]: https://packagecontrol.io/packages/AutoFileName





Credits
----------------------------------------------------------------------------

[Typescript tools][typescripttools] for codecompletion and live errors.
I'm using the same error icons as [SublimeLinter][sublimelinter].
I took inspiration from [Atom TypeScript][atomts].

[typescripttools]: https://github.com/clausreinke/typescript-tools
[sublimelinter]: https://github.com/raph-amiard/sublime-typescript
[atomts]: https://github.com/TypeStrong/atom-typescript




Notes for Upgraders / People which used T3S before
----------------------------------------------------------------------------

This is a clone of the Typescript T3S Plugin, but with a lots of changes. If you switch to ArcticTypescript, please:

 - read this readme
 - uninstall T3S
 - delete the *.sublime-workspace files in your projects
 - close all file tabs in your old T3S Projects
 - update your key binding overrides, The new key is 'ArcticTypescript'




Compatibility
----------------------------------------------------------------------------

Sublime Text 2 is not supported anymore: Use the T3S plugin instead of this
one for Sublime Text 2 users.

Build system may not work if you have installed typescript < 1.5 your projects
node_modules / package.json. Workaround until typescript 1.5 is installed: Set
the dependency in `package.json` to
`"typescript": "git+ssh://git@github.com:Microsoft/TypeScript.git"`.




Important Changes
----------------------------------------------------------------------------

v0.7.0:
*  Variable replacements for post or pre processing commands now require curly braces: `${tsconfig}`
*  Typescript 1.5 beta

v0.6.0:

*  Dropped .sublimets, x.sublime-project. Compiler options belong to tsconfig.json
*  Many internal changes. Report if something is broken.
*  README rewrite
*  ProjectWizzard
*  filesGlob

v0.5.0:

*  You will need a new config file called tsconfig.json
*  Updated to TS 1.5 via typescript-tools (switching to tsserver will come soon)
*  Dropped support for Outline view, since typescript-tools has dropped support
   for this. This feature will come back again with tsserver.

v0.4.0:

*  build system: (relative) paths with spaces are now enclosed in "" automatically
*  > If you used additional "" to workaround the issue, you have to remove them,
   refer to messages/0.4.0.txt

v0.3.0:

*  relative root files now have a different base directory
*  The default shortcut to switch to the error view changed to: CTRL + ALT + E
*  There are 4 new shortcuts to jump to the first four Errors:
   CTRL + ALT + E + H (or J, K, L)
