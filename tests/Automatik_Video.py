import cv2
import numpy as np

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
                # Filtern nach horizontalen Linien mit einem Toleranzbereich von ±angle_threshold Grad
                if abs(angle) <= angle_threshold:
                    horizontal_lines.append((x1, y1, x2, y2))
    return horizontal_lines

# Pfad zum Video
video_path = 'testimages/bier.mp4'  # Pfad zum Video anpassen
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Fehler: Video konnte nicht geöffnet werden")
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

while True:
    # Bild (Frame) aus dem Video lesen
    ret, frame = cap.read()

    if not ret:
        break  # Beenden, wenn keine Frames mehr verfügbar sind

    # Bild um 90 Grad gegen den Uhrzeigersinn drehen
    rotated_frame = frame

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
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=40, minLineLength=20, maxLineGap=30)

    # Nur fast waagerechte Linien filtern (±10 Grad)
    horizontal_lines = filter_horizontal_lines(lines, angle_threshold=50)

    # Neues leeres Bild für gefilterte Kanten (nur horizontale Linien)
    filtered_edges = np.zeros_like(edges)

    # Zeichne gefilterte horizontale Linien
    for x1, y1, x2, y2 in horizontal_lines:
        cv2.line(filtered_edges, (x1, y1), (x2, y2), 255, 2)

    # Durchschnitt der Kantenpositionen berechnen (y-Achse)
    avg_edge_pos = calculate_weighted_average_edge_position(horizontal_lines)

    # Bestimmen der Fensterhöhe
    window_height = rotated_frame.shape[0]

    # Berechnung der Ober- und Untergrenze (80% und 50%)
    upper_limit = int(0.20 * window_height)  # Obergrenze bei 80%
    lower_limit = int(0.50 * window_height)  # Untergrenze bei 50%

    # Grenzen einzeichnen
    cv2.line(rotated_frame, (0, lower_limit), (rotated_frame.shape[1], lower_limit), (255, 0, 0), 2)  # Untergrenze (50%)
    cv2.line(rotated_frame, (0, upper_limit), (rotated_frame.shape[1], upper_limit), (0, 0, 255), 2)  # Obergrenze (80%)

    # Prüfen, ob der Durchschnitt der Kantenpositionen unter oder oberhalb der Grenzen liegt
    if avg_edge_pos is not None:
        # Mittelwert-Linie einzeichnen
        cv2.line(rotated_frame, (0, avg_edge_pos), (rotated_frame.shape[1], avg_edge_pos), (0, 255, 0), 2)

        # Überprüfung der Position
        if avg_edge_pos > lower_limit:
            print("unter Untergreze")
        elif avg_edge_pos > upper_limit:
            print("Zwischen Ober und Untergrenze")
        else:
            print("ueber Obergrenze")

    # Bilder anzeigen
    cv2.imshow('Original Rotated Frame', rotated_frame)
    cv2.imshow('Filtered Horizontal Edges', filtered_edges)

    # Warten auf 30ms und Beenden, wenn 'q' gedrückt wird
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# VideoCapture freigeben und Fenster schließen
cap.release()
cv2.destroyAllWindows()
