import cv2
import numpy as np

# Load the image
input_image = cv2.imread('testimages/img5187.png')

# Convert to grayscale
gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGRA2GRAY)

# Apply blur
img_blur = cv2.GaussianBlur(gray_image, (7, 7), 0)

# Apply Canny edge detection
img_canny = cv2.Canny(img_blur, 10, 100)

# Invert the Canny image
img_canny = cv2.bitwise_not(img_canny)


# Show the output images
cv2.imshow('Original', input_image)
cv2.imshow('Canny Edges', img_canny)


cv2.waitKey(0)
cv2.destroyAllWindows()
