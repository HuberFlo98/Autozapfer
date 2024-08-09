import os
import cv2

def set_camera_focus(focus_value: int):
    # Überprüfen, ob das Fokus-Feature unterstützt wird
    # Fokus auf absolute Werte setzen (0 = Minimum, 255 = Maximum)
    os.system(f'v4l2-ctl -d /dev/video0 -c focus_absolute={focus_value}')
    print(f"Fokus wurde auf {focus_value} gesetzt.")

def capture_image():
    # OpenCV verwenden, um ein Bild von der Kamera aufzunehmen
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Kamera konnte nicht geöffnet werden.")
        return None
    
    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imshow("Captured Image", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return frame
    else:
        print("Fehler beim Aufnehmen des Bildes.")
        return None

def main():
    focus_values = [0, 50, 100, 150, 200, 255]  # Beispielwerte für den Fokus
    
    for focus in focus_values:
        set_camera_focus(focus)
        image = capture_image()
        if image is not None:
            print(f"Bild mit Fokus {focus} aufgenommen.")
        else:
            print(f"Fehler beim Aufnehmen des Bildes mit Fokus {focus}.")

if __name__ == "__main__":
    main()

    