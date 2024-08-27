import cv2
import numpy as np
import time
#import keyboard
import Jetson.GPIO as GPIO
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)


Motor2_einfahren = 35
Motor2_ausfahren = 37
Zapfhahn2 = 21
LED1 = 13

GPIO.setup(LED1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor2_einfahren, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor2_ausfahren, GPIO.OUT, initial=GPIO.LOW)
GPIO.output( LED1, GPIO.LOW)

GPIO.output( Motor2_einfahren, GPIO.LOW)
GPIO.output( Motor2_ausfahren, GPIO.LOW)

GPIO.setup(Zapfhahn2, GPIO.OUT, initial=GPIO.HIGH)



# Feste HSV-Werte einstellen
hMin = 0
sMin = 0
vMin = 200
hMax = 179
sMax = 255
vMax = 255

# Mindestlänge für vertikale Kanten
min_length = 100

# Prozentsatz für die Grenzwerte relativ zur Bildbreite
lower_bound_pct = 0.4  # 30% von der Bildbreite
upper_bound_pct = 0.8  # 70% von der Bildbreite

# Rechteck-Koordinaten (x, y, Breite, Höhe)
rect_x = 0
rect_y = 0
rect_width = 1280
rect_height = 960

# Webcam initialisieren (0 für die Standard-Webcam)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Webcam konnte nicht geöffnet werden.")
    exit()

