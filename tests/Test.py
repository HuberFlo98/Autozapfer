import cv2
import numpy as np

# Load in image
image = cv2.imread('testimages/img672.png')

# Set fixed HSV values
hMin = 0
sMin = 0
vMin = 255
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

# Convert edges to 3 channels to overlay on the original image
edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

# Overlay edges on the original image
overlay = cv2.addWeighted(image, 0.8, edges_colored, 0.2, 0)

# Display the overlay image
cv2.imshow('Output', output)
cv2.imshow('Edges Overlay', overlay)

# Wait indefinitely until a key is pressed
cv2.waitKey(0)
cv2.destroyAllWindows()
