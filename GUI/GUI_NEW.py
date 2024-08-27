import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import hashlib
import os
import time

# Globale Variablen für Benutzerinformationen
user_data = {}
current_user_image = None

# Funktion zum Hashen von Passwörtern
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Funktion für die Registrierung
def register_user(username, password, image):
    global user_data
    user_data[username] = {'password': hash_password(password), 'image': image}
    messagebox.showinfo("Erfolg", "Registrierung erfolgreich!")

# Funktion zum Überprüfen der Anmeldedaten
def check_login(username, password):
    global user_data
    if username in user_data and user_data[username]['password'] == hash_password(password):
        open_main_menu()
    else:
        messagebox.showerror("Fehler", "Falscher Benutzername oder Passwort!")

# Funktion zur Aufnahme eines Bildes mit der Webcam
def capture_image():
    global current_user_image
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Fehler", "Konnte kein Bild aufnehmen.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        if len(faces) > 0:
            current_user_image = frame
            cap.release()
            cv2.destroyAllWindows()
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            image = image.resize((250, 250))
            img = ImageTk.PhotoImage(image)
            lbl_img.config(image=img)
            lbl_img.image = img
            break

        # Zeigt das Live-Bild in einem kleinen Fenster
        cv2.imshow('Suche nach Gesicht...', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Funktion zum Registrierungsfenster
def open_registration():
    reg_window = tk.Toplevel(root)
    reg_window.title("Registrierung")
    reg_window.geometry("400x400")

    tk.Label(reg_window, text="Benutzername:").pack()
    reg_username = tk.Entry(reg_window)
    reg_username.pack()

    tk.Label(reg_window, text="Passwort:").pack()
    reg_password = tk.Entry(reg_window, show='*')
    reg_password.pack()

    tk.Button(reg_window, text="Bild aufnehmen", command=capture_image).pack()

    global lbl_img
    lbl_img = tk.Label(reg_window)
    lbl_img.pack()

    def save_registration():
        if reg_username.get() and reg_password.get() and current_user_image is not None:
            register_user(reg_username.get(), reg_password.get(), current_user_image)
            reg_window.destroy()
        else:
            messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen und ein Bild aufnehmen.")

    tk.Button(reg_window, text="Registrieren", command=save_registration).pack()

# Funktion zur Gesichtserkennung für den Login
def face_recognition_login():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Fehler", "Konnte kein Bild aufnehmen.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        if len(faces) > 0:
            cap.release()
            cv2.destroyAllWindows()
            for username, data in user_data.items():
                if current_user_image is not None:
                    # Hier wird das Bild von der Webcam mit dem gespeicherten Bild verglichen
                    if cv2.norm(frame, data['image']) < 10000:  # Beispielhafte Schwelle
                        open_main_menu()
                        return
            messagebox.showerror("Fehler", "Gesicht nicht erkannt.")
            break

        # Zeigt das Live-Bild in einem kleinen Fenster
        cv2.imshow('Suche nach Gesicht...', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Funktion für das Hauptmenü
def open_main_menu():
    main_menu = tk.Toplevel(root)
    main_menu.title("Hauptmenü")
    main_menu.geometry("400x400")
    tk.Label(main_menu, text="Willkommen im Hauptmenü!").pack()

# Funktion für den Guest-Login
def guest_login():
    open_main_menu()

# Funktion zum Aktualisieren der Uhrzeit
def update_time():
    current_time = time.strftime('%H:%M:%S')
    lbl_time.config(text=current_time)
    root.after(1000, update_time)

# Hauptfenster
root = tk.Tk()
root.title("Login System")
root.geometry("400x400")

lbl_time = tk.Label(root, text="", font=('Helvetica', 12))
lbl_time.pack()
update_time()

tk.Label(root, text="Benutzername:").pack()
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="Passwort:").pack()
entry_password = tk.Entry(root, show='*')
entry_password.pack()

tk.Button(root, text="Login", command=lambda: check_login(entry_username.get(), entry_password.get())).pack()
tk.Button(root, text="Registrierung", command=open_registration).pack()
tk.Button(root, text="Login mit Gesichtserkennung", command=face_recognition_login).pack()
tk.Button(root, text="Guest Login", command=guest_login).pack()

root.mainloop()

