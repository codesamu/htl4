import cv2
import numpy as np

# === iPhone 16 Breite in mm ===
IPHONE16_WIDTH_MM = 71.6  # Breite (kurze Seite) des iPhone 16 [web:56][web:61]

MIN_CONTOUR_AREA = 1500


def preprocess_for_contours(image):
    """
    Liefert ein binäres Bild, in dem iPhone + Objekt möglichst als
    gefüllte Flächen erscheinen.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # etwas stärker glätten
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    # adaptives Thresholding (invertiert), robust bei wechselnder Beleuchtung
    binary = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        21, 5
    )

    # kräftiges Closing, um Löcher und Lücken zu schließen
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=3)

    return binary


def get_sorted_contours(binary_img, min_area=MIN_CONTOUR_AREA):
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    big = [c for c in contours if cv2.contourArea(c) > min_area]
    if not big:
        return []
    # Von links nach rechts sortieren
    return sorted(big, key=lambda c: cv2.boundingRect(c)[0])


def rect_from_contour(contour, use_fallback=True):
    """
    Gibt Zentrum, Breite/Höhe (Pixel), Winkel und Box zurück.
    Fällt bei sehr „kaputten“ Konturen auf boundingRect zurück.[web:74][web:82]
    """
    rect = cv2.minAreaRect(contour)  # ((cx, cy), (w, h), angle)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    (cx, cy), (w_px, h_px), angle = rect

    if use_fallback:
        x, y, bw, bh = cv2.boundingRect(contour)
        aspect_rect = max(w_px, h_px) / (min(w_px, h_px) + 1e-6)
        aspect_bbox = max(bw, bh) / (min(bw, bh) + 1e-6)

        # Wenn minAreaRect extrem gestreckt ist, boundingRect bevorzugen
        if aspect_rect > 8 and aspect_bbox < aspect_rect:
            cx = x + bw / 2.0
            cy = y + bh / 2.0
            w_px = bw
            h_px = bh
            box = np.array(
                [[x, y],
                 [x + bw, y],
                 [x + bw, y + bh],
                 [x, y + bh]],
                dtype=np.int32
            )

    return (cx, cy), (w_px, h_px), angle, box


def draw_measurement(img, center, size_mm, box, color, label):
    (cx, cy) = center
    (w_mm, h_mm) = size_mm
    cv2.drawContours(img, [box], 0, color, 2)
    text = f"{label}: {w_mm:.1f}mm x {h_mm:.1f}mm"
    cv2.putText(img, text, (int(cx) - 120, int(cy)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def capture_single_frame(camera_source=1, out_name="capture.png"):
    """
    Zeigt Live-Vorschau, SPACE = Foto aufnehmen, q = abbrechen.[web:37][web:42]
    """
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        print("Kamera konnte nicht geöffnet werden.")
        return None

    print("Live-Vorschau: SPACE = Foto, q = Abbrechen")

    frame = None
    while True:
        ret, img = cap.read()
        if not ret:
            print("Kein Frame von der Kamera.")
            break

        cv2.imshow("Live", img)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            frame = img.copy()
            cv2.imwrite(out_name, frame)
            print(f"Foto gespeichert als {out_name}")
            break
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return frame


def process_image_with_iphone_ref(image):
    """
    Erwartung: iPhone 16 links, zu messendes Objekt rechts nebendran.
    Misst iPhone als Referenz und dann das nächste Objekt rechts.[web:7][web:19]
    """
    binary = preprocess_for_contours(image)
    contours = get_sorted_contours(binary)

    print(f"Gefundene große Konturen: {len(contours)}")

    if len(contours) < 1:
        print("Keine ausreichenden Konturen gefunden.")
        cv2.imshow("Binary", binary)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # Linke Kontur = iPhone
    iphone_contour = contours[0]
    center_i, (w_px_i, h_px_i), angle_i, box_i = rect_from_contour(iphone_contour)

    # kleine Seite als Breite des iPhones
    ref_px = min(w_px_i, h_px_i)
    if ref_px <= 0:
        print("Ungültige Referenzbreite.")
        return

    pixels_per_mm = ref_px / IPHONE16_WIDTH_MM
    print(f"Kalibriert mit iPhone 16: {pixels_per_mm:.3f} px/mm")

    # iPhone-Höhe in mm
    iphone_height_mm = max(w_px_i, h_px_i) / pixels_per_mm
    draw_measurement(
        image,
        center_i,
        (IPHONE16_WIDTH_MM, iphone_height_mm),
        box_i,
        (255, 0, 0),
        "iPhone"
    )

    # Nächstes Objekt rechts vom iPhone suchen
    iphone_x, _, _, _ = cv2.boundingRect(iphone_contour)
    candidate = None
    min_dx = float("inf")
    for cnt in contours:
        if cnt is iphone_contour:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        dx = x - iphone_x
        if dx > 0 and dx < min_dx:
            min_dx = dx
            candidate = cnt

    if candidate is None:
        print("Kein weiteres Objekt rechts vom iPhone gefunden.")
        cv2.imshow("Binary", binary)
        cv2.imshow("Result", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    center_o, (w_px_o, h_px_o), angle_o, box_o = rect_from_contour(candidate)
    w_mm_o = w_px_o / pixels_per_mm
    h_mm_o = h_px_o / pixels_per_mm

    draw_measurement(
        image,
        center_o,
        (w_mm_o, h_mm_o),
        box_o,
        (0, 255, 0),
        "Objekt"
    )

    print(f"Objektgroesse ~ {w_mm_o:.1f}mm x {h_mm_o:.1f}mm")

    cv2.imshow("Binary", binary)
    cv2.imshow("Result", image)
    cv2.imwrite("result_measurement.png", image)
    print("Ergebnisbild gespeichert als result_measurement.png")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    frame = capture_single_frame(camera_source=1, out_name="capture.png")
    if frame is None:
        return

    process_image_with_iphone_ref(frame)


if __name__ == "__main__":
    main()
