#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#reated on Sat May 27 01:44:24 2023

#author: daniel

#from tkinter import *
import SP.AnsteuerungLib as bz
import BV.GesichtsidentifizierungV02 as facerec
import tkinter as tk
import ttkthemes as ttkt
from tkinter import ttk
import sqlite3
from PIL import Image, ImageTk
from time import strftime
from UserManagement.UserLib import create_table, register_user, login_user, delete_user, login_guest, inc_promille

import Jetson.GPIO as GPIO

import subprocess

#initialize face recognition, create class elemnt and read in pictures
fr=facerec.FaceRecognition()
#global vars
osk = None
tilted_val = 45
# Erstellen der Datenbanktabelle
create_table()

#INIT Display
root = tk.Tk()  # create a root widget
#apply dark theme
style = ttkt.ThemedStyle(root)
style.set_theme("black")
#Set Styles for Widgets
style.configure("Mode.TButton", font=("Calibri",16), anchor="center")
style.configure("Menu.TButton", font=("Calibri",12), anchor="center")
style.configure("Label.TLabel", font=("Calibri",12), anchor="left")
style.configure("Mode.TLabel", font=("Calibri",16), anchor=tk.CENTER)
style.configure("Entry.TEntry", font=("Calibri",14), anchor="left")
style.configure("Scaler.TScale")

#adapt style for root and for menu bar
#root.configure(background="#D9D9D9")
root.configure(background="#FFFFFF")
root.minsize(800, 480)  # width, height
#root.maxsize(800, 480)
#root.geometry("1024x600+100+100")  # width x height + x + y
root.attributes('-fullscreen', False)
  
#H-KA Logo
image = Image.open('./Bilder/HKALogo2.jpg')
image = image.resize((136,36))
logo = ImageTk.PhotoImage(image)
lbl = tk.Label(root, image=logo)
lbl.place(x=888, y=0)

#list for frame administration
open_frames=[]
    
# Clock
root.title('Clock')   
def time():
    string = strftime('%H:%M')
    lbl.config(text=string)
    lbl.after(1000, time)
lbl = tk.Label(root, font=('calibri', 25, 'bold'), background='#FFFFFF', foreground='#219a34')
lbl.place(x=775, y=0)
time()

# Labels for Menu Bar
lbl_Autozapfer=tk.Label(root,text='Autozapfer', font=('calibri', 20, 'bold'), background='#FFFFFF', fg='#219a34')
lbl_Autozapfer.place(x=550,y=2,height= 36, width=175)
lbl_user=tk.Label(root,text='User:', font=('calibri', 12, 'bold'), background='#FFFFFF', fg='#219a34')
lbl_user.place(x=0,y=2, height= 36, width=200)
lbl_score=tk.Label(root,text='Score:', font=('calibri', 12, 'bold'), background='#FFFFFF', fg='#219a34')
lbl_score.place(x=300,y=2,height= 36, width=100)

#function for turning application off
def ausschalten():
    GPIO.cleanup   #Clean Up GPIOs
    root.destroy()  #destroy TKInter Window
    
# Offbutton
image = Image.open('./Bilder/Offbutton.png')
image = image.resize((36,36))
Offbt = ImageTk.PhotoImage(image)
bt_off= tk.Button(root,command=ausschalten, image = Offbt,bg="white")
bt_off.place(x=730,y=0)

# LogOff
bt_logoff = tk.Button(root, text="LogOff",command=lambda: startpage(root, lbl_user, lbl_score),bg="white")
bt_logoff.place(x=250,y=2,height=36, width=50)

#kill Frames
def kill(open_frames):
    try:
        for frame in open_frames:
            frame.destroy()
            open_frames.remove(frame)
    except:
        print("Error while deleting Frame or no open Frame")
        
#call keyboard
def open_keyboard():
    #subprocess.run(["onboard"])
    global osk
    osk=subprocess.Popen("exec " + "onboard",stdout= subprocess.PIPE, shell=True)
def close_keyboard():
    global osk
    if osk:
        osk.kill()
        osk = None
def on_slider_change(event):
    value = event.widget.get()
    global tilted_val
    tilted_val=value
    

