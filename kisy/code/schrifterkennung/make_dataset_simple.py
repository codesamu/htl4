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


def process_page(page_path: Path, output_root: Path, counts: dict) -> None:
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
    print(f"Verarbeite {page_path.name}: Größe {height} x {width}")

    letter_width = width // NUMBER_COLS
    letter_height = height // NUMBER_ROWS

    # Label aus Dateiname, z.B. 'A.png' -> 'A'
    label = page_path.stem[0].upper()

    for i in range(NUMBER_ROWS):
        for j in range(NUMBER_COLS):
            x = j * letter_width
            y = i * letter_height

            # Zuschneiden mit Rand
            letter_img = gray[
                y + MARGIN : y + letter_height - MARGIN,
                x + MARGIN : x + letter_width - MARGIN,
            ]

            # Falls aus irgendeinem Grund zu klein, überspringen
            if letter_img.size == 0:
                continue

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

    for page_path in page_files:
        process_page(page_path, output_root, counts)

    print("Fertig! Gespeicherte Bilder pro Buchstabe:")
    for label in sorted(counts.keys()):
        print(label, ":", counts[label])


if __name__ == "__main__":
    main()


