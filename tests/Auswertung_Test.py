import cv2 as cv
import numpy as np

# Funktion zum Erweitern einer Linie bis zu den Rändern des Bildes
def extend_line(x1, y1, x2, y2, img_shape):
    height, width = img_shape[:2]

    # Berechnung der Liniengleichung: y = mx + c
    if x2 - x1 != 0:
        m = (y2 - y1) / (x2 - x1)
        c = y1 - m * x1
    else:
        m = None  # Vertikale Linie

    # Finde die Schnittpunkte mit den Bildrändern
    if m is not None:
        # Schnittpunkte mit den linken und rechten Rändern (x = 0 und x = width)
        y_at_x0 = c
        y_at_xmax = m * width + c

        # Schnittpunkte mit den oberen und unteren Rändern (y = 0 und y = height)
        x_at_y0 = -c / m
        x_at_ymax = (height - c) / m

        # Erweitere die Linie basierend auf den Schnittpunkten
        points = [
            (0, int(round(y_at_x0))),  # Schnittpunkt mit dem linken Rand
            (width, int(round(y_at_xmax))),  # Schnittpunkt mit dem rechten Rand
            (int(round(x_at_y0)), 0),  # Schnittpunkt mit dem oberen Rand
            (int(round(x_at_ymax)), height)  # Schnittpunkt mit dem unteren Rand
        ]

        # Filtere Punkte, um nur die innerhalb der Bilddimensionen zu behalten
        valid_points = [(x, y) for x, y in points if 0 <= x <= width and 0 <= y <= height]

        # Gib die beiden Punkte zurück, die am weitesten voneinander entfernt sind (erweiterte Linie)
        if len(valid_points) == 2:
            return valid_points[0] + valid_points[1]
        else:
            # Berechne die Entfernungen zwischen jedem Paar und wähle das längste Segment aus
            max_distance = 0
            best_pair = (0, 0, 0, 0)
            for i in range(len(valid_points)):
                for j in range(i + 1, len(valid_points)):
                    x1_ext, y1_ext = valid_points[i]
                    x2_ext, y2_ext = valid_points[j]
                    distance = np.sqrt((x2_ext - x1_ext) ** 2 + (y2_ext - y1_ext) ** 2)
                    if distance > max_distance:
                        max_distance = distance
                        best_pair = (x1_ext, y1_ext, x2_ext, y2_ext)
            return best_pair

    else:
        # Vertikale Linie
        return (x1, 0, x2, height)

# Berechne den Winkel einer Linie in Grad
def calculate_angle(line):
    x1, y1, x2, y2 = line
    return np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi

# Berechne den senkrechten Abstand von einem Punkt zu einer Linie
def point_to_line_distance(x0, y0, x1, y1, x2, y2):
    """
    Berechne den senkrechten Abstand von einem Punkt (x0, y0) zu einer Linie definiert durch (x1, y1) -> (x2, y2).
    """
    A = y2 - y1
    B = x1 - x2
    C = x2 * y1 - x1 * y2

    distance = abs(A * x0 + B * y0 + C) / np.sqrt(A**2 + B**2)
    return distance

# Funktion zum Zusammenführen kollinearer vertikaler Linien
def merge_collinear_lines(lines, angle_threshold=15, distance_threshold=10):
    """
    Füge Linien zusammen, die ungefähr vertikal und kollinear sind.
    """
    merged_lines = []
    used_lines = [False] * len(lines)

    for i, line in enumerate(lines):
        if used_lines[i]:
            continue

        x1, y1, x2, y2 = line[0]
        current_angle = calculate_angle((x1, y1, x2, y2))

        # Überprüfe, ob die Linie ungefähr vertikal ist
        if (90 - angle_threshold < abs(current_angle) < 90 + angle_threshold) or \
           (270 - angle_threshold < abs(current_angle) < 270 + angle_threshold):

            # Initialisiere die zusammengeführte Linie als aktuelle Linie
            x1_min, x2_max = min(x1, x2), max(x1, x2)
            y1_min, y2_max = min(y1, y2), max(y1, y2)

            for j, other_line in enumerate(lines):
                if used_lines[j] or i == j:
                    continue

                ox1, oy1, ox2, oy2 = other_line[0]
                other_angle = calculate_angle((ox1, oy1, ox2, oy2))

                # Überprüfe, ob die andere Linie ungefähr vertikal und kollinear ist
                if abs(current_angle - other_angle) < angle_threshold:
                    # Überprüfe die Nähe der Linienendpunkte
                    if (point_to_line_distance(ox1, oy1, x1, y1, x2, y2) < distance_threshold and
                        point_to_line_distance(ox2, oy2, x1, y1, x2, y2) < distance_threshold):

                        # Aktualisiere die Endpunkte der zusammengeführten Linie
                        x1_min = min(x1_min, ox1, ox2)
                        x2_max = max(x2_max, ox1, ox2)
                        y1_min = min(y1_min, oy1, oy2)
                        y2_max = max(y2_max, oy1, oy2)
                        used_lines[j] = True

            # Füge die zusammengeführte Linie hinzu
            merged_lines.append([(x1_min, y1_min, x2_max, y2_max)])
            used_lines[i] = True

    return merged_lines

