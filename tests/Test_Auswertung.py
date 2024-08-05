import cv2
import numpy as np


# Rotation
def rotate(img, angle, rotPoint=None):
    (height,width) = img.shape[:2]

    if rotPoint is None:
        rotPoint = (width//2,height//2)
    
    rotMat = cv2.getRotationMatrix2D(rotPoint, angle, 1.0)
    dimensions = (width,height)

    return cv2.warpAffine(img, rotMat, dimensions)


image = cv2.imread('testimages\img8020.png')


# Rotate +90°
image = rotate(image, +90)
    
    # Bildvorverarbeitung
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (11, 11), 0)
edges = cv2.Canny(blurred, 50, 150)

    # Horizontale Linien erkennen
lines = cv2.HoughLinesP(edges, rho=2, theta=np.pi/180, threshold=10, minLineLength=70, maxLineGap=20)
horizontal_lines = []
    
    # Filtern der horizontalen Linien
if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            if np.abs(angle) < 13 or np.abs(angle - 180) < 13:
                #horizontal_lines.append(line)
                if 68 < y1 < 400 and 68 < y2 < 400:
                    horizontal_lines.append(line)

    # Zeichnen der horizontalen Linien
for line in horizontal_lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
    # Mittelwert der y-Koordinaten der Linien berechnen (68 bis 200)
if len(horizontal_lines) > 0:
        
        y_coords_1 = [line[0][1] for line in horizontal_lines if 68 <= line[0][1] <= 130]
        try:
            
            #trim_percent = 0  # 10% der Daten werden abgeschnitten
            mean_y_1 = int(np.mean(y_coords_1))
            
            # Zeichnen des roten Strichs basierend auf dem Mittelwert der y-Koordinaten (68 bis 200)
            cv2.line(image, (0, mean_y_1), (image.shape[1], mean_y_1), (0, 0, 255), 3)
            
            # Mittelwert ausgeben (68 bis 200)
            
            print("Mittelwert der y-Koordinaten gerade:", mean_y_1)
            
            #Hier wird der maximale y-Wert für die Kante angegeben !Achtung! wenn dieser <80 wird, schäumt das Bier über
            #Bei Export brauchen wir ca. 90
            if mean_y_1 < 85: 
                    print("Stop tapping")
        except:
            mean_y_1 = 0

    # Mittelwert der y-Koordinaten der Linien berechnen (200 bis 500)
if len(horizontal_lines) > 0:
        y_coords_2 = [line[0][1] for line in horizontal_lines if 200 <= line[0][1] <= 400]
        try:
            trim_percent = 0.1  # 10% der Daten werden abgeschnitten
            mean_y_2 = int(compute_trimmed_mean(y_coords_2, trim_percent))
            # Zeichnen des blauen Strichs basierend auf dem Mittelwert der y-Koordinaten (200 bis 500)
            cv2.line(image, (0, mean_y_2), (image.shape[1], mean_y_2), (255, 0, 0), 3)
            # Mittelwert ausgeben (200 bis 500)
            #print("Mittelwert der y-Koordinaten (200 bis 500):", mean_y_2)
        except:
            mean_y_2 = 0

cv2.imshow("Kanten", edges)
cv2.imshow("Ergebnis", image)

cv2.waitKey(0)

