
#Introduction

This is a short reference on how to test this plugin in a TDD way.

This plugin uses https://packagecontrol.io/packages/UnitTesting for testing itself.



# Preparations

Just for clarity: For development, do not install ArcticTypescript via Package Control. Instead install it into the "Packages" directory via git clone.

 * Install randy3k's UnitTesting via Package Control
 * Install Restart via Package Control
 * Install "Plugin UnitTest Harness" via Package Control
 * You may change the Keycode F5 for restart, since it interferes with ArcticTypescript at the moment


The Tests modify the project file on the fly, so best you open the TDDTesting Project.

 * Project -> Close Project
 * restart sublime
 * Project -> Open Project -> ArcticTypescript/tests/TDDTesting/TDDTesting.sublime-project

# TDD

Now every time that you restart sublime, it will execute the tests in lib/test and display the results.

Press F5 to restart sublime.

See any tests as examples on how to test.

To limit the executed tests, edit the filepattern parameter in ArcticTypescript.py. Do not commit changes done here.

# TODO

To be able to test different configurations, we must implement complete unloading of a loaded Typescript Project (no more globals!)



