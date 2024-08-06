import cv2 as cv
import numpy as np

# Rotation function
def rotate(img, angle, rotPoint=None):
    (height, width) = img.shape[:2]

    if rotPoint is None:
        rotPoint = (width // 2, height // 2)
    
    rotMat = cv.getRotationMatrix2D(rotPoint, angle, 1.0)
    dimensions = (width, height)

    return cv.warpAffine(img, rotMat, dimensions)

# Extend a line to the borders of the image
def extend_line(x1, y1, x2, y2, img_shape):
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

# Calculate angle of a line
def calculate_angle(line):
    x1, y1, x2, y2 = line
    return np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi

# Calculate perpendicular distance from a point to a line
def point_to_line_distance(x0, y0, x1, y1, x2, y2):
    """
    Calculate the perpendicular distance from a point (x0, y0) to a line defined by (x1, y1) -> (x2, y2).
    """
    # Using the line equation Ax + By + C = 0, find the perpendicular distance.
    A = y2 - y1
    B = x1 - x2
    C = x2 * y1 - x1 * y2
    
    # Distance from point to line
    distance = abs(A * x0 + B * y0 + C) / np.sqrt(A**2 + B**2)
    return distance

# Find a line parallel and separate from a given line
def find_parallel_and_separate_line(lines, reference_line, angle_threshold=5, min_distance=10):
    x1_ref, y1_ref, x2_ref, y2_ref = reference_line
    reference_angle = calculate_angle(reference_line)

    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = calculate_angle((x1, y1, x2, y2))
        
        # Check if the line is parallel within the angle threshold and separate by min_distance
        if abs(reference_angle - angle) < angle_threshold:
            # Calculate midpoint of the line to measure distance
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            distance = point_to_line_distance(mid_x, mid_y, x1_ref, y1_ref, x2_ref, y2_ref)
            if distance >= min_distance:
                return line[0]
    return None

# Read in an image
img = cv.imread('testimages/img9653.png')
cv.imshow('Original Image', img)

# Convert to grayscale
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Blur 
blur = cv.GaussianBlur(gray, (7, 7), cv.BORDER_DEFAULT)

# Cropped image
cropped_image = blur[400:800, 0:1150]  # Slicing to crop the image

# Initialize LSD (Line Segment Detector)
lsd = cv.createLineSegmentDetector(0)

# Detect lines in the image
lines = lsd.detect(cropped_image)[0]  # Get the detected lines from the first position of the tuple

# Check if lines are detected
if lines is not None:
    # Calculate the length of each line
    line_lengths = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        line_lengths.append((length, line))

    # Sort lines by length in descending order
    line_lengths.sort(reverse=True, key=lambda x: x[0])

    # Select the longest line
    longest_line = line_lengths[0][1][0]

    # Find a parallel and separate line
    parallel_line = find_parallel_and_separate_line(lines, longest_line, angle_threshold=5, min_distance=2)

    # Create a copy of the image to draw on
    drawn_img = cv.cvtColor(cropped_image, cv.COLOR_GRAY2BGR)

    if parallel_line is not None:
        # Extend and draw the longest line and the parallel line
        x1, y1, x2, y2 = longest_line
        x1_ext, y1_ext, x2_ext, y2_ext = extend_line(x1, y1, x2, y2, cropped_image.shape)
        cv.line(drawn_img, (x1_ext, y1_ext), (x2_ext, y2_ext), (0, 255, 0), 2)

        px1, py1, px2, py2 = parallel_line
        px1_ext, py1_ext, px2_ext, py2_ext = extend_line(px1, py1, px2, py2, cropped_image.shape)
        cv.line(drawn_img, (px1_ext, py1_ext), (px2_ext, py2_ext), (255, 0, 0), 2)

    # Display the result
    cv.imshow("Longest and Parallel Line Extended", drawn_img)
    cv.waitKey(0)
    cv.destroyAllWindows()

else:
    print("No lines detected.")

cv.waitKey(0)
