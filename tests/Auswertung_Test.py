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

# Function to merge collinear vertical lines
def merge_collinear_lines(lines, angle_threshold=15, distance_threshold=10):
    """
    Merge lines that are approximately vertical and collinear.
    """
    merged_lines = []
    used_lines = [False] * len(lines)

    for i, line in enumerate(lines):
        if used_lines[i]:
            continue

        x1, y1, x2, y2 = line[0]
        current_angle = calculate_angle((x1, y1, x2, y2))

        # Check if the line is approximately vertical
        if (90 - angle_threshold < abs(current_angle) < 90 + angle_threshold) or \
           (270 - angle_threshold < abs(current_angle) < 270 + angle_threshold):

            # Initialize merged line as current line
            x1_min, x2_max = min(x1, x2), max(x1, x2)
            y1_min, y2_max = min(y1, y2), max(y1, y2)

            for j, other_line in enumerate(lines):
                if used_lines[j] or i == j:
                    continue

                ox1, oy1, ox2, oy2 = other_line[0]
                other_angle = calculate_angle((ox1, oy1, ox2, oy2))

                # Check if other line is approximately vertical and collinear
                if abs(current_angle - other_angle) < angle_threshold:
                    # Check proximity of line endpoints
                    if (point_to_line_distance(ox1, oy1, x1, y1, x2, y2) < distance_threshold and
                        point_to_line_distance(ox2, oy2, x1, y1, x2, y2) < distance_threshold):

                        # Update merged line endpoints
                        x1_min = min(x1_min, ox1, ox2)
                        x2_max = max(x2_max, ox1, ox2)
                        y1_min = min(y1_min, oy1, oy2)
                        y2_max = max(y2_max, oy1, oy2)
                        used_lines[j] = True

            # Add the merged line
            merged_lines.append([(x1_min, y1_min, x2_max, y2_max)])
            used_lines[i] = True

    return merged_lines

def detect_lines_in_region(image, x_min, x_max, vertical_threshold):
    """
    Detect and merge vertical lines within a specified x-coordinate range in the image.
    """
    # Crop the image to the specified region
    cropped_region = image[:, x_min:x_max]

    # Initialize LSD (Line Segment Detector)
    lsd = cv.createLineSegmentDetector(0)

    # Detect lines in the cropped region
    lines = lsd.detect(cropped_region)[0]  # Get the detected lines from the first position of the tuple

    # Adjust line coordinates back to original image coordinates
    if lines is not None:
        lines = [np.array([line[0] + [x_min, 0, x_min, 0]]) for line in lines]

    # Filter and merge vertical lines
    vertical_lines = [line for line in lines if 
                      (90 - vertical_threshold < abs(calculate_angle(line[0])) < 90 + vertical_threshold) or
                      (270 - vertical_threshold < abs(calculate_angle(line[0])) < 270 + vertical_threshold)]

    # Merge collinear lines
    merged_lines = merge_collinear_lines(vertical_lines, angle_threshold=vertical_threshold, distance_threshold=10)

    return merged_lines

# Read image
img = cv.imread('testimages/img9006.png')
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

# Create a copy of the image to draw on
drawn_img = cv.cvtColor(dst2, cv.COLOR_GRAY2BGR)

# Define the angle range to include only vertical lines (e.g., within ±15 degrees of 90 or 270)
vertical_threshold = 15

# Check if lines are detected in the initial region (0 to 1200 x-coordinates)
x_min, x_max = 0, 1200
merged_lines = detect_lines_in_region(dst2, x_min, x_max, vertical_threshold)

# If no lines found in the initial region, check the entire image
if not merged_lines:
    merged_lines = detect_lines_in_region(dst2, 0, dst2.shape[1], vertical_threshold)

# Draw merged lines
for line in merged_lines:
    x1, y1, x2, y2 = line[0]
    cv.line(drawn_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

# Display the result
cv.imshow("Merged Vertical Lines", drawn_img)
cv.waitKey(0)
cv.destroyAllWindows()