# Pages
# Page for Login, opens at start of application
def startpage(root, label_user, label_score):
    #delete not used frames
    kill(open_frames)
    #configuring Status Bar
    label_score.config(text="Score: 0")
    label_user.config(text="User:")
    #Create Frame for startpage
    modebg=ttk.Frame(root)
    modebg.place(x=0,y=40,height=560,width=1024)
    #add page to open_frames
    open_frames.append(modebg)
    #Create Frame for Face ID
    facereg_frame = ttk.Frame(modebg, borderwidth = 5, relief="ridge")
    facereg_frame.place(x=512,y=0,height=560, width=512)
    #Create widgets for startpage
    lbl=ttk.Label(modebg,text='User-Login', style="Mode.TLabel")
    lbl.place(x=370,y=0,height=70, width=142)
    label_username = ttk.Label(modebg, text="Username:", style="Label.TLabel")
    entry_username = ttk.Entry(modebg, style="Entry.TEntry")
    label_password = ttk.Label(modebg, text="Password:", style="Label.TLabel")
    entry_password = ttk.Entry(modebg, style="Entry.TEntry", show="*")
    lbl_facereg=ttk.Label(facereg_frame)    #Label for showing Image
    lbl_facereg.place(x=0,y=0)
    button_register = ttk.Button(modebg, text="Registration", style="Menu.TButton", command=lambda: user_registration(root, label_user, label_score,fr))
    button_zapfen = ttk.Button(modebg, text="Beer", style="Menu.TButton", command=lambda: automode(root), state="disabled")
    button_guestlogin = ttk.Button(modebg, text = "Guest Login", style="Menu.TButton", command=lambda: login_guest(label_feedback, label_user, label_score, button_zapfen))
    button_login = ttk.Button(modebg, text="Login", style="Menu.TButton", command=lambda: login_user(entry_username, entry_password, label_feedback, label_user, label_score, button_zapfen))
    button_faceid = ttk.Button(modebg, text="Beer ID", style="Menu.TButton", command=lambda: fr.run_recognition(lbl_facereg, facereg_frame, modebg, entry_username, entry_password, button_faceid, bt_logoff, button_login, button_guestlogin, button_delete, button_register, label_feedback))
    button_delete = ttk.Button(modebg, text="Delete", style="Menu.TButton", command=lambda: delete_user(entry_username, entry_password, label_feedback,fr))
    button_showkeyboard= ttk.Button(modebg, text="Show\nKeyboard", style = "Menu.TButton", command=open_keyboard)
    button_closekeyboard = ttk.Button(modebg, text="Close\nKeyboard", style = "Menu.TButton", command=close_keyboard)
    label_feedback = ttk.Label(modebg, text="", style="Label.TLabel")
    # Positionieren der Widgets
    label_username.place(x=50, y=50, height=30)
    entry_username.place(x=50, y=80, height=50)                                                                                                             
    label_password.place(x=50, y=130, height=30)
    entry_password.place(x=50, y=160, height=50) 
    button_register.place(x=50, y=280, height=70, width=120)
    root.update() # update picture
    button_login.place(x=button_register.winfo_x() + button_register.winfo_width() + 20, y=280, height=70, width=120)
    root.update()
    button_delete.place(x=button_login.winfo_x() + button_login.winfo_width() + 20, y=280, height=70, width=120)
    root.update()
    button_showkeyboard.place(x=button_delete.winfo_x() + 0,y = 80, height = 70, width=120)
    root.update()
    button_closekeyboard.place(x=button_delete.winfo_x(),y = 180, height = 70, width=120)
    root.update()
    label_feedback.place(x=50, y=240, height=30)
    label_feedback.place_forget() # dont show label feedback until its used
    button_zapfen.place(x=50, y=380, height=70, width=120)
    root.update()
    button_guestlogin.place(x=button_login.winfo_x() + button_login.winfo_width() + 20, y=380, height=70, width=120)
    button_faceid.place(x=button_register.winfo_x() + button_register.winfo_width() + 20, y=380, height=70, width=120)
    
