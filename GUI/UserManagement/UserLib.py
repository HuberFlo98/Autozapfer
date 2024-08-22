#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 27 03:26:02 2023

@author: daniel
"""
import sqlite3
import os

def create_table():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  password TEXT NOT NULL,
                  weight TEXT NOT NULL,
                  score INTEGER,
                  promille REAL,
                  card_id TEXT NOT NULL,
                  picture TEXT NOT NULL)''')
    conn.commit()
    conn.close()
    
def register_user(username_entry, password_entry, weight_entry, label_feedback,fr):
    username = username_entry.get()
    password = password_entry.get()
    weight = weight_entry.get()

    # Überprüfen, ob der Benutzer bereits existiert
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        label_feedback.place(x=50, y=290, height=30)
        label_feedback.config(text="User already exists")
    else:
        # Benutzer in die Datenbank einfügen
        if username == "" or password == "" or (not weight.isnumeric()):
            label_feedback.place(x=50, y=290, height=30)
            label_feedback.config(text="Check entries")
        else:
            c.execute("INSERT INTO users (username, password, weight, score, promille, card_id, picture) VALUES (?, ?, ?, ?, ?, ?, ?)", (username, password, weight, 0, 0.0, "", ""))
            label_feedback.place(x=50, y=290, height=30)
            label_feedback.config(text="Registrations succesful")
            fr.add_faces(username + '.jpg')
    conn.commit()
    conn.close()

def login_user(username_entry, password_entry, label_feedback, label_user, label_score, button_zapfen):
    username = username_entry.get()
    password = password_entry.get()

    # Überprüfen, ob der Benutzer in der Datenbank existiert und das Passwort übereinstimmt
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    w = conn.cursor()
    w.execute("SELECT score FROM users WHERE username=? AND password=?", (username, password))
    if c.fetchone():
        score = int(w.fetchone()[0])
        label_user.config(text="User: " + username)
        label_score.config(text="Score: " + str(score))
        label_feedback.place(x=50, y=240, height=30)
        label_feedback.config(text="Login succesful")
        button_zapfen.config(state="normal")
    else:
        label_feedback.place(x=50, y=240, height=30)
        label_feedback.config(text="Invalid username or password")
    conn.close()
def login_faceid(username, username_entry, password_entry):
    conn = sqlite3.connect('user.db')
    c=conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username))
    password = c.fetchone()
    if password is not None:
        username_entry.config(text=username)
        password_entry.config(text=password)
    conn.commit()
    conn.close()
    
def login_guest(label_feedback, label_user, label_score, button_zapfen):
    label_user.config(text="User: Gast")
    label_score.config(text="Score: 0")
    label_feedback.place(x=50, y=240, height=30)
    label_feedback.config(text="Login succesful")
    button_zapfen.config(state="normal")
def delete_user(username_entry, password_entry, label_feedback,fr):
    username = username_entry.get()
    password = password_entry.get()

    # Überprüfen, ob der Benutzer in der Datenbank existiert und das Passwort übereinstimmt
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    if c.fetchone():
        c.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        conn.close()
        label_feedback.place(x=50, y=240, height=30)
        label_feedback.config(text="User deleted")
        try:
            picture_path = '/home/autozapfer/Dokumente/Software/GUI/BV/known_faces/' + username + '.jpg'
            fr.remove_faces(username + '.jpg')
            os.remove(picture_path)           
        except OSError as e:
            print("Error while deleting file:", e)
    else:
        conn.close()
        label_feedback.place(x=50, y=240, height=30)
        label_feedback.config(text="Invalid username or password")
def inc_promille(label_user, label_score):
    try:
        print("Inc Promille")
        username = label_user.cget("text").replace("User: ", "")
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        w = conn.cursor()
        w.execute("SELECT weight FROM users WHERE username=?", (username,))
        s = conn.cursor()
        s.execute("SELECT score FROM users WHERE username=?", (username,))
        p = conn.cursor()
        p.execute("SELECT promille FROM users WHERE username=?", (username,))                

        if c.fetchone():
            weight = int(w.fetchone()[0])
            score_old = int(s.fetchone()[0])
            promille_old = float(p.fetchone()[0])
            promille_val = 20/(weight * 0.7) #Alkohol in g / (Körpgergewicht * Wasseranteil)
            promille_new = float(promille_old) + promille_val
            score_new = score_old + 1
            label_score.config(text="Score: " + str(score_new))
            c.execute("update users set promille = ? where username = ?", (promille_new, username))
            c.execute("update users set score = ? where username = ?", (score_new, username))
            conn.commit()
    finally:
        if conn:
            conn.close()