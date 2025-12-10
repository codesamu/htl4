import cv2
import numpy as np

# === Parameter ===
REF_WIDTH_MM = 85.6  # reale Breite des Referenzobjekts (z.B. Kreditkarte) in mm
BLUR_KERNEL = (5, 5)
CANNY_THRESH1 = 50
CANNY_THRESH2 = 150
MIN_CONTOUR_AREA = 1000  # minimale Konturfläche, um Rauschen zu filtern

pixels_per_mm = None  # wird nach Kalibrierung gesetzt


def preprocess(frame):
    # Graustufen
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Rauschen reduzieren
    blurred = cv2.GaussianBlur(gray, BLUR_KERNEL, 0)

    # Kontrast optional anpassen (hier einfache Normalisierung)
    norm = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX)

    # Kanten (Canny)
    edges = cv2.Canny(norm, CANNY_THRESH1, CANNY_THRESH2)

    # Kleine Lücken schließen
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    return edges


def find_largest_contour(binary_img, min_area=MIN_CONTOUR_AREA):
    contours, _ = cv2.findContours(
        binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return None
    # nach Fläche filtern
    big = [c for c in contours if cv2.contourArea(c) > min_area]
    if not big:
        return None
    return max(big, key=cv2.contourArea)


def measure_object(frame, contour, ppm):
    # Minimales umschreibendes Rechteck
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    # Seitenlängen in Pixel
    (x, y), (w_px, h_px), angle = rect

    # In mm umrechnen
    w_mm = w_px / ppm
    h_mm = h_px / ppm

    # Visualisierung
    cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)
    label = f"{w_mm:.1f}mm x {h_mm:.1f}mm"
    cv2.putText(frame, label, (int(x) - 80, int(y)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return w_mm, h_mm


def calibrate_ppm(frame, edges):
    """
    Kalibriert pixels_per_mm über die größte Kontur
    (z.B. deine Referenzkarte im Bild).
    Lege die Referenz gut sichtbar in die Szene und drücke 'c'.
    """
    global pixels_per_mm

    cnt = find_largest_contour(edges)
    if cnt is None:
        print("Kalibrierung fehlgeschlagen: keine große Kontur gefunden.")
        return None

    # Rechteck um Referenz
    rect = cv2.minAreaRect(cnt)
    (x, y), (w_px, h_px), angle = rect

    # Längere Seite als Breite annehmen (hängt von Ausrichtung ab)
    ref_px = max(w_px, h_px)
    if ref_px <= 0:
        print("Kalibrierung fehlgeschlagen: ungültige Referenzbreite.")
        return None

    ppm = ref_px / REF_WIDTH_MM
    pixels_per_mm = ppm

    # Visualisierung
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(frame, [box], 0, (255, 0, 0), 2)
    cv2.putText(frame, f"Calibrated: {ppm:.2f} px/mm",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 0, 0), 2)
    print(f"Kalibriert: {ppm:.3f} Pixel pro mm")
    return ppm


def main():
    global pixels_per_mm

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kamera konnte nicht geöffnet werden.")
        return

    print("Tasten:")
    print("  c - Kalibrieren mit Referenzobjekt")
    print("  s - aktuellen Frame + Messung speichern")
    print("  q - Beenden")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kein Frame von der Kamera.")
            break

        # Kopie für Ausgabe
        display = frame.copy()

        # Preprocessing
        edges = preprocess(frame)

        # Wenn kalibriert: Objekt messen (nimm z.B. größte Kontur als Messobjekt)
        if pixels_per_mm is not None:
            cnt = find_largest_contour(edges)
            if cnt is not None:
                measure_object(display, cnt, pixels_per_mm)
                cv2.putText(display, f"{pixels_per_mm:.2f} px/mm",
                            (20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 255), 2)

        # Fenster anzeigen
        cv2.imshow("Frame", display)
        cv2.imshow("Edges", edges)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('c'):
            # Kalibrieren
            calibrate_ppm(display, edges)
        elif key == ord('s'):
            # Speichern des aktuellen Frames
            cv2.imwrite("measurement_frame.png", display)
            print("Frame gespeichert als measurement_frame.png")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