def user_registration(root, label_user, label_score,fr):
    #delete not used frames
    kill(open_frames)
    #Create frame for registration
    reg_frame=ttk.Frame(root)
    reg_frame.place(x=0,y=40,height=560,width=1024)
    #add page to open_frames
    open_frames.append(reg_frame)
    #Create Frame for registration picture
    picture_frame = ttk.Frame(reg_frame, borderwidth = 5, relief="ridge")
    picture_frame.place(x=512,y=0,height=560, width=512)
    #Create widgets
    lbl=ttk.Label(reg_frame,text='Registration', style="Mode.TLabel")
    lbl.place(x=370,y=0,height=70, width=142)
    label_username = ttk.Label(reg_frame, text="Username:", style="Label.TLabel")
    entry_username = ttk.Entry(reg_frame, style="Entry.TEntry")
    label_password = ttk.Label(reg_frame, text="Password:", style="Label.TLabel")
    entry_password = ttk.Entry(reg_frame, style="Entry.TEntry", show="*")
    label_weight = ttk.Label(reg_frame, text="Weight in kg:", style="Label.TLabel")
    entry_weight = ttk.Entry(reg_frame, style="Entry.TEntry")
    label_feedback = ttk.Label(reg_frame, text="", style="Label.TLabel")
    lbl_facereg = ttk.Label(picture_frame)
    lbl_facereg.place(x=0,y=0)
    button_register = ttk.Button(reg_frame, text="Finish\nRegistration", style="Menu.TButton", command=lambda: register_user(entry_username, entry_password, entry_weight, label_feedback,fr))
    button_userlogin = ttk.Button(reg_frame, text="Back To\nUserLogin", style="Menu.TButton", command=lambda: startpage(root, label_user, label_score))
    button_picture = ttk.Button(reg_frame, text="Take Picture", style="Menu.TButton", command=lambda: fr.take_picture(lbl_facereg, picture_frame, reg_frame, button_picture, button_register, button_userlogin, entry_username, entry_password, entry_weight, label_feedback))
    button_showkeyboard= ttk.Button(reg_frame, text="Show\nKeyboard", style = "Menu.TButton", command=open_keyboard)
    button_closekeyboard = ttk.Button(reg_frame, text="Close\nKeyboard", style = "Menu.TButton", command=close_keyboard)
    #place widgets
    label_username.place(x=50, y=50, height=30)
    entry_username.place(x=50, y=80, height=50)
    label_password.place(x=50, y=130, height=30)
    entry_password.place(x=50, y=160, height=50)
    label_weight.place(x=50, y=210, height=30)
    entry_weight.place(x=50, y=240, height=50)
    label_feedback.place(x=50, y=290, height=30)
    label_feedback.place_forget() #dont show label until its not used
    button_register.place(x=50, y=380, height=70, width=120)
    button_register.config(state="disabled")
    button_userlogin.place(x=190, y=380, height=70, width=120)
    button_picture.place(x=330, y=380, height=70, width=120)
    button_showkeyboard.place(x=330,y = 80, height = 70, width=120)
    button_closekeyboard.place(x=330,y = 180, height = 70, width=120)
    root.update()
    
