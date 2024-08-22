import cv2
import numpy as np
import time

# Feste HSV-Werte einstellen
hMin = 0
sMin = 0
vMin = 0
hMax = 179
sMax = 255
vMax = 255

# Mindestlänge für vertikale Kanten
min_length = 50

# Prozentsatz für die Grenzwerte relativ zur Bildbreite
lower_bound_pct = 0.3  # 30% von der Bildbreite
upper_bound_pct = 0.7  # 70% von der Bildbreite

# Webcam initialisieren (0 für die Standard-Webcam)
cap = cv2.VideoCapture(0)

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
program_running = True  # Flag, um den Not-Stop zu überwachen

def close_valve():
    """Ventil schließen."""
    print("Ventil schließen")

def perform_action_1():
    global action_status, program_running
    print("Aktion 1: Motor ausfahren")
    timed_sleep(10)  # Motor ausfahren simuliert durch eine Zeitverzögerung
    if program_running:
        print("Ventil aufmachen")
        action_status = "waiting_for_action_1"

def perform_action_2():
    global action_status, program_running
    print("Aktion 2: Ventil aufmachen")
    if program_running:
        action_status = "waiting_for_action_2"

def perform_action_3():
    global program_running
    close_valve()  # Ventil schließen bevor das Programm beendet wird
    print("Aktion 3: Programm beenden")
    program_running = False

def handle_action_1():
    global action_status, program_running
    ret, img = cap.read()
    if not ret:
        print("Kein Bild von der Webcam erhalten.")
        return
    
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
    global action_status, program_running
    ret, img = cap.read()
    if not ret:
        print("Kein Bild von der Webcam erhalten.")
        return
    
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
            print("Motor einfahren")
            timed_sleep(10)  # Motor einfahren simuliert durch eine Zeitverzögerung
            if program_running:
                action_status = "action_2"
        else:
            print("Kante noch nicht im gewünschten Bereich")

def wait_for_action_2():
    global action_status, program_running
    ret, img = cap.read()
    if not ret:
        print("Kein Bild von der Webcam erhalten.")
        return
    
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
        upper_bound = int(upper_bound_pct * width)
        
        if mean_x > upper_bound:
            close_valve()  # Ventil schließen bevor das Programm beendet wird
            print("Kante über Grenzwert 2")
            action_status = "action_3"
        else:
            print("Kante noch nicht über Grenzwert 2")

def timed_sleep(duration):
    """Simuliert eine Zeitverzögerung, die währenddessen ständig auf Not-Stop überprüft."""
    start_time = time.time()
    while time.time() - start_time < duration:
        if not program_running:
            break
        time.sleep(0.1)

while program_running:
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

    # Beenden, wenn die 'q'-Taste oder die ESC-Taste (Not-Stop) gedrückt wird
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:  # ESC-Taste
        close_valve()
        print("Not-Stop aktiviert. Programm beendet.")
        program_running = False
        break

# Webcam freigeben und Fenster schließen
cap.release()
cv2.destroyAllWindows()
