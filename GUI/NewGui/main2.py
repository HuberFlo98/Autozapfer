import tkinter as tk
from tkinter import ttk

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="This is Page One")
        label.pack(pady=10, padx=10)
        
        button = tk.Button(self, text="Go to Page Two", command=self.go_to_page_two)
        button.pack(pady=5)

    def go_to_page_two(self):
        self.controller.show_frame(PageTwo)

class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="This is Page Two")
        label.pack(pady=10, padx=10)
        
        button = tk.Button(self, text="Go to Page One", command=self.go_to_page_one)
        button.pack(pady=5)

    def go_to_page_one(self):
        self.controller.show_frame(PageOne)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Navigation Example")
        self.geometry("300x200")
        
        self.frames = {}
        
        for F in (PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.pack(fill="both", expand=True)
        
        self.show_frame(PageOne)
    
    def show_frame(self, page_class):
        frame = self.frames[page_class.__name__]
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()