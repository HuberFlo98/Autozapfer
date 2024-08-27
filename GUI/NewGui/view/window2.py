import tkinter as tk

class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="This is Page Two")
        label.pack(pady=10, padx=10)
        
        button = tk.Button(self, text="Go to Page One", command=lambda: controller.goToPage(controller.MainPage))
        button.pack(pady=5)