def detect_lines_in_region(image, x_min, x_max, vertical_threshold):
    """
    Erkenne und vereine vertikale Linien in einem angegebenen x-Koordinatenbereich im Bild.
    """
    # Schneide das Bild auf den angegebenen Bereich zu
    cropped_region = image[:, x_min:x_max]

    # Initialisiere LSD (Line Segment Detector)
    lsd = cv.createLineSegmentDetector(0)

    # Erkenne Linien im zugeschnittenen Bereich
    lines = lsd.detect(cropped_region)[0]  # Die erkannten Linien aus der ersten Position des Tupels holen

    # Korrigiere die Linienkoordinaten zurück zu den ursprünglichen Bildkoordinaten
    if lines is not None:
        lines = [np.array([line[0] + [x_min, 0, x_min, 0]]) for line in lines]

    # Filtere und vereine vertikale Linien
    vertical_lines = [line for line in lines if 
                      (90 - vertical_threshold < abs(calculate_angle(line[0])) < 90 + vertical_threshold) or
                      (270 - vertical_threshold < abs(calculate_angle(line[0])) < 270 + vertical_threshold)]

    # Füge kollineare Linien zusammen
    merged_lines = merge_collinear_lines(vertical_lines, angle_threshold=vertical_threshold, distance_threshold=10)

    return merged_lines

# Lese das Bild ein
img = cv.imread('testimages/img5455.png')
pts = np.array([[0, 200], [700, 180], [1150, 136], [1150, 840], [0, 780]])

# In Graustufen konvertieren
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Weichzeichnen
blur = cv.GaussianBlur(gray, (3, 3), cv.BORDER_DEFAULT)

## (1) Zuschneiden des Begrenzungsrechtecks
rect = cv.boundingRect(pts)
x, y, w, h = rect
croped = blur[y:y+h, x:x+w].copy()

## (2) Erstelle Maske
pts = pts - pts.min(axis=0)

mask = np.zeros(croped.shape[:2], np.uint8)
cv.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv.LINE_AA)

## (3) Bitwise-Operation
dst = cv.bitwise_and(croped, croped, mask=mask)

## (4) Füge den weißen Hintergrund hinzu
bg = np.ones_like(croped, np.uint8) * 255
cv.bitwise_not(bg, bg, mask=mask)
dst2 = bg + dst

# Erstelle eine Kopie des Bildes zum Zeichnen
drawn_img = cv.cvtColor(dst2, cv.COLOR_GRAY2BGR)

# Definiere den Bereich für vertikale Linien (z.B. ±15 Grad um 90 oder 270)
vertical_threshold = 15

# Überprüfe, ob Linien im ursprünglichen Bereich (0 bis 1200 x-Koordinaten) erkannt wurden
x_min, x_max = 0, 1200
merged_lines = detect_lines_in_region(dst2, x_min, x_max, vertical_threshold)

# Wenn keine Linien im ursprünglichen Bereich gefunden wurden, überprüfe das gesamte Bild
if not merged_lines:
    merged_lines = detect_lines_in_region(dst2, 0, dst2.shape[1], vertical_threshold)

# Berechne die Längen der Linien
line_lengths = [(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), (x1, y1, x2, y2)) for (x1, y1, x2, y2) in [line[0] for line in merged_lines]]

# Sortiere die Linien nach Länge und wähle die zwei längsten aus
sorted_lines = sorted(line_lengths, key=lambda item: item[0], reverse=True)
longest_lines = sorted_lines[:2]

# Zeichne nur die zwei längsten Linien
for _, (x1, y1, x2, y2) in longest_lines:
    cv.line(drawn_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

# Zeige das Ergebnis an
cv.imshow("Longest Vertical Lines", drawn_img)
cv.waitKey(0)
cv.destroyAllWindows()
