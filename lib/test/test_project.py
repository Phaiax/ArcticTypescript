# coding=utf8

import sublime, sys, os
from ArcticTypescript.lib.ArcticTestCase import ArcticTestCase
from sublime_unittest import TestCase
from unittest.mock import MagicMock as MM

Project =  sys.modules["ArcticTypescript.lib.system.Project"]

class test_project_opening(ArcticTestCase):

    def setUp(self):
        # No settings or other files
        self.clear_files_except_sublimeproject()
        #self.assert_no_typescript_project_settings()


    def test_opening_ts_file_should_trigger_dialog_if_no_project_settings(self):
        """ Dialog is only shown when no .sublimets or *.sublime-project is found
        or if these files do not specify any root files"""

        return
        # mock show method
        tmp_show = Project.ProjectError.show
        Project.ProjectError.show = MM()

        self.create_ts_file()
        self.open_and_focus_tsfile()

        yield 10 # pause 10 ms

        self.assertTrue(Project.ProjectError.show.called)

        # reset mocked method
        Project.ProjectError.show = tmp_show
        self.close_view()
        self.rm_file()


    def test_opening_ts_file_should_init_project(self):
        self.create_settings()
        self.create_ts_file()

        tmp_init = Project.OpenedProject.__init__
        Project.OpenedProject.__init__ = MM()

        self.open_and_focus_tsfile()

        yield 10

        self.assertTrue(Project.OpenedProject.__init__)

        # reset mocked method
        Project.OpenedProject.__init__ = tmp_init
        #self.close_view()
        #self.rm_file()



    def test_opening_ts_file_should_create_projectclass(self):
        pass
        #sublime.active_window().project_data()
        #x = Project.project_by_view(1)
        #self.assertEqual(x, 13)

# for testing sublime command

class test_helloworld_command(TestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def setText(self, string):
        pass
        #self.view.run_command("insert", {"characters": string})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row,0)))

    def test_hello_world_st3(self):
        #self.view.run_command("hello_world")
        first_row = self.getRow(0)
        #self.assertEqual(first_row,"hello world")

    def test_hello_world(self):
        self.setText("new ")
        #self.view.run_command("hello_world")
        first_row = self.getRow(0)
        #self.assertEqual(first_row,"new hello world")


Project =  sys.modules["ArcticTypescript.lib.system.Project"]

class test_internal_functions(TestCase):
    def test_foo(self):
        x = Project.project_by_view(1)
        self.assertEqual(x, 13)