def show_preview():
    """
    Zeigt ein Vorschaufenster an, das das Webcam-Bild mit den oberen und unteren Grenzwerten darstellt.
    Das Fenster schließt sich, wenn eine Taste gedrückt wird.
    """
    while True:
        ret, img = cap.read()
        if not ret:
            print("Kein Bild von der Webcam erhalten.")
            break

        # Zuschneiden des Bildes
        img = img[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
        height, width = img.shape[:2]
        lower_bound = int(lower_bound_pct * width)
        upper_bound = int(upper_bound_pct * width)

        # Zeichnen der Grenzwerte als vertikale Linien
        cv2.line(img, (lower_bound, 0), (lower_bound, height), (0, 255, 255), 2)
        cv2.line(img, (upper_bound, 0), (upper_bound, height), (0, 255, 255), 2)

        # Anzeigetext hinzufügen
        cv2.putText(img, "Preview: Press any key to start", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Vorschau anzeigen
        cv2.imshow('Preview', img)

        # Wenn eine Taste gedrückt wird, das Fenster schließen
        if cv2.waitKey(1) != -1:
            break

    cv2.destroyWindow('Preview')

# Vorschau anzeigen
show_preview()

# Status der Aktionen
action_status = "idle"

def close_valve():
    """Ventil schließen."""
    GPIO.output( Zapfhahn2, GPIO.HIGH)
    print("Ventil schließen")


def perform_action_1():
    global action_status
    print("Aktion 1: Motor ausfahren")
    GPIO.output( Motor2_einfahren, GPIO.LOW)
    GPIO.output( Motor2_ausfahren, GPIO.HIGH)
    time.sleep(10)  # Motor ausfahren simuliert durch eine Zeitverzögerung
    GPIO.output( Zapfhahn2, GPIO.LOW)
    GPIO.output( LED1, GPIO.HIGH)
    print("Ventil aufmachen")
    action_status = "waiting_for_action_1"

def perform_action_2():
    global action_status
    GPIO.output( Zapfhahn2, GPIO.LOW)
    print("Aktion 2: Ventil aufmachen")
    action_status = "waiting_for_action_2"

def perform_action_3():
    global action_status
    close_valve()  # Ventil schließen bevor das Programm beendet wird
    print("Aktion 3: Programm beenden")
    GPIO.output( LED1, GPIO.LOW)
    cap.release()
    cv2.destroyAllWindows()
    exit()

def handle_action_1():
    global action_status
    ret, img = cap.read()
    if not ret:
        print("Kein Bild von der Webcam erhalten.")
        return
    
    # Zuschneiden des Bildes
    img = img[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
    height, width = img.shape[:2]
    lower_bound = int(lower_bound_pct * width)
    upper_bound = int(upper_bound_pct * width)

    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(img, img, mask=mask)
    edges = cv2.Canny(output, 100, 200)
    kernel = np.ones((5, 5), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vertical_contours = []
    for contour in contours:
        _, _, w, h = cv2.boundingRect(contour)
        if h > w and h >= min_length:
            vertical_contours.append((contour, h))

    vertical_contours = sorted(vertical_contours, key=lambda x: x[1], reverse=True)
    two_longest_contours = [cnt[0] for cnt in vertical_contours[:1]]

    x_coords = []
    for contour in two_longest_contours:
        for point in contour:
            x_coords.append(point[0][0])

    mean_x = None
    if x_coords:
        mean_x = int(np.mean(x_coords))
    
    # In Aktion 1 übergehen, wenn keine Kante erkannt wurde
    if mean_x is None:
        print("Keine Kante erkannt")
        perform_action_1()
    elif mean_x < lower_bound:
        print("Kante unter Grenzwert 1")
        perform_action_1()
    elif lower_bound <= mean_x <= upper_bound:
        print("Kante zwischen Grenzwerten 1 und 2")
        perform_action_2()
    elif mean_x > upper_bound:
        print("Kante über Grenzwert 2")
        perform_action_3()

def wait_for_action_1():
    global action_status
    ret, img = cap.read()
    if not ret:
        print("Kein Bild von der Webcam erhalten.")
        return
    
    # Zuschneiden des Bildes
    img = img[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
    height, width = img.shape[:2]
    lower_bound = int(lower_bound_pct * width)
    upper_bound = int(upper_bound_pct * width)

    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(img, img, mask=mask)
    edges = cv2.Canny(output, 100, 200)
    kernel = np.ones((5, 5), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vertical_contours = []
    for contour in contours:
        _, _, w, h = cv2.boundingRect(contour)
        if h > w and h >= min_length:
            vertical_contours.append((contour, h))

    vertical_contours = sorted(vertical_contours, key=lambda x: x[1], reverse=True)
    two_longest_contours = [cnt[0] for cnt in vertical_contours[:1]]

    x_coords = []
    for contour in two_longest_contours:
        for point in contour:
            x_coords.append(point[0][0])

    mean_x = None
    if x_coords:
        mean_x = int(np.mean(x_coords))

    if mean_x is not None:
        lower_bound = int(lower_bound_pct * width)
        upper_bound = int(upper_bound_pct * width)
        
        if lower_bound <= mean_x <= upper_bound:
            print("Kante zwischen Grenzwerten 1 und 2")
            close_valve()  # Ventil schließen bevor der Motor eingefahren wird
            GPIO.output( Motor2_einfahren, GPIO.HIGH)
            GPIO.output( Motor2_ausfahren, GPIO.LOW)
            print("Motor einfahren")
            time.sleep(10)
            action_status = "action_2"
        else:
            print("Kante noch nicht im gewünschten Bereich")

def wait_for_action_2():
    global action_status
    ret, img = cap.read()
    if not ret:
        print("Kein Bild von der Webcam erhalten.")
        return
    
    # Zuschneiden des Bildes
    img = img[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
    height, width = img.shape[:2]
    lower_bound = int(lower_bound_pct * width)
    upper_bound = int(upper_bound_pct * width)

    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(img, img, mask=mask)
    edges = cv2.Canny(output, 100, 200)
    kernel = np.ones((5, 5), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vertical_contours = []
    for contour in contours:
        _, _, w, h = cv2.boundingRect(contour)
        if h > w and h >= min_length:
            vertical_contours.append((contour, h))

    vertical_contours = sorted(vertical_contours, key=lambda x: x[1], reverse=True)
    longest_contours = [cnt[0] for cnt in vertical_contours[:1]]

    x_coords = []
    for contour in longest_contours:
        for point in contour:
            x_coords.append(point[0][0])

    mean_x = None
    if x_coords:
        mean_x = int(np.mean(x_coords))

    if mean_x is not None:
        if mean_x > upper_bound:
            print("Kante über Grenzwert 2")
            close_valve()  # Ventil schließen bevor das Programm beendet wird
            action_status = "action_3"
        else:
            print("Kante noch nicht über Grenzwert 2")

while True:
    if action_status == "idle":
        handle_action_1()
    elif action_status == "waiting_for_action_1":
        wait_for_action_1()
    elif action_status == "action_2":
        perform_action_2()
    elif action_status == "waiting_for_action_2":
        wait_for_action_2()
    elif action_status == "action_3":
        perform_action_3()

    # # Beenden, wenn die 'q'-Taste gedrückt wird
    # if keyboard.is_pressed('q'):
    #     close_valve()  # Ventil schließen, wenn 'q' gedrückt wird
    #     break

# Webcam freigeben und Fenster schließen
cap.release()
cv2.destroyAllWindows()
