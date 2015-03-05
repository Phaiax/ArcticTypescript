# coding=utf8


from sublime_unittest import TestCase
import sublime
import os


class ArcticTestCase(TestCase):
    def assert_no_typescript_project_settings(self):
        # make sure no typescript settings are present
        project_data = sublime.active_window().project_data()
        if 'settings' in project_data:
            if 'typescript' in project_data["settings"]:
                project_data["settings"].pop("typescript")
                sublime.active_window().set_project_data(project_data)

        project_data = sublime.active_window().project_data()
        if 'settings' in project_data:
            self.assertNotIn('typescript', project_data['settings'].keys())


    def assert_active_window_is_tddproject_and_return_projectfolder(self):
        tddprojectfolder = sublime.active_window().folders()[0]
        self.assertTrue(tddprojectfolder.endswith("TDDTesting"))
        return tddprojectfolder

    def create_ts_file(self, filename='main.ts'):
        # create empty ts file
        tddprojectfolder = self.assert_active_window_is_tddproject_and_return_projectfolder()
        self.tsfilepath = os.path.join(tddprojectfolder, filename)
        open(self.tsfilepath, 'a').close()

        return self.tsfilepath

    def open_and_focus_tsfile(self, filepath='', filename=''):
        filepath = self._find_filepath(filepath=filepath, filename=filename)
        self.tsview = sublime.active_window().open_file(filepath)
        sublime.active_window().focus_view(self.tsview)

        return self.tsview

    def _find_filepath(self, filepath, filename):
        if filename:
            tddprojectfolder = self.assert_active_window_is_tddproject_and_return_projectfolder()
            filepath = os.path.join(tddprojectfolder, filename)
        elif not filepath:
            filepath = self.tsfilepath
        return filepath

    def close_view(self, view=None):
        if view is None:
            view = self.tsview
        view.set_scratch(True)
        view.window().focus_view(view)
        view.window().run_command("close_file")

    def rm_file(self, filepath='', filename=''):
        filepath = self._find_filepath(filepath=filepath, filename=filename)
        os.remove(filepath)

    def clear_files_except_sublimeproject(self):
        tddprojectfolder = self.assert_active_window_is_tddproject_and_return_projectfolder()
        #f = []
        for root, dirs, files in os.walk(tddprojectfolder, topdown=False):
            for name in files:
                if name != "TDDTesting.sublime-project" and name != "TDDTesting.sublime-workspace":
                    os.remove(os.path.join(root, name))
                    #f.append(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
                #f.append(os.path.join(root, name))
        #self.assertTrue(False, msg=f)

    def create_settings(self, type='sublime-project', rootfile="main.ts"):
        self.assertEqual(type, 'sublime-project') # todo: sublimets

        self.assert_active_window_is_tddproject_and_return_projectfolder()
        project_data = sublime.active_window().project_data()
        if "settings" not in project_data:
            project_data["settings"] = {  }
        if "typescript" not in project_data["settings"]:
            project_data["settings"]["typescript"] = {  }

        project_data["settings"]["typescript"]["roots"] = [rootfile]

        project_data["settings"]["typescript"]["settings"] = {
                "auto_complete": True,
                "build_on_save": False,
                "build_parameters": {
                    "allow_bool_synonym": False,
                    "allow_import_module_synonym": False,
                    "concatenate_and_emit_output_file_path": "none",
                    "ecmascript_target": "ES3",
                    "generate_declaration": False,
                    "generate_source_map": False,
                    "map_files_root_path": "none",
                    "module_kind": "none",
                    "no_implicit_any_warning": False,
                    "output_dir_path": "none",
                    "post_processing_commands": [],
                    "pre_processing_commands": [],
                    "remove_comments_from_output": False,
                    "skip_resolution_and_preprocessing": False,
                    "source_files_root_path": "none"
                },
                "error_on_save_only": False,
                "node_path": "none",
                "show_build_file": False
            }

        sublime.active_window().set_project_data(project_data)