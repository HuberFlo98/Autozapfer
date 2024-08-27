import tkinter as tk
from tkinter import ttk
from tkinter import *

class RegistrationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        #Create widgets
        lbl=ttk.Label(self,text='Registration', style="Mode.TLabel")
        lbl.pack(side=LEFT)
        label_username = ttk.Label(self, text="Username:", style="Label.TLabel")
        entry_username = ttk.Entry(self, style="Entry.TEntry")
        label_password = ttk.Label(self, text="Password:", style="Label.TLabel")
        entry_password = ttk.Entry(self, style="Entry.TEntry", show="*")
        label_weight = ttk.Label(self, text="Weight in kg:", style="Label.TLabel")
        entry_weight = ttk.Entry(self, style="Entry.TEntry")
        label_feedback = ttk.Label(self, text="", style="Label.TLabel")
        #lbl_facereg = ttk.Label(picture_frame)
        #lbl_facereg.pack(side=LEFT)
        button_register = ttk.Button(self, text="Finish\nRegistration", style="Menu.TButton", command=lambda: controller.register_user())
        button_userlogin = ttk.Button(self, text="Back To\nUserLogin", style="Menu.TButton", command=lambda: controller.goToPage(controller.MainPage))
        #button_picture = ttk.Button(self, text="Take Picture", style="Menu.TButton", command=lambda: fr.take_picture())
        button_showkeyboard= ttk.Button(self, text="Show\nKeyboard", style = "Menu.TButton", command=controller.open_keyboard)
        button_closekeyboard = ttk.Button(self, text="Close\nKeyboard", style = "Menu.TButton", command=controller.close_keyboard)
        #pack(side=LEFT)
        label_username.pack(side=LEFT)
        entry_username.pack(side=LEFT)
        label_password.pack(side=LEFT)
        entry_password.pack(side=LEFT)
        label_weight.pack(side=LEFT)
        entry_weight.pack(side=LEFT)
        label_feedback.pack(side=LEFT)
        label_feedback.place_forget() #dont show label until its not used
        button_register.pack(side=LEFT)
        button_register.config(state="disabled")
        button_userlogin.pack(side=LEFT)
       # button_picture.pack(side=LEFT)
        button_showkeyboard.pack(side=LEFT)
        button_closekeyboard.pack(side=LEFT)