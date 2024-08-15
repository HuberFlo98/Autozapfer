import cv2

# Öffne die Webcam
cap = cv2.VideoCapture(0)
 #1

# Überprüfe, ob die Webcam geöffnet wurde
if not cap.isOpened():
    print("Fehler: Webcam konnte nicht geöffnet werden")
    exit()

# Setze den Fokuswert manuell (z.B. 100, kann je nach Kamera variieren)
focus_value = 0
cap.set(cv2.CAP_PROP_FOCUS, focus_value)

# Mache ein Bild
ret, frame = cap.read()
if not ret:
    print("Fehler: Bild konnte nicht aufgenommen werden")
    cap.release()
    exit()

# Zeige das aufgenommene Bild an
cv2.imshow('Aufgenommenes Bild', frame)

# Warte, bis eine Taste gedrückt wird, um das Fenster zu schließen
cv2.waitKey(0)

# Freigeben der Kamera und Schließen aller Fenster
cap.release()
cv2.destroyAllWindows()