def automode(root):
    #delete not used frames
    kill(open_frames)
    #create page
    modebg=ttk.Frame(root)
    modebg.place(x=0,y=40,height=560,width=1024)
    #add page to open_frames
    open_frames.append(modebg)
    #switch valve to beer
    bz.SetHigh_MagnetVentil1(1)
    bz.SetHigh_MagnetVentil2(1)
    #Create Frame for Bier Status
    cam_frame = ttk.Frame(modebg, borderwidth = 5, relief="ridge")
    cam_frame.place(x=512,y=0,height=560, width=512)
    #Create Widgets
    lbl=ttk.Label(modebg,text='Automatic', style="Mode.TLabel")
    lbl_cam = ttk.Label(cam_frame)
    #Manual Button
    manualbt=ttk.Button(modebg,text='Manual', style="Mode.TButton", command=lambda: manualmode(root))
    # Status anzeigen Button
    if (lbl_user.cget("text").replace("User: ", "") != "Gast"):
        statebt = ttk.Button(modebg, text="Show\nstatus", style="Menu.TButton", command=lambda: statemode(root))
        statebt.place(x=365,y=450,height= 70, width=120)
    else:
        statebt = None
    #label Feedback
    label_feedback = ttk.Label(modebg, text="", style="Label.TLabel")
    # Bier 1 Button
    bierlinksimg= Image.open('./Bilder/Bier.png')
    bierlinksimg = bierlinksimg.resize((100,172))
    bierlinksphoto = ImageTk.PhotoImage(bierlinksimg)
    bierlinksbt= ttk.Button(root, image=bierlinksphoto, text="Beer 1", compound="center", command=lambda: bz.autobier1(root, tilted_val, lbl_user, lbl_score, bt_off, bt_logoff, lbl_cam, cam_frame, modebg, bierlinksbt,bierrechtsbt,manualbt, label_feedback,statebt))
    bierlinksbt.image = bierlinksphoto
    # Bier 2 Button
    bierrechtsimg= Image.open('./Bilder/Bier.png')
    bierrechtsimg = bierrechtsimg.resize((100,172))
    bierrechtsphoto = ImageTk.PhotoImage(bierrechtsimg)
    bierrechtsbt= ttk.Button(root, image=bierrechtsphoto, text="Beer 2", compound="center", command=lambda: bz.autobier2(root, tilted_val, lbl_user, lbl_score, bt_off, bt_logoff, lbl_cam, cam_frame, modebg, bierlinksbt,bierrechtsbt,manualbt, label_feedback,statebt))
    bierrechtsbt.image = bierrechtsphoto
    #Slider for foam1
    slider = ttk.Scale(modebg, from_=45, to=65, orient="horizontal",style="TScale")
    slider.bind("<Motion>", on_slider_change)
    #labels for slider
    label_smallfoam = ttk.Label(modebg, text="Small\nFoam", style="Label.TLabel")
    label_muchfoam = ttk.Label(modebg, text="Much\nFoam", style="Label.TLabel")
    #Position Widgets
    lbl.place(x=900,y=0,height=70, width=124)
    manualbt.place(x=0,y=0,height=70, width=120)
    bierlinksbt.place(x=70,y=170)
    bierrechtsbt.place(x=210,y=170)
    label_feedback.place(x=50, y=290, height=30)
    label_feedback.place_forget() #dont show label until its not used
    lbl_cam.place(x=0,y=0)
    slider.place(x=70,y=450, width=240)
    label_smallfoam.place(x=20,y=450)
    label_muchfoam.place(x=310,y=450)
    
    
