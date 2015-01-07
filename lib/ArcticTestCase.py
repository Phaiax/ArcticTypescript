from sublime_unittest import TestCase
import sublime
import os

class ArcticTestCase(TestCase):
    def assert_no_typescript_project_settings(self):
        # make sure no typescript settings are present
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

        tsfile = os.path.join(tddprojectfolder, filename)
        open(tsfile, 'a').close()
        return tsfile

    def close_view(self, view):
        view.set_scratch(True)
        view.window().focus_view(view)
        view.window().run_command("close_file")
