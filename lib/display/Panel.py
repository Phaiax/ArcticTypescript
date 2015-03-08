# coding=utf8



class Panel(object):

    panel = None

    def show(self,window):
        self.window = window
        if not self.panel:
            self.panel = self.create_output_panel(self.window,'typescript_output')

    def hide(self):
        self.window.run_command("hide_panel", {"panel": "output.typescript_output"})

    def update(self,output):
        self.panel.run_command('append', {'characters': output})
        self.panel.show(self.panel.size()-1)
        self.window.run_command("show_panel", {"panel": "output.typescript_output"})

    def clear(self,window):
        self.window = window
        self.panel = self.create_output_panel(self.window,'typescript_output')

    def create_output_panel(self,window,name):
        return window.create_output_panel(name)


# --------------------------------------- INITIALISATION -------------------------------------- #

PANEL = Panel()