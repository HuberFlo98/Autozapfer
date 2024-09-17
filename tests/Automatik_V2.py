import cv2
import numpy as np
import time

# Funktion zum Drehen eines Bildes um 90 Grad gegen den Uhrzeigersinn
def rotate_image(image):
    return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

# Funktion zum Berechnen der Länge einer Linie
def line_length(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Funktion zum Berechnen des gewichteten Mittelwerts der Kantenpositionen
def calculate_weighted_average_edge_position(lines):
    total_weight = 0
    weighted_sum = 0
    for x1, y1, x2, y2 in lines:
        length = line_length(x1, y1, x2, y2)
        avg_y = (y1 + y2) / 2
        weighted_sum += avg_y * length
        total_weight += length
    if total_weight > 0:
        return int(weighted_sum / total_weight)
    return None

# Funktion zur Berechnung des Winkels einer Linie
def calculate_angle(x1, y1, x2, y2):
    return np.degrees(np.arctan2(y2 - y1, x2 - x1))

# Funktion zum Filtern von Linien nach horizontaler Ausrichtung
def filter_horizontal_lines(lines, angle_threshold=10):
    horizontal_lines = []
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                angle = calculate_angle(x1, y1, x2, y2)
                if abs(angle) <= angle_threshold:
                    horizontal_lines.append((x1, y1, x2, y2))
    return horizontal_lines

# Zugriff auf die Webcam (Kamera 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Fehler: Webcam konnte nicht geöffnet werden")
    exit()

# HSV-Bereich festlegen
hMin = 0
sMin = 0
vMin = 100
hMax = 150
sMax = 100
vMax = 255

# Erstellen eines HSV-Min/Max-Arrays
lower_hsv = np.array([hMin, sMin, vMin])
upper_hsv = np.array([hMax, sMax, vMax])

# Status der Aktionen
action_status = "idle"

def close_valve():
    """Ventil schließen."""
    print("Ventil schließen")

def perform_action_1():
    global action_status
    print("Aktion 1: Motor ausfahren")
    time.sleep(10)  # Motor ausfahren simuliert durch eine Zeitverzögerung
    print("Ventil aufmachen")
    action_status = "waiting_for_action_1"

def perform_action_2():
    global action_status
    print("Aktion 2: Ventil aufmachen")
    action_status = "waiting_for_action_2"

def perform_action_3():
    global action_status
    close_valve()  # Ventil schließen bevor das Programm beendet wird
    print("Aktion 3: Programm beenden")
    cap.release()
    cv2.destroyAllWindows()
    exit()

def handle_action_1(mean_x, lower_bound, middle_threshold):
    global action_status
    if mean_x is None:
        print("Keine Kante erkannt")
        perform_action_1()
    elif mean_x > lower_bound:
        print("Kante unter Grenzwert 1")
        perform_action_1()
    elif middle_threshold <= mean_x < lower_bound:
        print("Kante zwischen Grenzwerten 1 und 2")
        perform_action_2()
    elif mean_x < middle_threshold:
        print("Kante über Grenzwert 2")
        perform_action_3()

def wait_for_action_1(mean_x, middle_threshold):
    global action_status
    if middle_threshold <= mean_x < lower_bound:
        print("Kante zwischen Grenzwerten 1 und 2")
        close_valve()  # Ventil schließen bevor der Motor eingefahren wird
        print("Motor einfahren")
        time.sleep(10)
        action_status = "action_2"
    else:
        print("Kante noch nicht im gewünschten Bereich")

def wait_for_action_2(mean_x, upper_limit):
    global action_status
    if mean_x < upper_limit:
        close_valve()  # Ventil schließen bevor das Programm beendet wird
        print("Kante über Grenzwert 2")
        action_status = "action_3"
    else:
        print("Kante noch nicht unter Grenzwert 2")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fehler: Bild konnte nicht aufgenommen werden")
        break

    # Bild um 90 Grad gegen den Uhrzeigersinn drehen
    rotated_frame = rotate_image(frame)

    # Bild von BGR zu HSV konvertieren
    hsv_frame = cv2.cvtColor(rotated_frame, cv2.COLOR_BGR2HSV)

    # Maske basierend auf HSV-Werten erstellen
    mask = cv2.inRange(hsv_frame, lower_hsv, upper_hsv)

    # Maske auf das Bild anwenden
    masked_frame = cv2.bitwise_and(rotated_frame, rotated_frame, mask=mask)

    # Technik 1: Bild glätten, um unnötige Details zu entfernen
    blurred_frame = cv2.GaussianBlur(masked_frame, (5, 5), 0)

    # Kanten im maskierten und geglätteten Bild mit Canny finden
    edges = cv2.Canny(blurred_frame, 100, 200)

    # Hough-Linien-Transformation verwenden, um Linien zu erkennen
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=50, maxLineGap=10)

    # Nur fast waagerechte Linien filtern (±50 Grad)
    horizontal_lines = filter_horizontal_lines(lines, angle_threshold=50)

    # Durchschnitt der Kantenpositionen berechnen (y-Achse)
    avg_edge_pos = calculate_weighted_average_edge_position(horizontal_lines)

    # Bestimmen der Fensterhöhe
    window_height = rotated_frame.shape[0]

    # Berechnung der Ober- und Untergrenze (50% und 20%)
    lower_bound = int(0.50 * window_height)  # Untergrenze bei 50%
    middle_threshold = int(0.20 * window_height)  # Grenzwert zwischen Aktion 1 und 2
    upper_limit = int(0.20 * window_height)  # Obergrenze bei 20%

    # Grenzen einzeichnen
    cv2.line(rotated_frame, (0, lower_bound), (rotated_frame.shape[1], lower_bound), (255, 0, 0), 2)  # Untergrenze (50%)
    cv2.line(rotated_frame, (0, middle_threshold), (rotated_frame.shape[1], middle_threshold), (0, 0, 255), 2)  # Grenzwert (20%)

    # Prüfen, ob der Durchschnitt der Kantenpositionen unter oder oberhalb der Grenzen liegt
    if avg_edge_pos is not None:
        cv2.line(rotated_frame, (0, avg_edge_pos), (rotated_frame.shape[1], avg_edge_pos), (0, 255, 0), 2)

        # Berechnung der Mittelwert-Position auf Basis der Fensterhöhe
        mean_x = avg_edge_pos

        if action_status == "idle":
            handle_action_1(mean_x, lower_bound, middle_threshold)
        elif action_status == "waiting_for_action_1":
            wait_for_action_1(mean_x, middle_threshold)
        elif action_status == "action_2":
            perform_action_2()
        elif action_status == "waiting_for_action_2":
            wait_for_action_2(mean_x, upper_limit)
        elif action_status == "action_3":
            perform_action_3()
    else:
        if action_status == "idle":
            perform_action_1()

    # Bild anzeigen
    cv2.imshow('Original Rotated Webcam', rotated_frame)
    cv2.imshow('Filtered Horizontal Edges', np.zeros_like(edges))  # Optional, zur Darstellung der Kanten

    # Abbrechen, wenn die Taste 'q' gedrückt wird
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Webcam freigeben und Fenster schließen
cap.release()
cv2.destroyAllWindows()
