#!/usr/bin/env python3
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_FILE = ROOT / 'Pflanzenliste_Maturaarbeit_DBV2.0_cvs.csv'
INPUT_DIR = ROOT / 'Images'
OUTPUT_DIR = ROOT / 'Images'
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP'}


def read_ids():
    with CSV_FILE.open('r', encoding='utf-8-sig') as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        return []
    header = lines[0].split(';')
    id_index = header.index('ID') if 'ID' in header else None
    if id_index is None:
        raise SystemExit('Spalte ID wurde in der CSV nicht gefunden.')
    ids = []
    for line in lines[1:]:
        parts = line.split(';')
        if parts[id_index].strip():
            ids.append(parts[id_index].strip())
    return ids


def ensure_output_dir():
    OUTPUT_DIR.mkdir(exist_ok=True)


def extract_id_from_filename(path):
    match = re.search(r'(?i)pf[-_]?0*(\d+)', path.name)
    if not match:
        return None
    return int(match.group(1))


def sync_images(ids):
    if not INPUT_DIR.exists():
        raise SystemExit(f'Ordner nicht gefunden: {INPUT_DIR}')

    files = sorted([p for p in INPUT_DIR.iterdir() if p.is_file()])
    image_files = [p for p in files if p.suffix.lower() in {ext.lower() for ext in SUPPORTED_EXTENSIONS}]
    if not image_files:
        raise SystemExit(f'Keine unterstützten Bilddateien gefunden in {INPUT_DIR}')

    for plant_id in ids:
        numeric_id = int(plant_id)
        matches = [image_file for image_file in image_files if extract_id_from_filename(image_file) == numeric_id]
        if not matches:
            print(f'Kein Bild gefunden für ID {numeric_id}')
            continue

        source = matches[0]
        target_name = f'PF-{numeric_id:03d}{source.suffix}'
        target = OUTPUT_DIR / target_name
        if target.exists() and target.resolve() == source.resolve():
            print(f'Bereit: {target.name}')
        elif target.exists():
            print(f'Vorhanden: {target.name}')
        else:
            shutil.copy2(source, target)
            print(f'Kopiert: {source.name} -> {target.name}')


if __name__ == '__main__':
    ensure_output_dir()
    ids = read_ids()
    print(f'{len(ids)} Pflanzen-IDs gefunden.')
    sync_images(ids)
    print('Fertig. Bilder liegen jetzt im Ordner Images/.')
