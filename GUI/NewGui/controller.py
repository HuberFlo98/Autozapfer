import view.window2 as window2
import view.mainpage as mainpage
import view.registrationPage as registrationPage
class Controller():

    Window2 = window2.PageTwo
    MainPage = mainpage.MainPage
    RegistrationPage = registrationPage.RegistrationPage
    frames = {}

    def __init__(self, window):
        self.window = window
        
    def goToPage(self, page_class):
        frame = self.frames[page_class.__name__]
        print(frame)
        frame.tkraise()

    def addFrame(self, key, frame):
        print("test")
        print(key)
        self.frames[key] = frame

    def open_keyboard(self):
        self.window.open_keyboard()
        return
    
    def close_keyboard(self):
        self.window.close_keyboard()
        return

    def delete_user(self):
        return
    def login_user(self):
        return
    
    def login_guest(self):
        return
    def automode(self):
        return
    def user_registration(self):
        self.goToPage(self.RegistrationPage)
        return