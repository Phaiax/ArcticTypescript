ArcticTypescript
================

 * TypeScript language auto completion
 * TypeScript language syntax highlighting
 * TypeScript language error highlighting
 * A build System
 * Fast access to errors via shortcuts and clicks
 * Goto definition
 * View type
 * Wizzard for project creation




Commands and Shortcuts
----------------------------------------------------------------------------

 * `ctrl + space`           trigger code completion.
 * `alt + shift + e e`      error view
 * `alt + shift + e h`      jump to 1st error
 * `alt + shift + e j`      jump to 2nd error
 * `alt + shift + e k`      jump to 3rd error
 * `alt + shift + e l`      jump to 4th error
 * `F1`                     show details about type under cursor
 * `F4`                     jump to definition
 * `F5`                     reload (to this if autocompletion is missing something)
 * `F8` or `ctrl + b`       Build the project.
 * Goto Anything -> "ArcticTypescript: Terminate All Builds" if build is stuck




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


Either `outDir` `out`.




### ArcticTypescript settings

You can configure ArcticTypescript as well (type, default):

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
    + GUI: Menu -> Preferences -> "Settings - User" -> `['ArcticTypescript'][KEY]`
      `<sublime config dir>/Packages/User/Preferences.sublime-settings ['ArcticTypescript'][KEY]`
    + GUI Menu -> Preferences -> Package Settings ->
      ArcticTypescript -> "Settings - User" -> `[KEY]`
      `<sublime config dir>/Packages/User/ArcticTypescript.sublime-settings [KEY]`
 * For personal, project specific settings
    + GUI: Menu -> Project -> "Edit Project" -> `['settings']['ArcticTypescript'][KEY]`
    `<ProjectSettings>.sublime-settings ['settings']['ArcticTypescript'][KEY]`

 * If you are not part of a team or for settings for everyone or for project
   specific settings if you don't have created a sublime project
    + `tsconfig.json ['ArcticTypescript'][KEY]`


Example Settings in project file `mytyproject.sublime-settings`:

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
                    "cat $tsconfig",
                    "echo a\\\\nbc | cat"
                ]
            }
        }
    }

The working directory for all commands is `$tsconfig_path`. They will be executed
using `subprocess.Popen(cmd, shell=True)`. shell=True -> You can use pipes, ...

For the string values, you can use variables,
the [Sublime Variables][sublime_variables] and these:

 * `platform` : sys.platform = "linux" | "darwin" | "nt"
 * `tsconfig` : the path to tsconfig.json
 * `tsconfig_path` : the folder of tsconfig.json


 [sublime_variables]: http://docs.sublimetext.info/en/latest/reference/build_systems/configuration.html?highlight=file_name#build-system-variables




Installation
----------------------------------------------------------------------------

Install [Package Control][pc_install] for Sublime Text 3, [node.js][nodejs], and
[Typescript][typescript] via npm: `npm install -g typescript`

[pc_install]: https://packagecontrol.io/installation#st3
[nodejs]: http://nodejs.org/
[typescript]: http://www.typescriptlang.org/

Goto Anything: `Package Control: Install Package` > `ArcticTypescript`




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
 - only use one root file
 - delete the *.sublime-workspace files in your projects
 - close all file tabs in your old T3S Projects
 - update your key binding overrides, The new key is 'ArcticTypescript'




Compatibility
----------------------------------------------------------------------------

Sublime Text 2 is not supported anymore: Use the T3S plugin instead of this
one for Sublime Text 2 users.




Important Changes
----------------------------------------------------------------------------

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
