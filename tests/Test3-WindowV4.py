import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import Text
from PIL import Image, ImageTk

#import Jetson.GPIO as GPIO
#GPIO.cleanup()
#GPIO.setmode(GPIO.BOARD)

motor_active = False
Motor2_einfahren = 35
Motor2_ausfahren = 37
Zapfhahn2 = 21
LED1 = 11

#GPIO.setup(LED1, GPIO.OUT, initial=GPIO.LOW)
#GPIO.setup(Motor2_einfahren, GPIO.OUT, initial=GPIO.LOW)
#GPIO.setup(Motor2_ausfahren, GPIO.OUT, initial=GPIO.LOW)
#GPIO.output( LED1, GPIO.HIGH)

#GPIO.output( Motor2_einfahren, GPIO.LOW)
#GPIO.output( Motor2_ausfahren, GPIO.LOW)

#GPIO.setup(Zapfhahn2, GPIO.OUT, initial=GPIO.HIGH)

# Timer für die Zeit ohne erkannte Kante
no_edge_start_time = None  # Zeit, zu der keine Kante erkannt wurde
max_no_edge_time = 4  # Zeit in Sekunden, nach der abgebrochen wird
no_edge=False

# Funktion zum Überprüfen, ob 4 Sekunden vergangen sind, ohne eine Kante zu finden
def check_no_edge_duration():
    global no_edge_start_time
    global max_no_edge_time
    global no_edge
    
    # Prüfe, ob der Timer gestartet ist und ob 4 Sekunden vergangen sind
    if no_edge_start_time and ((time.time() - no_edge_start_time) >= max_no_edge_time)and not no_edge:
        no_edge=True
        log_message("Keine Kante für 4 Sekunden erkannt")
        print("Keine Kante seit 4 Sekunden erkannt. Abbruch.")
        #GPIO.output(Zapfhahn2, GPIO.HIGH)
        print("Ventil schließen")
        log_message("Ventil schließen")
        motor_einfahren()  # Motor einfährt
        root.after(10000, root_quit)  # Beende das Programm

def motor_ausfahren():
    global motor_active
    motor_active = True
    log_message("... Motor fährt aus")
    print("Motor fährt aus")
    #GPIO.output(Motor2_ausfahren, GPIO.HIGH)
    #GPIO.output(Motor2_einfahren, GPIO.LOW)

def motor_einfahren():
    global motor_active
    motor_active = True
    log_message("... Motor fährt ein")
    print("Motor fährt ein")
    #GPIO.output(Motor2_ausfahren, GPIO.LOW)
    #GPIO.output(Motor2_einfahren, GPIO.HIGH)

# Funktion, die nach 10 Sekunden ausgeführt wird, um den Ablauf fortzusetzen
def Status1_Motor_ausgefahren():
    global valve_open
    global motor_active
    motor_active = False
    log_message("Aktion für Status 1: Motor ausgefahren")
    print("Motor ist jetzt ausgefahren")

    #GPIO.output(Zapfhahn2, GPIO.LOW)
    print("Ventil aufmachen")
    log_message("Aktion für Status 1: Ventil aufgemacht")
    valve_open = True


def Status2_Motor_eingefahren():
    global valve_open
    global motor_active
    motor_active = False
    log_message("Aktion für Status 2: Motor eingefahren")
    print("Motor ist jetzt eingefahren")


    #GPIO.output( Zapfhahn2, GPIO.LOW)
    print("Ventil aufmachen")
    log_message("Aktion für Status 2: Ventil aufgemacht")
    valve_open = True


def button_pressed_action():
    log_message("Programm wird beendet.")



# Funktion zum Anzeigen von Logs im Textfeld
def log_message(message):
    log_text.insert(tk.END, message + '\n')
    log_text.see(tk.END)

# Funktion, um den Button zu klicken und Status 3 zu aktivieren
def button_pressed():
    global valve_open

    log_message("Aktion für Button: Button gedrückt")
    print("Button gedrückt. Ventil wird geschlossen und Motor fährt herunter.")

    #GPIO.output(Zapfhahn2, GPIO.HIGH)
    log_message("Aktion für Button: Ventil geschlossen.")
    print("Ventil geschlossen.")
    valve_open=False

    # Motor fährt 10 Sekunden herunter
    motor_einfahren()
    root.after(10000, button_pressed_action)
    global motor_active
    motor_active = False
    root.after(10000, root_quit)

def root_quit():
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
# Timer für Kantenlos-Zeit
last_edge_detected_time = time.time()  # Zeit, wann die letzte Kante erkannt wurde
edge_timeout = 4  # Sekunden, nach denen das Ventil geschlossen werden soll, wenn keine Kante gefunden wird
valve_open = False  # Status, ob das Ventil offen ist

