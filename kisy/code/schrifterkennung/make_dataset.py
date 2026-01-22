import cv2
import numpy as np
import os

output_folder = "letters"
os.makedirs(output_folder, exist_ok=True)

# Anzahl der Bilder
num_images = 4

letter_id = 0  # globaler Zähler für alle Bilder

for img_idx in range(1, num_images + 1):
    image_path = f"./data/letters_{img_idx}.png"
    image = cv2.imread(image_path)

    if image is None:
        print(f"Bild {image_path} nicht gefunden, überspringe...")
        continue

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Horizontale Linien
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (80, 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
    horizontal_lines = cv2.dilate(horizontal_lines, cv2.getStructuringElement(cv2.MORPH_RECT, (20, 3)), iterations=2)

    # Vertikale Linien
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 80))
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
    vertical_lines = cv2.dilate(vertical_lines, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 20)), iterations=2)

    intersections = cv2.bitwise_and(horizontal_lines, vertical_lines)
    intersections = cv2.dilate(intersections, np.ones((5, 5), np.uint8), iterations=2)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(intersections, connectivity=8)
    intersection_points = [tuple(map(int, centroids[i])) for i in range(1, num_labels)]

    if not intersection_points:
        print(f"Keine Ecken in {image_path} gefunden, überspringe...")
        continue

    points = np.array(intersection_points)
    top_left = tuple(points[np.argmin(points[:, 0] + points[:, 1])])
    top_right = tuple(points[np.argmax(points[:, 0] - points[:, 1])])
    bottom_left = tuple(points[np.argmin(points[:, 0] - points[:, 1])])
    bottom_right = tuple(points[np.argmax(points[:, 0] + points[:, 1])])

    inner_cols = 8
    inner_rows = 13
    grid_width = top_right[0] - top_left[0]
    grid_height = bottom_left[1] - top_left[1]
    cell_width = grid_width / inner_cols
    cell_height = grid_height / inner_rows

    extra_left = 50
    extra_right = 20
    extra_top = 10
    extra_bottom = 10

    offset_tl = (int(top_left[0] - cell_width - extra_left), int(top_left[1] - cell_height - extra_top))
    offset_tr = (int(top_right[0] + cell_width + extra_right), int(top_right[1] - cell_height - extra_top))
    offset_bl = (int(bottom_left[0] - cell_width - extra_left), int(bottom_left[1] + cell_height + extra_bottom))
    offset_br = (int(bottom_right[0] + cell_width + extra_right), int(bottom_right[1] + cell_height + extra_bottom))

    output_cell_size = 64
    output_border_left = output_cell_size + int(extra_left * output_cell_size / cell_width)
    output_border_right = output_cell_size + int(extra_right * output_cell_size / cell_width)
    output_border_top = output_cell_size + int(extra_top * output_cell_size / cell_height)
    output_border_bottom = output_cell_size + int(extra_bottom * output_cell_size / cell_height)

    output_width = output_border_left + (inner_cols * output_cell_size) + output_border_right
    output_height = output_border_top + (inner_rows * output_cell_size) + output_border_bottom

    src_points = np.float32([offset_tl, offset_tr, offset_br, offset_bl])
    dst_points = np.float32([[0, 0], [output_width, 0], [output_width, output_height], [0, output_height]])

    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    warped = cv2.warpPerspective(gray, matrix, (output_width, output_height))

    cols = inner_cols + 2
    rows = inner_rows + 2
    padding = 3

    for row in range(rows):
        for col in range(cols):
            if col == 0:
                x1 = 0
                x2 = output_border_left
            elif col == cols - 1:
                x1 = output_border_left + (col - 1) * output_cell_size
                x2 = output_width
            else:
                x1 = output_border_left + (col - 1) * output_cell_size
                x2 = x1 + output_cell_size

            if row == 0:
                y1 = 0
                y2 = output_border_top
            elif row == rows - 1:
                y1 = output_border_top + (row - 1) * output_cell_size
                y2 = output_height
            else:
                y1 = output_border_top + (row - 1) * output_cell_size
                y2 = y1 + output_cell_size

            cell_img = warped[y1 + padding:y2 - padding, x1 + padding:x2 - padding]
            cv2.imwrite(os.path.join(output_folder, f"letter_{letter_id:03d}_r{row:02d}_c{col:02d}.png"), cell_img)
            letter_id += 1

    print(f"{image_path} verarbeitet. Aktueller Zähler: {letter_id}")

print(f"Fertig. Insgesamt {letter_id} Buchstaben extrahiert.")
