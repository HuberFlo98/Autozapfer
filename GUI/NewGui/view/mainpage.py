import tkinter as tk
from tkinter import ttk 
from tkinter import *


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="This is Page one")
        label.pack(pady=10, padx=10)
        
        button = tk.Button(self, text="Go to Page two", command=lambda: controller.goToPage(controller.Window2))
        button.pack(pady=5)

        #configuring Status Bar
        #label_score.config(text="Score: 0")
        #label_user.config(text="User:")
        #Create Frame for startpage
       
        #Create widgets for startpage
        lbl=ttk.Label(self,text='User-Login', style="Mode.TLabel")
        lbl.pack(side=LEFT)
        label_username = ttk.Label(self, text="Username:", style="Label.TLabel")
        entry_username = ttk.Entry(self, style="Entry.TEntry")
        label_password = ttk.Label(self, text="Password:", style="Label.TLabel")
        entry_password = ttk.Entry(self, style="Entry.TEntry", show="*")
        lbl_facereg=ttk.Label(self)    #Label for showing Image
        lbl_facereg.pack(side=LEFT)
        button_register = ttk.Button(self, text="Registration", style="Menu.TButton", command=lambda: controller.user_registration())
        button_zapfen = ttk.Button(self, text="Beer", style="Menu.TButton", command=lambda: controller.automode(), state="disabled")
        button_guestlogin = ttk.Button(self, text = "Guest Login", style="Menu.TButton", command=lambda: controller.login_guest())
        button_login = ttk.Button(self, text="Login", style="Menu.TButton", command=lambda: controller.login_user())
        #button_faceid = ttk.Button(self, text="Beer ID", style="Menu.TButton", command=lambda: fr.run_recognition())
        button_delete = ttk.Button(self, text="Delete", style="Menu.TButton", command=lambda: controller.delete_user())
        button_showkeyboard= ttk.Button(self, text="Show\nKeyboard", style = "Menu.TButton", command=controller.open_keyboard)
        button_closekeyboard = ttk.Button(self, text="Close\nKeyboard", style = "Menu.TButton", command=controller.close_keyboard)
        label_feedback = ttk.Label(self, text="", style="Label.TLabel")
        # Positionieren der Widgets
        label_username.pack(side=LEFT)
        entry_username.pack(side=LEFT)
        label_password.pack(side=LEFT)
        entry_password.pack(side=LEFT)
        button_register.pack(side=LEFT)
        button_login.pack(side=LEFT)
        button_delete.pack(side=LEFT)
        button_showkeyboard.pack(side=LEFT)
        button_closekeyboard.pack(side=LEFT)
        label_feedback.pack(side=LEFT)
        label_feedback.place_forget() # dont show label feedback until its used
        button_zapfen.pack(side=LEFT)
        button_guestlogin.pack(side=LEFT)
        self.update()
        #button_faceid.pack(side=LEFT)


