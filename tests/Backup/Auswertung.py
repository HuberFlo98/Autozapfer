import cv2 as cv
import numpy as np


# Rotation
def rotate(img, angle, rotPoint=None):
    (height,width) = img.shape[:2]

    if rotPoint is None:
        rotPoint = (width//2,height//2)
    
    rotMat = cv.getRotationMatrix2D(rotPoint, angle, 1.0)
    dimensions = (width,height)

    return cv.warpAffine(img, rotMat, dimensions)

# Read in an image
img = cv.imread('testimages\img9913.png')
cv.imshow('Park', img)

# #Rotate +90°
# rotated = rotate(img, +90)
# cv.imshow('Rotated', rotated)

# Converting to grayscale
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#cv.imshow('Gray', gray)

# Blur 
blur = cv.GaussianBlur(gray, (3,3), cv.BORDER_DEFAULT)

#cropped
#                     Höhe     Länge
cropped_image = blur[200:800 ,0:1100] # Slicing to crop the image
#cv.imshow('cropped_image', cropped_image)

def extend_line(x1, y1, x2, y2, img_shape):
    """
    Extend a line to the borders of the image.
    
    Parameters:
    x1, y1: Coordinates of the start point.
    x2, y2: Coordinates of the end point.
    img_shape: Shape of the image (height, width).
    
    Returns:
    (x1_ext, y1_ext, x2_ext, y2_ext): The extended line coordinates.
    """
    height, width = img_shape[:2]

    # Calculate line equation parameters: y = mx + c
    if x2 - x1 != 0:
        m = (y2 - y1) / (x2 - x1)
        c = y1 - m * x1
    else:
        m = None  # Vertical line

    # Find intersections with image borders
    if m is not None:
        # Line intersects with left and right borders (x = 0 and x = width)
        y_at_x0 = c
        y_at_xmax = m * width + c
        
        # Line intersects with top and bottom borders (y = 0 and y = height)
        x_at_y0 = -c / m
        x_at_ymax = (height - c) / m
        
        # Extend line based on intersection points
        points = [
            (0, int(round(y_at_x0))),  # Intersect with left border
            (width, int(round(y_at_xmax))),  # Intersect with right border
            (int(round(x_at_y0)), 0),  # Intersect with top border
            (int(round(x_at_ymax)), height)  # Intersect with bottom border
        ]

        # Filter points to be within image dimensions
        valid_points = [(x, y) for x, y in points if 0 <= x <= width and 0 <= y <= height]
        
        # Return the two points that are furthest apart (extended line)
        if len(valid_points) == 2:
            return valid_points[0] + valid_points[1]
        else:
            # Calculate distances between each pair and select the longest segment
            max_distance = 0
            best_pair = (0, 0, 0, 0)
            for i in range(len(valid_points)):
                for j in range(i + 1, len(valid_points)):
                    x1_ext, y1_ext = valid_points[i]
                    x2_ext, y2_ext = valid_points[j]
                    distance = np.sqrt((x2_ext - x1_ext) ** 2 + (y2_ext - y1_ext) ** 2)
                    if distance > max_distance:
                        max_distance = distance
                        best_pair = (x1_ext, y1_ext, x2_ext, y2_ext)
            return best_pair

    else:
        # Vertical line
        return (x1, 0, x2, height)



# Initialize LSD (Line Segment Detector)
lsd = cv.createLineSegmentDetector(0)

# Detect lines in the image
lines = lsd.detect(cropped_image)[0]  # Get the detected lines from the first position of the tuple

# Check if lines are detected
if lines is not None:
    # Calculate the length of each line
    line_lengths = []
    for i, line in enumerate(lines):
        x1, y1, x2, y2 = line[0]
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        line_lengths.append((length, line))

    # Sort lines by length in descending order
    line_lengths.sort(reverse=True, key=lambda x: x[0])

    # Select the two longest lines
    two_longest_lines = [line for _, line in line_lengths[:2]]

    # Create a copy of the image to draw on
    drawn_img = cropped_image.copy()

    # Extend and draw only the two longest lines on the image
    for line in two_longest_lines:
        x1, y1, x2, y2 = line[0]
        x1_ext, y1_ext, x2_ext, y2_ext = extend_line(x1, y1, x2, y2, cropped_image.shape)
        
        # Draw the extended line on the image
        cv.line(drawn_img, (x1_ext, y1_ext), (x2_ext, y2_ext), (0, 255, 0), 2)

    # Display the result
    cv.imshow("Two Longest Lines Extended", drawn_img)
    cv.waitKey(0)
    cv.destroyAllWindows()

else:
    print("No lines detected.")

cv.waitKey(0)


