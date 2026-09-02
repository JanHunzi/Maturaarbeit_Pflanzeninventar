#!/usr/bin/env python3
"""Baut images/image_index.json aus dem tatsächlichen Inhalt des images/-Ordners.

Hintergrund / Problem:
Die Weboberfläche (index.html) lädt `images/image_index.json`, um pro
Pflanzen-ID (Spalte `ID` in der CSV) die passenden Bilddateien zu finden.
Diese Datei wurde bisher manuell gepflegt und geriet dadurch schnell aus dem
Takt mit dem tatsächlichen Inhalt von `images/` - neu hinzugefügte Bilder
wurden dadurch nie angezeigt, obwohl die Dateien vorhanden waren.

Dieses Skript baut die Datei stattdessen direkt aus dem Ordnerinhalt und ist
so robust gegenüber üblichen Schreibweise-Unterschieden in Dateinamen:

- Gross-/Kleinschreibung wird ignoriert ("PF", "pf", "Pf" ...).
- Trennzeichen zwischen "PF" und der Nummer dürfen "-", "_", " " oder auch
  fehlen sein (z.B. "PF-003", "PF_003", "PF 003", "PF003").
- Führende Nullen in der Nummer werden ignoriert ("PF-003" == "PF-3").
- Unterstriche/Bindestriche/Leerzeichen sowie Umlaute/Akzente im restlichen
  Dateinamen spielen für die Zuordnung keine Rolle, nur die führende Nummer
  zählt.
- Unterstützte Endungen: .jpg, .jpeg, .png, .webp (Gross-/Kleinschreibung
  wird ignoriert).

Dateien, die nicht dem Muster "PF<Trennzeichen><Nummer>..." entsprechen (z.B.
die Referenzbilder "Z.1_web.webp", "ZZ_web.webp" ...), gehören zu keiner
Pflanzen-ID und werden übersprungen statt einen Fehler zu verursachen.

Aufruf:
    python3 scripts/build_image_index.py
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / 'images'
INDEX_FILE = IMAGES_DIR / 'image_index.json'
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

# Erkennt "PF" gefolgt von optionalem Trennzeichen und der Pflanzen-Nummer,
# unabhängig von Gross-/Kleinschreibung und führenden Nullen.
ID_PATTERN = re.compile(r'^pf[-_\s]?0*(\d+)', re.IGNORECASE)


def normalize_filename(name):
    """Normalisiert einen Dateinamen für den robusten Vergleich.

    Wandelt Umlaute/Akzente in ihre Basisbuchstaben um, vereinheitlicht
    Leerzeichen/Unterstriche/Bindestriche und macht alles klein.
    """
    decomposed = unicodedata.normalize('NFKD', name)
    ascii_only = decomposed.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[-_\s]+', '-', ascii_only).lower()


def extract_plant_id(filename):
    """Liefert die numerische Pflanzen-ID aus einem Dateinamen oder None."""
    match = ID_PATTERN.match(normalize_filename(filename))
    if not match:
        return None
    return str(int(match.group(1)))


def build_index():
    if not IMAGES_DIR.exists():
        raise SystemExit(f'Ordner nicht gefunden: {IMAGES_DIR}')

    index = {}
    for path in sorted(IMAGES_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        plant_id = extract_plant_id(path.name)
        if plant_id is None:
            continue
        index.setdefault(plant_id, []).append(path.name)

    for filenames in index.values():
        filenames.sort()

    return dict(sorted(index.items(), key=lambda item: int(item[0])))


if __name__ == '__main__':
    image_index = build_index()
    INDEX_FILE.write_text(
        json.dumps(image_index, ensure_ascii=False, indent=2, sort_keys=False) + '\n',
        encoding='utf-8',
    )
    print(f'{len(image_index)} Pflanzen-IDs mit Bildern in {INDEX_FILE.relative_to(ROOT)} gespeichert.')