def update_frame():
    global previous_position_status, initial_status_evaluated, action2_executed, position_status,no_edge_start_time, valve_open
    

    #---------------------------------------------------------------------------------#
    # Ein Frame von der Kamera lesen
    ret, img = cap.read()
    if not ret:
        log_message("Fehler beim Lesen des Frames oder Ende des Streams")
        #GPIO.output(Zapfhahn2, GPIO.HIGH)
        log_message("Ventil geschlossen.")
        print("Ventil geschlossen.")
        motor_einfahren()
        root.after(10000, root_quit)


    
    # Bilddimensionen abrufen
    img_height, img_width = img.shape[:2]
    # Punkte zum Zuschneiden definieren (nur y-Achse berücksichtigen)
    pts = np.array([[0, 100], [img_width, 100], [img_width, img_height], [0, img_height]])

    # Rechteck beschneiden (nur y-Koordinaten werden hier benutzt)
    rect = cv2.boundingRect(pts)
    x, y, w, h = rect

    # x-Koordinate und Breite auf volle Bildbreite setzen
    x = 0
    w = img_width

    # Bild zuschneiden (ohne Überprüfung)
    image = img[y:y+h, x:x+w].copy()

    #-----------------------------PARAMETER-------------------------------------------#
    # Feste HSV-Werte
    hMin, sMin, vMin, hMax, sMax, vMax = 0, 0, 255, 179, 255, 255

    # Mindestlänge für vertikale Kanten
    min_length = 110

    # Grenzwerte für den Mittelwert der X-Koordinaten
    lower_bound = 100
    upper_bound = 200

    #-----------------------------Bildverarbeitung------------------------------------#

    # Mindest- und Maximal-HSV-Werte festlegen
    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])

    # HSV-Bild erstellen und in einem Bereich filtern
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)

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
    longest_contours = [cnt[0] for cnt in vertical_contours[:1]]

    # Leeres Bild zum Zeichnen der zwei längsten vertikalen Konturen erstellen
    edges_colored = np.zeros_like(image)

    # Die zwei längsten vertikalen Konturen in Gelb zeichnen
    cv2.drawContours(edges_colored, longest_contours, -1, (255, 255, 0), 2)

    # Kantenbild mit dem Originalbild überlagern
    overlay = cv2.addWeighted(image, 0.8, edges_colored, 0.2, 0)

    # Mittelwert der X-Koordinaten der erkannten Konturen berechnen
    x_coords = []
    for contour in longest_contours:
        for point in contour:
            x_coords.append(point[0][0])

    # Überprüfen, ob keine Kante erkannt wurde
    if not vertical_contours and valve_open==True:
        if no_edge_start_time is None:
            # Starte den Timer, wenn dies das erste Mal ist, dass keine Kante gefunden wurde
            no_edge_start_time = time.time()
        else:
            # Überprüfe, ob 4 Sekunden vergangen sind
            check_no_edge_duration()
    else:
        # Eine Kante wurde erkannt, setze den Timer zurück
        no_edge_start_time = None

    if not x_coords:
        position_status = 1
        #cv2.putText(overlay, "Keine Kante erkannt, Status 1", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    else:
        mean_x = int(np.mean(x_coords))
        cv2.line(overlay, (mean_x, 0), (mean_x, overlay.shape[0]), (0, 0, 255), 2)
    #-----------------------------Auswertung------------------------------------#
        if mean_x < lower_bound:
            position_status = 1
        elif mean_x > upper_bound:
            position_status = 3
        else:
            position_status = 2


    # Verarbeite Statusänderungen und aktiviere/deaktiviere den Button
    if (position_status == 1 or position_status == 2) and not motor_active==True :
        btn.config(state=tk.NORMAL)  # Button aktivieren
    else:
        btn.config(state=tk.DISABLED)  # Button deaktivieren
    if not motor_active:
        if previous_position_status != position_status:

            if position_status == 1 and not action2_executed:

                log_message("Aktion für Status 1: Motor ausfahren")
                motor_ausfahren()  # Starte den Motor
                root.after(10000, Status1_Motor_ausgefahren)

            elif position_status == 2 and not action2_executed:
                action2_executed = True

                #GPIO.output( Zapfhahn2, GPIO.HIGH)
                print("Ventil schließen")
                log_message("Aktion für Status 2: Ventil schließen")
                valve_open=False

                motor_einfahren()
                root.after(10000, Status2_Motor_eingefahren)
        
            elif position_status == 3 and action2_executed == False:
                log_message("Aktion für Status 3: Über Grenzwert 2")
                print("Aktion für Status 3: Über Grenzwert 2")

                #GPIO.output(Zapfhahn2, GPIO.HIGH)
                log_message("Aktion für Status 3: Ventil geschlossen.")
                print("Ventil geschlossen") 
                valve_open=False

                motor_einfahren()
                root.after(10000, root_quit)

            elif position_status == 3 and action2_executed == True:
                log_message("Aktion für Status 3: Über Grenzwert. Keine weitere Aktion möglich.")
                print("Aktion für Status 3: Über Grenzwert 2")


                #GPIO.output( Zapfhahn2, GPIO.HIGH)
                print("Ventil schließen")            
                log_message("Aktion für Status 3: Ventil schließen")
                valve_open=False

                root_quit()

    # Grenzwerte als vertikale Linien einzeichnen
    cv2.line(overlay, (lower_bound, 0), (lower_bound, overlay.shape[0]), (0, 255, 255), 2)
    cv2.line(overlay, (upper_bound, 0), (upper_bound, overlay.shape[0]), (0, 255, 255), 2)

    # Bild um 90° gegen den Uhrzeigersinn drehen
    overlay = cv2.rotate(overlay, cv2.ROTATE_90_COUNTERCLOCKWISE)

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
