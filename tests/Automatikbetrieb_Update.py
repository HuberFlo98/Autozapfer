import cv2
import numpy as np
import threading
import time
#import keyboard

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
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Webcam konnte nicht geöffnet werden.")
    exit()

# Benutzerdefinierte Thread-Klasse
class Thread:
    def __init__(self):
        self.thread = None
        self.thread_started = False

    def run(self):
        pass

    def start(self, entry_function=None, user_param=None):
        if entry_function is None:
            entry_function = self.run

        self.thread = threading.Thread(target=entry_function, args=(user_param,))
        self.thread.start()
        self.thread_started = True
        return True

    def stop(self, wait=False):
        self.thread_started = False
        if wait and self.thread is not None:
            self.thread.join()

    @staticmethod
    def yield_ms(ms):
        time.sleep(ms / 1000.0)

# Globale Variable zur Verwaltung des Programmstatus
action_status = "waiting_for_start"

def show_preview(*args):
    """
    Zeigt ein Vorschaufenster an, das das Webcam-Bild mit den oberen und unteren Grenzwerten darstellt.
    Das Fenster schließt sich, wenn eine Taste gedrückt wird.
    """
    global action_status

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

        # Wenn eine Taste gedrückt wird, das Fenster schließen und den Status ändern
        if cv2.waitKey(1) != -1:
            action_status = "start_main_window"
            break

    cv2.destroyWindow('Preview')

def main_window(*args):
    """
    Zeigt das Hauptfenster an, nachdem eine Taste gedrückt wurde, und führt die Hauptlogik aus.
    """
    global action_status

    while True:
        if action_status == "start_main_window":
            ret, img = cap.read()
            if not ret:
                print("Kein Bild von der Webcam erhalten.")
                break

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
                cv2.line(img, (mean_x, 0), (mean_x, height), (255, 0, 0), 2)

            # Zeichnen der Grenzwerte als vertikale Linien
            cv2.line(img, (lower_bound, 0), (lower_bound, height), (0, 255, 255), 2)
            cv2.line(img, (upper_bound, 0), (upper_bound, height), (0, 255, 255), 2)

            # Hauptfenster anzeigen
            cv2.imshow('Main Window', img)

            if mean_x is None:
                print("Keine Kante erkannt")
                action_status = "waiting_for_action_1"
            elif mean_x < lower_bound:
                print("Kante unter Grenzwert 1")
                action_status = "waiting_for_action_1"
            elif lower_bound <= mean_x <= upper_bound:
                print("Kante zwischen Grenzwerten 1 und 2")
                action_status = "waiting_for_action_1"
            elif mean_x > upper_bound:
                print("Kante über Grenzwert 2")
                action_status = "complete"

            if cv2.waitKey(1) == ord('q'):
                action_status = "exit"
                break

        elif action_status == "complete":
            print("Aktionen abgeschlossen. Das Programm kann beendet werden.")
            break

        elif action_status == "exit":
            break

# Start des Vorschaufensters
preview_thread = Thread()
preview_thread.start(entry_function=show_preview)

# Warten, bis das Vorschaufenster beendet ist und das Hauptfenster gestartet wird
preview_thread.stop(wait=True)

# Start des Hauptfensters
main_thread = Thread()
main_thread.start(entry_function=main_window)

# Warten, bis das Hauptfenster beendet ist
main_thread.stop(wait=True)

# Ressourcen freigeben
cap.release()
cv2.destroyAllWindows()

