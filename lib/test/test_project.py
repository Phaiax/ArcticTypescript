import sublime, sys
from unittest import TestCase


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
