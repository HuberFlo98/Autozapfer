import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import Text
from PIL import Image, ImageTk

import Jetson.GPIO as GPIO

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)


Motor2_einfahren = 35
Motor2_ausfahren = 37
Zapfhahn2 = 21
LED1 = 11

GPIO.setup(LED1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor2_einfahren, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor2_ausfahren, GPIO.OUT, initial=GPIO.LOW)
GPIO.output( LED1, GPIO.LOW)

GPIO.output( Motor2_einfahren, GPIO.LOW)
GPIO.output( Motor2_ausfahren, GPIO.LOW)

GPIO.setup(Zapfhahn2, GPIO.OUT, initial=GPIO.HIGH)





# Funktion zum Anzeigen von Logs im Textfeld
def log_message(message):
    log_text.insert(tk.END, message + '\n')
    log_text.see(tk.END)

# Funktion, um den Button zu klicken und Status 3 zu aktivieren
def button_pressed():
    log_message("Button gedrückt. Ventil wird geschlossen und Motor fährt herunter.")
    print("Button gedrückt. Ventil wird geschlossen und Motor fährt herunter.")
    # Hier Aktionen zum Schließen des Ventils und Herunterfahren des Motors
    GPIO.output(Zapfhahn2, GPIO.HIGH)
    log_message("Ventil geschlossen.")
    print("Ventil geschlossen.")
    # Motor fährt 10 Sekunden herunter
    GPIO.output( Motor2_einfahren, GPIO.HIGH)
    GPIO.output( Motor2_ausfahren, GPIO.LOW)
    log_message("Motor fährt für 10 Sekunden herunter.")
    print("Motor fährt für 10 Sekunden herunter.")
    time.sleep(10)
    
    # Programm beenden nach 10 Sekunden
    log_message("Programm wird beendet.")
    root.quit()

# Hauptfenster einrichten
root = tk.Tk()
root.title("Kanten Overlay mit Steuerung")
root.geometry("1280x720")  # Initiale Fenstergröße, wird gleich auf Vollbild gesetzt
root.attributes("-fullscreen", True)  # Setzt das Fenster auf Vollbild

# Frame für die Webcam und den Button erstellen
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Label für das Webcam-Bild
video_label = tk.Label(main_frame)
video_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Knopf auf der rechten Seite
button_frame = tk.Frame(main_frame)
button_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
btn = tk.Button(button_frame, text="Cancel", command=button_pressed, font=("Arial", 20), state=tk.DISABLED)
btn.pack(pady=20)

# Textfeld für Logs unterhalb des Kamerabildes
log_text = Text(root, height=10)
log_text.pack(fill=tk.X, padx=10, pady=10)

# Kamera initialisieren
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    log_message("Fehler beim Öffnen der Kamera")
    exit()

previous_position_status = None  # Speichert den vorherigen Status (None als initialer Wert)
allowed_status_change = {1: [2, 3], 2: [3], 3: []}  # Erlaubte Statusänderungen
initial_status_evaluated = False  # Überprüft, ob der Startstatus bereits evaluiert wurde
action2_executed = False  # Flag, um zu überprüfen, ob Aktion 2 bereits ausgeführt wurde
position_status = None  # Startet ohne Status


