import sublime, sys, json
from sublime_unittest import TestCase

import ArcticTypescript.lib.system.ProjectSettingsUpdater as PSU

class test_updateprojectsettings(TestCase):
    def test_old_to_new(self):
        # test_convert_settings_to_tsconfigjson
        # https://github.com/TypeStrong/tsconfig

        old_config = json.loads("""{
            "activate_build_system":true,
            "auto_complete":true,
            "node_path":"none",
            "error_on_save_only":false,
            "build_on_save":false,
            "show_build_file":false,
            "build_parameters":{
                "pre_processing_commands":[],
                "post_processing_commands":[],
                "output_dir_path":"none",
                "concatenate_and_emit_output_file_path":"none",
                "source_files_root_path":"none",
                "map_files_root_path":"none",
                "module_kind":"none",
                "allow_bool_synonym":false,
                "allow_import_module_synonym":false,
                "generate_declaration":false,
                "no_implicit_any_warning":false,
                "skip_resolution_and_preprocessing":false,
                "remove_comments_from_output":false,
                "generate_source_map":false,
                "ecmascript_target":"ES3"
            }
        }""")

        valid_new_tsconfig = json.loads("""{
            "compilerOptions": {
                "module": "commonjs",
                "noImplicitAny": true,
                "removeComments": true,
                "preserveConstEnums": true,
                "out": "../../built/local/tsc.js",
                "sourceMap": true
            },
            "files": [
                "./src/foo.ts"
            ]
        }""")

        tsconfig = PSU.old_settings_to_tsconfig(old_config)

        self.assertIn("")


        self.assertEqual(13, 13)
