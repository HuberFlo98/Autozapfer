from time import strftime


def time(tk, root):
    string = strftime('%H:%M')
    lbl = tk.Label(root, font=('calibri', 25, 'bold'), background='#FFFFFF', foreground='#219a34')
    lbl.place(x=775, y=0)
    lbl.config(text=string)
    lbl.after(1000, time)