def update_frame():
    global previous_position_status, initial_status_evaluated, action2_executed, position_status
    
    # Ein Frame von der Kamera lesen
    ret, img = cap.read()
    if not ret:
        log_message("Fehler beim Lesen des Frames oder Ende des Streams")
        position_status = 3
        return


    # Feste HSV-Werte
    hMin, sMin, vMin, hMax, sMax, vMax = 0, 0, 255, 179, 255, 255

    # Mindestlänge für vertikale Kanten
    min_length = 100

    # Grenzwerte für den Mittelwert der X-Koordinaten
    lower_bound = 200
    upper_bound = 400

    # Mindest- und Maximal-HSV-Werte festlegen
    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])

    # HSV-Bild erstellen und in einem Bereich filtern
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(img, img, mask=mask)

    # Canny-Kantenerkennung anwenden
    edges = cv2.Canny(output, 100, 200)

    # Kanten verdicken
    kernel = np.ones((5, 5), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)

    # Konturen basierend auf den Kanten finden
    contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Nur vertikale Konturen filtern
    vertical_contours = []
    for contour in contours:
        _, _, w, h = cv2.boundingRect(contour)
        if h > w and h >= min_length:
            vertical_contours.append((contour, h))

    # Sortieren der vertikalen Konturen nach Länge (absteigend)
    vertical_contours = sorted(vertical_contours, key=lambda x: x[1], reverse=True)

    # Auswahl der längsten Konturen
    two_longest_contours = [cnt[0] for cnt in vertical_contours[:1]]

    # Leeres Bild zum Zeichnen der zwei längsten vertikalen Konturen erstellen
    edges_colored = np.zeros_like(img)

    # Die zwei längsten vertikalen Konturen in Gelb zeichnen
    cv2.drawContours(edges_colored, two_longest_contours, -1, (255, 255, 0), 2)

    # Kantenbild mit dem Originalbild überlagern
    overlay = cv2.addWeighted(img, 0.8, edges_colored, 0.2, 0)

    # Mittelwert der X-Koordinaten der erkannten Konturen berechnen
    x_coords = []
    for contour in two_longest_contours:
        for point in contour:
            x_coords.append(point[0][0])

    if not x_coords:
        position_status = 1
        #cv2.putText(overlay, "Keine Kante erkannt, Status 1", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    else:
        mean_x = int(np.mean(x_coords))
        cv2.line(overlay, (mean_x, 0), (mean_x, overlay.shape[0]), (0, 0, 255), 2)

        if mean_x < lower_bound:
            position_status = 1
            #cv2.putText(overlay, "Unter Grenzwert 1", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        elif mean_x > upper_bound:
            position_status = 3
            #cv2.putText(overlay, "Über Grenzwert 2", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            position_status = 2
            #cv2.putText(overlay, "Zwischen Wert 1 und 2", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)


    # Verarbeite Statusänderungen und aktiviere/deaktiviere den Button
    if position_status == 1 or position_status == 2 :
        btn.config(state=tk.NORMAL)  # Button aktivieren
    else:
        btn.config(state=tk.DISABLED)  # Button deaktivieren

    if previous_position_status != position_status:
        if position_status == 1 and not action2_executed:
            log_message("Aktion für Status 1: Motor ausfahren")
            print("Motor ausfahren")
            GPIO.output( Motor2_einfahren, GPIO.LOW)
            GPIO.output( Motor2_ausfahren, GPIO.HIGH)
            time.sleep(10)  # Motor ausfahren simuliert durch eine Zeitverzögerung
            GPIO.output( LED1, GPIO.HIGH)
            print("LED ON")
            log_message("Aktion für Status 1: LED ON")
            GPIO.output( Zapfhahn2, GPIO.LOW)
            print("Ventil aufmachen")
            log_message("Aktion für Status 1: Ventil aufmachen")
        elif position_status == 2 and not action2_executed:
            action2_executed = True
            log_message("Aktion für Status 2: Ventil schließen")
            GPIO.output( Zapfhahn2, GPIO.HIGH)
            print("Ventil schließen")
            GPIO.output( Motor2_einfahren, GPIO.HIGH)
            GPIO.output( Motor2_ausfahren, GPIO.LOW)
            print("Motor einfahren")
            log_message("Aktion für Status 2: Motor einfahren")
            time.sleep(10)
            GPIO.output( LED1, GPIO.HIGH)
            print("LED ON")
            log_message("Aktion für Status 2: LED ON")
            GPIO.output( Zapfhahn2, GPIO.LOW)
            print("Ventil aufmachen")
            log_message("Aktion für Status 2: Ventil aufmachen")
        elif position_status == 3:
            log_message("Aktion für Status 3: Über Grenzwert. Keine weitere Aktion möglich.")
            print("Aktion für Status 3: Über Grenzwert 2")
            GPIO.output( LED1, GPIO.LOW)
            GPIO.output( Zapfhahn2, GPIO.HIGH)
            print("Ventil schließen")
            print("Programm wird in 10 Sekunden beendet.")
            time.sleep(10)
            root.quit()

    # Grenzwerte als vertikale Linien einzeichnen
    cv2.line(overlay, (lower_bound, 0), (lower_bound, overlay.shape[0]), (0, 255, 255), 2)
    cv2.line(overlay, (upper_bound, 0), (upper_bound, overlay.shape[0]), (0, 255, 255), 2)

    # Bild konvertieren und anzeigen
    img_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)

    video_label.imgtk = img_tk
    video_label.config(image=img_tk)

    previous_position_status = position_status

    # Aktualisiere das Frame nach einer kurzen Verzögerung erneut
    root.after(10, update_frame)

# Startet das Video-Update
update_frame()

# Hauptloop starten
root.mainloop()

# Kamera freigeben
cap.release()
cv2.destroyAllWindows()
