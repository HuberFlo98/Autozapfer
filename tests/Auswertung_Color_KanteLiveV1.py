import cv2
import numpy as np

# Feste HSV-Werte einstellen
hMin = 0
sMin = 0
vMin = 255
hMax = 179
sMax = 255
vMax = 255

# Mindestlänge für vertikale Kanten
min_length = 100

# Grenzwerte für den Mittelwert der X-Koordinaten
lower_bound = 200  # Beispielwert für die untere Grenze
upper_bound = 400  # Beispielwert für die obere Grenze

# Kamera-Feed initialisieren (0 für die erste verfügbare Kamera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Fehler beim Öffnen der Kamera")
    exit()

# Fenster nur einmal initialisieren
cv2.namedWindow('Längste vertikale Kanten Overlay')
cv2.namedWindow('Original')

while True:
    # Ein Frame von der Kamera lesen
    ret, img = cap.read()
    if not ret:
        print("Fehler beim Lesen des Frames oder Ende des Streams")
        break

    # Bilddimensionen abrufen
    img_height, img_width = img.shape[:2]

    # Punkte zum Zuschneiden definieren
    pts = np.array([[0, 0], [0, 1280], [960, 1280], [0, 960]])

    # Rechteck beschneiden
    rect = cv2.boundingRect(pts)
    x, y, w, h = rect

    # Überprüfen und Anpassen der Zuschneidekoordinaten
    if x < 0:
        w += x
        x = 0
    if y < 0:
        h += y
        y = 0
    if x + w > img_width:
        w = img_width - x
    if y + h > img_height:
        h = img_height - y

    if x >= 0 and y >= 0 and x+w <= img_width and y+h <= img_height:
        image = img[y:y+h, x:x+w].copy()
    else:
        continue

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
    two_longest_contours = [cnt[0] for cnt in vertical_contours[:1]]

    # Leeres Bild zum Zeichnen der zwei längsten vertikalen Konturen erstellen
    edges_colored = np.zeros_like(image)

    # Die zwei längsten vertikalen Konturen in Gelb zeichnen
    cv2.drawContours(edges_colored, two_longest_contours, -1, (255, 255, 0), 2)

    # Kantenbild mit dem Originalbild überlagern
    overlay = cv2.addWeighted(image, 0.8, edges_colored, 0.2, 0)

    # Mittelwert der X-Koordinaten der erkannten Konturen berechnen
    x_coords = []
    for contour in two_longest_contours:
        for point in contour:
            x_coords.append(point[0][0])

    # Statusvariable für die Position des Mittelwerts
    position_status = 0

    if x_coords:
        mean_x = int(np.mean(x_coords))

        # Eine vertikale Linie an der Position des Mittelwerts zeichnen
        cv2.line(overlay, (mean_x, 0), (mean_x, overlay.shape[0]), (0, 0, 255), 2)

        # Vergleich des Mittelwerts mit den Grenzwerten
        if mean_x < lower_bound:
            position_status = 1
            cv2.putText(overlay, "Unter Grenzwert 1", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        elif mean_x > upper_bound:
            position_status = 3
            cv2.putText(overlay, "Über Grenzwert 2", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            position_status = 2
            cv2.putText(overlay, "Zwischen Wert 1 und 2", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Grenzwerte als vertikale Linien einzeichnen
    cv2.line(overlay, (lower_bound, 0), (lower_bound, overlay.shape[0]), (0, 255, 255), 2)
    cv2.line(overlay, (upper_bound, 0), (upper_bound, overlay.shape[0]), (0, 255, 255), 2)

    # Ergebnisse im Fenster anzeigen (Fenster bleiben offen)
    cv2.imshow('Längste vertikale Kanten Overlay', overlay)
    cv2.imshow('Original', img)

    # Abbruch bei Tastendruck 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kamera-Feed freigeben und Fenster schließen
cap.release()
cv2.destroyAllWindows()