def manualmode(root):
    #delete not used frames
    kill(open_frames)
    #create page
    modebg=ttk.Frame(root)
    modebg.place(x=0,y=40,height=560,width=1024)
    #add page to open_frames
    open_frames.append(modebg)
    lbl=ttk.Label(modebg,text='Manual', style="Mode.TLabel")
    lbl.place(x=900,y=0,height=70, width=124)
    # Mode Button
    autobt=ttk.Button(modebg,text='Auto', style="Mode.TButton", command=lambda: automode(root))
    autobt.place(x=0,y=0,height=70,width=120)
    # Reinugung Button
    cleanbt=ttk.Button(modebg,text='Cleaning', style="Mode.TButton", command=lambda: cleanmode(root))
    cleanbt.place(x=140,y=0,height=70, width=120)
    #Button, um gezapftes Bier User-Score hinzuzufügen, nur wenn kein Gast-Login
    if (lbl_user.cget("text").replace("User: ", "") != "Gast"):
        end_zapfen_bt=ttk.Button(modebg,text='Finished with\nTapping', style="Menu.TButton", command=lambda: inc_promille(lbl_user, lbl_score))
        end_zapfen_bt.place(x=345,y=450,height=70, width=120)
    # Bier 1 Button
    bier1img= Image.open('./Bilder/Bier.png')
    bier1img = bier1img.resize((100,172))
    bier1photo = ImageTk.PhotoImage(bier1img)
    bier1bt= ttk.Button(root, text="Beer 1", image=bier1photo, compound="center")
    bier1bt.image = bier1photo
    bier1bt.place(x=70,y=170)
    bier1bt.bind("<Button-1>", bz.SetLow_Zapfhahn1)
    bier1bt.bind("<ButtonRelease-1>", bz.SetHigh_Zapfhahn1)
    # Bier 2 Button
    bier2img= Image.open('./Bilder/Bier.png')
    bier2img = bier2img.resize((100,172))
    bier2photo = ImageTk.PhotoImage(bier2img)
    bier2bt= ttk.Button(root, text="Beer 2", image=bier2photo, compound="center")
    bier2bt.image = bier2photo
    bier2bt.place(x=210,y=170)
    bier2bt.bind("<Button-1>", bz.SetLow_Zapfhahn2)
    bier2bt.bind("<ButtonRelease-1>", bz.SetHigh_Zapfhahn2)
    # Glas 1 hoch Button
    up1bt = ttk.Button(modebg, text="Glass ↑", style="Menu.TButton")
    up1bt.place(x=65,y=350,height= 70, width=120)
    up1bt.bind("<Button-1>", bz.SetLow_Ausfahren_Motor1)
    up1bt.bind("<ButtonRelease-1>", bz.SetHigh_Ausfahren_Motor1)
    # Glas 1 runter Button
    down1bt = ttk.Button(modebg, text="Glass ↓", style="Menu.TButton")
    down1bt.place(x=65,y=450,height= 70, width=120)
    down1bt.bind("<Button-1>", bz.SetLow_Einfahren_Motor1)
    down1bt.bind("<ButtonRelease-1>", bz.SetHigh_Einfahren_Motor1)
    # Glas 2 hoch Button
    up2bt = ttk.Button(modebg, text="Glass ↑", style="Menu.TButton")
    up2bt.place(x=205,y=350,height= 70, width=120)
    up2bt.bind("<Button-1>", bz.SetLow_Ausfahren_Motor2)
    up2bt.bind("<ButtonRelease-1>", bz.SetHigh_Ausfahren_Motor2)
    # Glas 2 runter Button
    down2bt = ttk.Button(modebg, text="Glass ↓", style="Menu.TButton")
    down2bt.place(x=205,y=450,height= 70, width=120)
    down2bt.bind("<Button-1>", bz.SetLow_Einfahren_Motor2)
    down2bt.bind("<ButtonRelease-1>", bz.SetHigh_Einfahren_Motor2)

    #lights
    ledOnbtn = ttk.Button(modebg, text="LEDon", style="Menu.TButton")
    ledOnbtn.place(x=480,y=450,height= 70, width=120)
    ledOnbtn.bind("<Button-1>", bz.SetHigh_ALL)

    ledoffbtn = ttk.Button(modebg, text="LEDon", style="Menu.TButton")
    ledoffbtn.place(x=480,y=520,height= 70, width=120)
    ledoffbtn.bind("<Button-1>", bz.SetLow_ALL)


def cleanmode(root):
    #delete not used frames
    kill(open_frames)
    #create page
    modebg=ttk.Frame(root)
    modebg.place(x=0,y=40,height=560,width=1024)
    #add page to open_frames
    open_frames.append(modebg)
    #Set Label for showing page name in GUI
    lbl=ttk.Label(modebg,text='Cleaning', style="Mode.TLabel")
    lbl.place(x=900,y=0,height=70, width=124)
    #switch valve to water
    bz.SetLow_MagnetVentil1(1)
    bz.SetLow_MagnetVentil2(1)
    # Mode Button
    autobt=ttk.Button(modebg,text='Auto', style="Mode.TButton", command=lambda: automode(root))
    autobt.place(x=0,y=0,height=70,width=120)
    # Platz 1 reinigen Manual
    mancl1bt = ttk.Button(modebg, text="Cleaning\nLeft",style="Menu.TButton")
    mancl1bt.place(x=75,y=290,height=70, width=120)
    mancl1bt.bind("<Button-1>", bz.SetLow_Zapfhahn1)
    mancl1bt.bind("<ButtonRelease-1>", bz.SetHigh_Zapfhahn1)
    
    # Platz 2 reinigen Manual
    mancl2bt = ttk.Button(modebg, text="Cleaning\nRight",style="Menu.TButton")
    mancl2bt.place(x=215,y=290,height=70, width=120)
    mancl2bt.bind("<Button-1>", bz.SetLow_Zapfhahn2)
    mancl2bt.bind("<ButtonRelease-1>", bz.SetHigh_Zapfhahn2)

