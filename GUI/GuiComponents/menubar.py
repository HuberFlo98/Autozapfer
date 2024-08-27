def menubar(root, tk):
    lbl_Autozapfer=tk.Label(root,text='Autozapfer', font=('calibri', 20, 'bold'), background='#FFFFFF', fg='#219a34')
    lbl_Autozapfer.place(x=550,y=2,height= 36, width=175)
    lbl_user=tk.Label(root,text='User:', font=('calibri', 12, 'bold'), background='#FFFFFF', fg='#219a34')
    lbl_user.place(x=0,y=2, height= 36, width=200)
    lbl_score=tk.Label(root,text='Score:', font=('calibri', 12, 'bold'), background='#FFFFFF', fg='#219a34')
    lbl_score.place(x=300,y=2,height= 36, width=100)

    lbl_Autozapfer=tk.Label(root,text='Autozapfer', font=('calibri', 20, 'bold'), background='#FFFFFF', fg='#219a34')
    lbl_Autozapfer.place(x=550,y=2,height= 36, width=175)
    lbl_user=tk.Label(root,text='User:', font=('calibri', 12, 'bold'), background='#FFFFFF', fg='#219a34')
    lbl_user.place(x=0,y=2, height= 36, width=200)
    lbl_score=tk.Label(root,text='Score:', font=('calibri', 12, 'bold'), background='#FFFFFF', fg='#219a34')
    lbl_score.place(x=300,y=2,height= 36, width=100)

    # Offbutton
    image = Image.open('./Bilder/Offbutton.png')
    image = image.resize((36,36))
    Offbt = ImageTk.PhotoImage(image)
    bt_off= tk.Button(root,command=ausschalten, image = Offbt,bg="white")
    bt_off.place(x=730,y=0)

    # LogOff
    bt_logoff = tk.Button(root, text="LogOff",command=lambda: startpage(root, lbl_user, lbl_score),bg="white")
    bt_logoff.place(x=250,y=2,height=36, width=50)