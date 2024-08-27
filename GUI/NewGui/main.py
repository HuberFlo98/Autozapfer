import tkinter as tk
import view.mainpage as mainpage
import view.window2 as window2
import view.registrationPage as registrationPage
import controller as c
import subprocess

class App(tk.Tk):

    osk = None

    def __init__(self):
        super().__init__()
        controller = c.Controller(self)
        self.title("Tkinter Navigation Example")
        self.geometry("1600x800")

        
        for F in [mainpage.MainPage, window2.PageTwo, registrationPage.RegistrationPage]:
            frame = F(parent=self, controller=controller)
            frame.grid(row=0,column=0,sticky="nsew")
            controller.addFrame(F.__name__, frame)

        
        controller.goToPage(mainpage.MainPage)


    #def go_to_page_one(self):
        #self.controller.show_frame(PageOne)

    def open_keyboard(self):
        self.osk=subprocess.Popen("exec " + "onboard",stdout= subprocess.PIPE, shell=True)
    def close_keyboard(self):
        if self.osk:
            self.osk.kill()
            self.osk = None


if __name__ == "__main__":
    app = App()
    app.mainloop()