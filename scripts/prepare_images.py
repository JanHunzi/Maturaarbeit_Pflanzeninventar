#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_FILE = ROOT / 'Pflanzenliste_Maturaarbeit_DBV2.0_cvs.csv'
INPUT_DIR = ROOT / 'images'
OUTPUT_DIR = ROOT / 'images'
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


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


def copy_images(ids):
    if not INPUT_DIR.exists():
        raise SystemExit(f'Ordner nicht gefunden: {INPUT_DIR}')

    files = sorted([p for p in INPUT_DIR.iterdir() if p.is_file()])
    image_files = [p for p in files if p.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not image_files:
        raise SystemExit(f'Keine unterstützten Bilddateien gefunden in {INPUT_DIR}')

    for index, image_file in enumerate(image_files[:len(ids)], start=1):
        plant_id = ids[index - 1]
        stem = Path(image_file.name)
        ext = stem.suffix.lower()
        target_name = f'PF-{int(plant_id):03d}{ext}'
        target = OUTPUT_DIR / target_name
        if image_file.name != target_name:
            if target.exists():
                print(f'Vorhanden: {target.name}')
            else:
                shutil.copy2(image_file, target)
                print(f'Kopiert: {image_file.name} -> {target.name}')
        else:
            print(f'Bereit: {image_file.name}')


if __name__ == '__main__':
    ensure_output_dir()
    ids = read_ids()
    print(f'{len(ids)} Pflanzen-IDs gefunden.')
    copy_images(ids)
    print('Fertig. Bilder liegen jetzt im Ordner images/.')
