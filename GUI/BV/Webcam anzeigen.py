#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 13:41:18 2023

@author: sammu
"""

import cv2
import numpy as np
# Erstelle eine Instanz der VideoCapture-Klasse
cap = cv2.VideoCapture(3)

# Schleife, um das Bild kontinuierlich anzuzeigen
while True:
    # Erfasse das aktuelle Bild von der Webcam
    ret, frame = cap.read()
    rotated_frame1 = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    pts = np.array([[75,0],[500,380],[500,0]], dtype=np.int32)
    mask = np.zeros_like(rotated_frame1)
    cv2.fillPoly(mask, [pts], (255,255,255))
    rotated_frame = cv2.bitwise_and(rotated_frame1, mask)
    # Zeige das Bild im Fenster an
    cv2.imshow('Webcam', rotated_frame)

    # Warte auf die Eingabe einer Taste
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Beende die Verbindung zur Webcam und schließe das Fenster
cap.release()
cv2.destroyAllWindows()
