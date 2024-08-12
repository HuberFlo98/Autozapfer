import cv2
import numpy as np

# Load in image
image = cv2.imread('testimages/img9404.png')

pts = np.array([[0,200],[700,180],[1080,136],[1080,840],[0,780]])

## (1) Crop the bounding rect
rect = cv2.boundingRect(pts)
x,y,w,h = rect
croped = image[y:y+h, x:x+w].copy()


# Set fixed HSV values
hMin = 0
sMin = 0
vMin = 180
hMax = 179
sMax = 255
vMax = 255

# Set minimum and max HSV values to display
lower = np.array([hMin, sMin, vMin])
upper = np.array([hMax, sMax, vMax])

# Create HSV Image and threshold into a range
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower, upper)
output = cv2.bitwise_and(image, image, mask=mask)

# Apply Canny Edge Detection
edges = cv2.Canny(output, 100, 200)

# Dilate the edges to make them thicker
kernel = np.ones((5,5), np.uint8)  # 5x5 kernel for dilation
edges_dilated = cv2.dilate(edges, kernel, iterations=1)

# Create an empty image with the same dimensions as the original
edges_colored = np.zeros_like(image)

# Set the dilated edges to red (BGR format: Blue = 0, Green = 0, Red = 255)
edges_colored[edges_dilated != 0] = [255, 255, 0]

# Overlay red edges on the original image
overlay = cv2.addWeighted(image, 0.8, edges_colored, 0.2, 0)

# Display the overlay image
cv2.imshow('Thicker Red Edges Overlay', overlay)

# Wait indefinitely until a key is pressed
cv2.waitKey(0)
cv2.destroyAllWindows()
