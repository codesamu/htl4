import os
from pathlib import Path

import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import cv2


def ensure_dir(path: Path) -> None:
    """Create directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def crop_and_resize(img_gray: np.ndarray, x: int, y: int, w: int, h: int, size: int = 28) -> Image.Image:
    """
    Crop a bounding box from a grayscale image, make it roughly square with padding,
    and resize to (size x size) pixels.
    """
    # Crop the region of interest
    roi = img_gray[y : y + h, x : x + w]

    # Create a square canvas with padding
    max_side = max(w, h)
    canvas = np.full((max_side, max_side), 255, dtype=np.uint8)  # white background

    # Center the ROI on the canvas
    y_offset = (max_side - h) // 2
    x_offset = (max_side - w) // 2
    canvas[y_offset : y_offset + h, x_offset : x_offset + w] = roi

    # Resize to target size
    resized = cv2.resize(canvas, (size, size), interpolation=cv2.INTER_AREA)
    return Image.fromarray(resized)


def extract_letters_from_pdf(
    pdf_path: str,
    output_root: str = "dataset",
    page_labels: list[str] | None = None,
    min_box_size: int = 10,
) -> None:
    """
    Konvertiert eine PDF-Datei mit Buchstaben in einen Datensatz:
    - Alle Bilder werden auf 28x28 Pixel gebracht.
    - Für jeden Buchstaben wird ein Unterordner angelegt (z.B. 'A', 'B', ...).

    Annahme:
    - Jede Seite der PDF enthält Beispiele EINER einzigen Klasse (z.B. nur 'A', dann nur 'B', ...).
    - Die Zuordnung Seite -> Buchstabe erfolgt über `page_labels`, z.B.:
        page_labels = ["A", "B", "C", ...]

    Parameter:
    - pdf_path: Pfad zur PDF-Datei (z.B. 'letters.pdf').
    - output_root: Wurzelordner für den Datensatz.
    - page_labels: Liste der Labels (Buchstaben) pro Seite.
    - min_box_size: Minimale Breite/Höhe einer Bounding Box, um kleine Artefakte zu filtern.
    """
    pdf_path = str(pdf_path)
    # Immer relativ zum Speicherort dieses Skripts speichern,
    # egal von welchem Arbeitsverzeichnis das Skript gestartet wird.
    script_dir = Path(__file__).resolve().parent
    output_root_path = script_dir / output_root
    ensure_dir(output_root_path)

    # PDF in Seiten-Bilder umwandeln
    pages = convert_from_path(pdf_path, dpi=300)

    if page_labels is None:
        # Fallback: generische Labels, falls der Nutzer sie nicht angibt
        page_labels = [f"page_{i}" for i in range(len(pages))]

    if len(page_labels) != len(pages):
        raise ValueError(
            f"Anzahl der page_labels ({len(page_labels)}) stimmt nicht mit Anzahl der Seiten ({len(pages)}) überein."
        )

    for page_idx, page in enumerate(pages):
        label = page_labels[page_idx]
        label_dir = output_root_path / label
        ensure_dir(label_dir)

        # In Graustufen umwandeln
        gray = np.array(page.convert("L"))

        # Hintergrund weiß, Schrift dunkel: binarisieren und invertieren für Kontur-Erkennung
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Konturen (verbundene Komponenten) finden
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        img_count = 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # Kleine Artefakte rausfiltern
            if w < min_box_size or h < min_box_size:
                continue

            # Buchstabenbild ausschneiden und auf 28x28 skalieren
            letter_img = crop_and_resize(gray, x, y, w, h, size=28)

            # Dateiname, z.B. A_0001.png
            img_count += 1
            filename = f"{label}_{img_count:04d}.png"
            save_path = label_dir / filename
            letter_img.save(save_path)

        print(f"Seite {page_idx + 1}/{len(pages)} ('{label}'): {img_count} Bilder gespeichert in {label_dir}")


if __name__ == "__main__":
    """
    Beispiel-Aufruf:
    - Angenommen, die PDF hat 26 Seiten:
        Seite 1: A
        Seite 2: B
        ...
        Seite 26: Z

    Dann kannst du hier die Liste der Buchstaben anpassen.
    """
    # Hier die Labels anpassen je nach Aufbau deiner 'letters.pdf'
    # Beispiel für A-Z:
    page_labels_example = [chr(ord("A") + i) for i in range(26)]

    extract_letters_from_pdf(
        pdf_path="letters_removed.pdf",
        output_root="dataset",
        page_labels=page_labels_example,
        min_box_size=10,
    )


