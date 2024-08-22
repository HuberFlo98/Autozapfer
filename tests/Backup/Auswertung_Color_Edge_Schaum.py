import cv2
import numpy as np
import os
import glob

# Verzeichnis mit Bildern definieren
input_dir = 'testimages/'
output_dir = 'output_images/'

# Verzeichnisse erstellen, falls sie nicht existieren
os.makedirs(output_dir, exist_ok=True)

# Feste HSV-Werte einstellen
hMin = 0
sMin = 47
vMin = 137
hMax = 179
sMax = 166
vMax = 254

# Mindestlänge für vertikale Kanten
min_length = 125

# Alle PNG-Dateien im Verzeichnis finden
image_files = glob.glob(os.path.join(input_dir, '*.png'))

for image_file in image_files:
    # Bild laden
    img = cv2.imread(image_file)

    # Punkte zum Zuschneiden definieren
    pts = np.array([[0, 630], [1280, 630], [1280, 850], [0, 850]])

    # Rechteck beschneiden
    rect = cv2.boundingRect(pts)
    x, y, w, h = rect
    image = img[y:y+h, x:x+w].copy()

    # Mindest- und Maximal-HSV-Werte festlegen
    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])

    # HSV-Bild erstellen und in einem Bereich filtern
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)

    # Canny-Kantenerkennung anwenden
    edges = cv2.Canny(output, 500, 500)

    # Kanten verdicken
    kernel = np.ones((5, 5), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)

    # Konturen basierend auf den Kanten finden
    contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Nur vertikale Konturen filtern
    vertical_contours = []
    for contour in contours:
        # Bounding Box der Kontur berechnen
        _, _, w, h = cv2.boundingRect(contour)
        
        # Prüfen, ob die Kontur überwiegend vertikal ist und die Mindestlänge erfüllt
        if h > w and h >= min_length:
            vertical_contours.append((contour, h))

    # Sortieren der vertikalen Konturen nach Länge (absteigend)
    vertical_contours = sorted(vertical_contours, key=lambda x: x[1], reverse=True)

    # Auswahl der zwei längsten Konturen
    two_longest_contours = [cnt[0] for cnt in vertical_contours[:2]]

    # Leeres Bild zum Zeichnen der zwei längsten vertikalen Konturen erstellen
    edges_colored = np.zeros_like(image)

    # Die zwei längsten vertikalen Konturen in einer spezifischen Farbe (z.B. Gelb) zeichnen
    cv2.drawContours(edges_colored, two_longest_contours, -1, (255, 255, 0), 2)

    # Kantenbild mit dem Originalbild überlagern
    overlay = cv2.addWeighted(image, 0.8, edges_colored, 0.2, 0)

    # Überlagertes Bild speichern
    output_file = os.path.join(output_dir, os.path.basename(image_file))
    cv2.imwrite(output_file, overlay)

    # Optional: Anzeige des Ergebnisses
    cv2.imshow('Zwei längste vertikale Kanten Overlay', overlay)
    cv2.imshow('Original', img)
    cv2.waitKey(0)

# Fenster schließen
cv2.destroyAllWindows()
