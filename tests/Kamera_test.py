import cv2 as cv

src = cv.VideoCapture(0)
ret, frame = src.read()
grau = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)

gauss = cv.GaussianBlur(grau, (5,5),3)

kanten = cv.Canny(gauss, 0, 10)

cv.imshow(kanten)
cv.waitKey(0)