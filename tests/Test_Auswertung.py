import cv2
import numpy as np

# Load the image
input_image = cv2.imread('testimages/img9041.png')

# Define the points for cropping
pts = np.array([[0, 220], [1150, 220], [1150, 770], [0, 770]])

# Crop the bounding rectangle
rect = cv2.boundingRect(pts)
x, y, w, h = rect
cropped = input_image[y:y+h, x:x+w].copy()

# Convert to grayscale
gray_image = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur
img_blur = cv2.GaussianBlur(gray_image, (7, 7), 0)

# Apply Canny edge detection
img_canny = cv2.Canny(img_blur, 1, 35)

# Invert the Canny image
img_canny = cv2.bitwise_not(img_canny)






# Find contours
contours, hierarchy = cv2.findContours(cv2.bitwise_not(img_canny), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Calculate contour lengths and store them with contours
contour_lengths = [(cv2.arcLength(contour, True), contour) for contour in contours]

# Sort contours by length in descending order
contour_lengths.sort(key=lambda x: x[0], reverse=True)

# Take the two longest contours
two_longest_contours = contour_lengths[:2]

# Draw the two longest contours on the image
for length, contour in two_longest_contours:
    # Draw the contour on the cropped image
    cv2.drawContours(cropped, [contour], -1, (0, 0, 255), 2)

    # Print coordinates of each point in the longest contours
    for point in contour:
        coord = point[0]  # Extracting the (x, y) coordinate
        print(f"Coordinate: {coord}")

    # Display the length of each edge
    print(f"Edge length: {length}")






# Display the results
cv2.imshow('Cropped Image with Longest Contours', cropped)
cv2.imshow('Canny Image', img_canny)
cv2.waitKey(0)
cv2.destroyAllWindows()
