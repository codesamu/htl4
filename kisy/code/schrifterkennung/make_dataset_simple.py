import os
from pathlib import Path

import cv2
import numpy as np


# ==========================
# Parameter anpassen
# ==========================

# Ordner, in dem die Seiten als PNGs liegen (z.B. A.png, B.png, ...)
PAGES_FOLDER = "letters"

# Wie viele Reihen und Spalten hat dein Raster?
NUMBER_ROWS = 13
NUMBER_COLS = 8

# Rand, der bei jedem Buchstaben weggeschnitten wird
MARGIN = 15

# Zielgröße für die Buchstabenbilder
TARGET_SIZE = 28

# Zielordner für den Datensatz
OUTPUT_ROOT = "dataset_simple"


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def _find_line_positions(projection: np.ndarray, min_rel_height: float = 0.5) -> list[int]:
    """
    Finde Positionen starker Linien (Rasterlinien) in einer Projektionskurve.
    Gibt die Mittelpunkte zusammenhängender Segmente zurück, deren Wert
    über einem Schwellwert liegt.
    """
    if projection.size == 0:
        return []

    max_val = float(projection.max())
    if max_val <= 0:
        return []

    threshold = max_val * min_rel_height

    positions: list[int] = []
    in_segment = False
    start = 0

    for idx, val in enumerate(projection):
        if val >= threshold and not in_segment:
            in_segment = True
            start = idx
        elif val < threshold and in_segment:
            in_segment = False
            end = idx - 1
            center = (start + end) // 2
            positions.append(center)

    if in_segment:
        end = len(projection) - 1
        center = (start + end) // 2
        positions.append(center)

    return positions


def process_page(page_path: Path, output_root: Path, counts: dict, page_index: int) -> None:
    """
    Schneidet eine einzelne Seite (PNG) in das Raster und
    speichert alle Kacheln in den Ordner des Buchstabens.

    Der Buchstabe wird aus dem Dateinamen genommen, z.B. 'A.png' -> 'A'.
    """
    image = cv2.imread(str(page_path))
    if image is None:
        print(f"Konnte Bild nicht laden: {page_path}")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    height, width, _ = image.shape
    print(f"Verarbeite {page_path.name}: Größe {height} x {width}, Seite-Index {page_index}")

    # Bild binarisieren und invertieren (Rasterlinien/Buchstaben dunkel)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Projektionen berechnen
    vertical_proj = np.sum(thresh, axis=0)   # über Zeilen summieren -> vertikale Linien
    horizontal_proj = np.sum(thresh, axis=1)  # über Spalten summieren -> horizontale Linien

    x_lines = _find_line_positions(vertical_proj, min_rel_height=0.5)
    y_lines = _find_line_positions(horizontal_proj, min_rel_height=0.5)

    # Wir erwarten NUMBER_COLS+1 vertikale und NUMBER_ROWS+1 horizontale Linien
    if len(x_lines) != NUMBER_COLS + 1 or len(y_lines) != NUMBER_ROWS + 1:
        print(
            f"Warnung: erwartete {NUMBER_COLS+1} vertikale / {NUMBER_ROWS+1} horizontale Linien, "
            f"gefunden wurden {len(x_lines)} / {len(y_lines)}. Fallback auf gleichmäßiges Raster."
        )
        # Gleichmäßiges Raster als Fallback
        x_lines = [int(j * width / NUMBER_COLS) for j in range(NUMBER_COLS + 1)]
        y_lines = [int(i * height / NUMBER_ROWS) for i in range(NUMBER_ROWS + 1)]

    for i in range(NUMBER_ROWS):
        # Welcher Buchstabe gehört zu dieser Zeile?
        # Annahme: auf JEDER Seite steht in Zeile 0 der Buchstabe A,
        # in Zeile 1 der Buchstabe B, ..., also jede Seite enthält das
        # komplette Alphabet mit gleicher Anordnung.
        # -> Der Buchstabe hängt NUR von der Zeile ab, nicht von der Seite.
        if i >= 26:
            # Nur A–Z (26 Buchstaben)
            break
        label = chr(ord("A") + i)

        for j in range(NUMBER_COLS):
            x1 = x_lines[j]
            x2 = x_lines[j + 1]
            y1 = y_lines[i]
            y2 = y_lines[i + 1]

            # Etwas Innenrand, damit die gezeichneten Linien abgeschnitten werden
            inner_margin = max(1, MARGIN // 3)
            x1_crop = x1 + inner_margin
            x2_crop = x2 - inner_margin
            y1_crop = y1 + inner_margin
            y2_crop = y2 - inner_margin

            # Safety: Koordinaten innerhalb des Bildes halten
            x1_crop = max(0, min(x1_crop, width - 1))
            x2_crop = max(0, min(x2_crop, width))
            y1_crop = max(0, min(y1_crop, height - 1))
            y2_crop = max(0, min(y2_crop, height))

            # Zuschneiden
            letter_img = gray[y1_crop:y2_crop, x1_crop:x2_crop]

            # Falls aus irgendeinem Grund zu klein, überspringen
            if letter_img.size == 0 or letter_img.shape[0] < 5 or letter_img.shape[1] < 5:
                continue  # zu klein oder leer

            # Auf 28x28 skalieren
            letter_img_resized = cv2.resize(
                letter_img, (TARGET_SIZE, TARGET_SIZE), interpolation=cv2.INTER_AREA
            )

            # Ordner für Buchstaben
            label_dir = output_root / label
            ensure_dir(str(label_dir))

            # Laufende Nummer für diesen Buchstaben
            counts.setdefault(label, 0)
            counts[label] += 1

            filename = f"{label}_{counts[label]:04d}.png"
            save_path = label_dir / filename

            cv2.imwrite(str(save_path), letter_img_resized)


def main() -> None:
    # Immer relativ zum Speicherort dieses Skripts arbeiten,
    # egal von welchem Arbeitsverzeichnis aus es gestartet wird.
    script_dir = Path(__file__).resolve().parent

    pages_dir = script_dir / PAGES_FOLDER
    output_root = script_dir / OUTPUT_ROOT
    ensure_dir(str(output_root))

    # Alle PNG-Seiten im Ordner 'letters'
    page_files = sorted(
        [p for p in pages_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}]
    )

    if not page_files:
        raise FileNotFoundError(f"Keine Seitenbilder in Ordner: {PAGES_FOLDER}")

    counts: dict[str, int] = {}

    for page_index, page_path in enumerate(page_files):
        process_page(page_path, output_root, counts, page_index)

    print("Fertig! Gespeicherte Bilder pro Buchstabe:")
    for label in sorted(counts.keys()):
        print(label, ":", counts[label])


if __name__ == "__main__":
    main()


