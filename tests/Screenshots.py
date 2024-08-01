import cv2
import random

KAMERA_NR = 1

vc = cv2.VideoCapture(1)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()

randomint = random.randint(0, 9999)
cv2.imwrite("./testimages/img" + str(randomint) + ".png",frame)