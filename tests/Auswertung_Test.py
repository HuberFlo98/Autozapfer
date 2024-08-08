import cv2 as cv
import numpy as np

# Function to extend a line to the borders of the image
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

# Calculate the angle of a line in degrees
def calculate_angle(line):
    x1, y1, x2, y2 = line
    return np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi

# Calculate the perpendicular distance from a point to a line
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

# Find the nearest parallel line to the longest line with a minimum distance
def find_nearest_parallel_line(lines, reference_line, angle_threshold=5, min_distance=10):
    x1_ref, y1_ref, x2_ref, y2_ref = reference_line
    reference_angle = calculate_angle(reference_line)

    min_distance_found = float('inf')
    nearest_parallel_line = None
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = calculate_angle((x1, y1, x2, y2))

        # Check if the line is parallel within the angle threshold
        if abs(reference_angle - angle) < angle_threshold:
            # Calculate midpoint of the line to measure distance
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            distance = point_to_line_distance(mid_x, mid_y, x1_ref, y1_ref, x2_ref, y2_ref)
            if min_distance < distance < min_distance_found:  # Ensure it meets minimum distance
                min_distance_found = distance
                nearest_parallel_line = line[0]
    return nearest_parallel_line








# Read image
img = cv.imread('testimages/img8020.png')
pts = np.array([[0, 200], [700, 180], [1080, 136], [1080, 840], [0, 780]])








# Convert to grayscale
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Blur 
blur = cv.GaussianBlur(gray, (3, 3), cv.BORDER_DEFAULT)

## (1) Crop the bounding rect
rect = cv.boundingRect(pts)
x, y, w, h = rect
croped = blur[y:y+h, x:x+w].copy()

## (2) make mask
pts = pts - pts.min(axis=0)

mask = np.zeros(croped.shape[:2], np.uint8)
cv.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv.LINE_AA)

## (3) do bit-op
dst = cv.bitwise_and(croped, croped, mask=mask)

## (4) add the white background
bg = np.ones_like(croped, np.uint8) * 255
cv.bitwise_not(bg, bg, mask=mask)
dst2 = bg + dst

# Initialize LSD (Line Segment Detector)
lsd = cv.createLineSegmentDetector(0)

# Detect lines in the image
lines = lsd.detect(dst2)[0]  # Get the detected lines from the first position of the tuple

# Create a copy of the image to draw on
drawn_img = cv.cvtColor(dst2, cv.COLOR_GRAY2BGR)

# Define the angle range to include only vertical lines (e.g., within ±15 degrees of 90 or 270)
vertical_threshold = 15

# Check if lines are detected
if lines is not None:
    # Calculate the length of each line
    line_lengths = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        angle = calculate_angle((x1, y1, x2, y2))

        # Include only vertical lines
        if (90 - vertical_threshold < abs(angle) < 90 + vertical_threshold) or \
           (270 - vertical_threshold < abs(angle) < 270 + vertical_threshold):
            line_lengths.append((length, line))

            # Draw all detected vertical lines
            cv.line(drawn_img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 1)

    # Sort lines by length in descending order
    line_lengths.sort(reverse=True, key=lambda x: x[0])

    if line_lengths:
        # Select the longest line
        longest_line = line_lengths[0][1][0]

        # Find the nearest parallel line
        nearest_parallel_line = find_nearest_parallel_line(lines, longest_line, angle_threshold=10, min_distance=5)

        # Draw the longest line in red
        x1, y1, x2, y2 = longest_line
        x1_ext, y1_ext, x2_ext, y2_ext = extend_line(x1, y1, x2, y2, dst2.shape)
        cv.line(drawn_img, (x1_ext, y1_ext), (x2_ext, y2_ext), (0, 0, 255), 2)

        # Draw the nearest parallel line in green if it meets the minimum distance requirement
        if nearest_parallel_line is not None:
            nx1, ny1, nx2, ny2 = nearest_parallel_line
            nx1_ext, ny1_ext, nx2_ext, ny2_ext = extend_line(nx1, ny1, nx2, ny2, dst2.shape)
            cv.line(drawn_img, (nx1_ext, ny1_ext), (nx2_ext, ny2_ext), (0, 255, 0), 1)

    # Display the result
    cv.imshow("Vertical Lines", drawn_img)
    cv.waitKey(0)
    cv.destroyAllWindows()
else:
    print("No lines detected.")
