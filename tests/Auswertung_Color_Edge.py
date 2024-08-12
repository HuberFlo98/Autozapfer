import cv2
import numpy as np

# Load in image
img = cv2.imread('testimages/img7926.png')

pts = np.array([[0, 630], [1280, 630], [1280, 770], [0, 770]])

## (1) Crop the bounding rect
rect = cv2.boundingRect(pts)
x, y, w, h = rect
image = img[y:y+h, x:x+w].copy()

# Set fixed HSV values
hMin = 0
sMin = 40
vMin = 153
hMax = 179
sMax = 114
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
kernel = np.ones((5,5), np.uint8)
edges_dilated = cv2.dilate(edges, kernel, iterations=1)

# Find contours based on the edges
contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Sort contours by length and keep only the two longest
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

# Create an empty image to draw the two longest contours
edges_colored = np.zeros_like(image)

# Draw the two longest contours in red
cv2.drawContours(edges_colored, contours, -1, (255, 255, 0), 2)

# Overlay the edges on the original cropped image
overlay = cv2.addWeighted(image, 0.8, edges_colored, 0.2, 0)

# Display the overlay image and the original image
cv2.imshow('Two Longest Edges Overlay', overlay)
cv2.imshow('Original', img)
cv2.imwrite('Edge.jpg', overlay)

# Wait indefinitely until a key is pressed
cv2.waitKey(0)
cv2.destroyAllWindows()