def statemode(root):
    #delete not used frames
    kill(open_frames)
    #create page
    modebg=ttk.Frame(root, borderwidth=5, relief="ridge")
    modebg.place(x=0,y=40,height=560,width=1024)
    #add page to open_frames
    open_frames.append(modebg)
    #modebg.grid(column=0,row=0)
    table_frame = ttk.Frame(modebg, borderwidth=5, relief="ridge")
    #table_frame.place(x=50, y=50)
    table_frame.grid(column=3, row=1, columnspan=3, rowspan=10)
    lbl=ttk.Label(modebg,text='Status', style="Mode.TLabel")
    lbl.place(x=900,y=0,height=70, width=124)
    # Mode Button
    autobt=ttk.Button(modebg,text='Automatic\nModus', style="Mode.TButton", command=lambda: automode(root))
    #autobt.place(x=0,y=40,height= 36, width=52)
    autobt.grid(column=0, row=0, columnspan=2, rowspan=3)
    
    lbl_promille=ttk.Label(modebg,text="Promille: ", font=("Calibri",16))
    #lbl_promille.place(x=850, y=400, height=20, width=150)
    lbl_promille.place(x=650,y=0,height=70, width=250)
    promille = 0.0
    try:
        my_conn = sqlite3.connect('user.db')
        p = my_conn.cursor()
        p.execute("SELECT promille FROM users WHERE username=?", (lbl_user.cget("text").replace("User: ", ""),))
        promille = p.fetchone()[0]
        r_set=my_conn.execute('''SELECT username, score from users order by score desc limit 0,10''')
        i=0 # row value inside the loop
        e = ttk.Entry(table_frame, font=('Arial', 15, 'bold'), width=5)
        e.grid(row=0,column=0)
        e.insert(tk.END, "Ranking")
        e = ttk.Entry(table_frame, font=('Arial', 15, 'bold'), width=30)
        e.grid(row=0,column=1)
        e.insert(tk.END, "Username")
        e = ttk.Entry(table_frame, font=('Arial', 15, 'bold'), width=5)
        e.grid(row=0,column=2)
        e.insert(tk.END, "Score")
        for user in r_set: 
            e = ttk.Entry(table_frame, font=('Arial', 15), width=5)
            e.grid(row=i+1,column=0)
            e.insert(tk.END, i+1)
            for j in range(len(user)):
                if j==0:
                    e = ttk.Entry(table_frame, font=('Arial', 15), width=30)
                else:
                    e = ttk.Entry(table_frame,font=('Arial', 15), width=5) 
                e.grid(row=i+1, column=j+1) 
                e.insert(tk.END, user[j])
            i=i+1
    finally:
        if my_conn:
            my_conn.close()
    lbl_promille.config(text="Alcohol level: " + str(round(promille,1)), style="Label.TLabel")
    
def dec_promille():
    conn = sqlite3.connect("user.db")
    c = conn.cursor()
    c.execute("SELECT * from users")
    zeilen = c.fetchall()
    for zeile in zeilen:
        username = zeile[1] #username
        promille = zeile[5] #promille-Wert
        promille_neu = float(promille - 0.15)
        if promille_neu < 0:
            promille_neu = 0.0       
        #Aktualisiere Wert in Datenbank
        c.execute("update users set promille = ? where username = ?", (promille_neu, username))
        conn.commit()
    conn.close()
    lbl.after(3600000, dec_promille)
#initialize GPIO-Pins

bz.init_GPIO()
print("GPIO InitGUI")
#start decrementing alcohol-level each hour
dec_promille()
#open start page 
startpage(root, lbl_user, lbl_score)

root.mainloop()