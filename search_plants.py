#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from pathlib import Path

CSV_PATH = Path(__file__).with_name("Pflanzenliste_Maturaarbeit_DBV2.0_cvs.csv")
MONTH_FIELDS = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
MONTH_NAMES = {name.lower(): name for name in MONTH_FIELDS}
MONTH_NAMES.update({str(i + 1): MONTH_FIELDS[i] for i in range(12)})


def detect_csv_settings(path: Path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        sample = handle.read(4096)
        if sample.count(";") >= sample.count(","):
            return {"delimiter": ";"}
        return {"delimiter": ","}


def load_rows(path: Path):
    settings = detect_csv_settings(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, **settings)
        for row in reader:
            yield row


def build_matcher(query: str, regex: bool, ignore_case: bool):
    if regex:
        flags = re.IGNORECASE if ignore_case else 0
        pattern = re.compile(query, flags)

        def matcher(text: str) -> bool:
            return bool(pattern.search(text))
    else:
        if ignore_case:
            query_lower = query.lower()

            def matcher(text: str) -> bool:
                return query_lower in text.lower()
        else:
            def matcher(text: str) -> bool:
                return query in text

    return matcher


def row_matches(row, matcher, fields=None):
    if fields is None:
        values = row.values()
    else:
        values = (row.get(field, "") for field in fields)

    for value in values:
        if value is None:
            continue
        if matcher(str(value)):
            return True
    return False


def month_matches(row, months, month_value):
    for month in months:
        value = str(row.get(month, "")).strip()
        if value != month_value:
            return False
    return True


def normalize_month(value: str):
    token = value.strip().lower()
    if token in MONTH_NAMES:
        return MONTH_NAMES[token]
    raise argparse.ArgumentTypeError(f"Ungültiger Monat: {value}. Gültig sind {', '.join(MONTH_FIELDS)} oder 1-12.")


def format_row(row, fieldnames):
    return ";".join(str(row.get(field, "")).strip() for field in fieldnames)


def main():
    parser = argparse.ArgumentParser(
        description="Suche in einzelnen Spalten und Monaten der Pflanzenliste."
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Suchbegriff, der in den gewählten Spalten gefunden werden soll.",
    )
    parser.add_argument(
        "--path",
        default=str(CSV_PATH),
        help="CSV-Datei, die durchsucht werden soll. Standard: Pflanzenliste_Maturaarbeit_DBV2.0_cvs.csv",
    )
    parser.add_argument(
        "--field",
        action="append",
        dest="fields",
        help="Spaltenname, in der gesucht werden soll. Mehrfach möglich. Wenn nicht angegeben, werden alle Spalten durchsucht.",
    )
    parser.add_argument(
        "--month",
        action="append",
        dest="months",
        type=normalize_month,
        help="Monat, der zutreffen muss. Mehrfach möglich. Werte: Jan, Feb, ..., Dez oder 1-12.",
    )
    parser.add_argument(
        "--month-value",
        choices=["0", "1"],
        default="1",
        help="Monatswert, nach dem gefiltert werden soll. Standard: 1.",
    )
    parser.add_argument(
        "--regex",
        action="store_true",
        help="Interpretieren Sie die Suche als regulären Ausdruck.",
    )
    parser.add_argument(
        "--no-ignore-case",
        action="store_true",
        help="Deaktiviere die Groß-/Kleinschreibung bei der Suche.",
    )
    parser.add_argument(
        "--columns",
        action="store_true",
        help="Zeige die Spaltenüberschriften und beende das Programm.",
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Gib nur die Anzahl der Treffer aus statt der kompletten Zeilen.",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Datei nicht gefunden: {path}", file=sys.stderr)
        sys.exit(1)

    rows = list(load_rows(path))
    if not rows:
        print(f"Keine Daten in {path}", file=sys.stderr)
        sys.exit(1)

    fieldnames = list(rows[0].keys())

    if args.columns:
        print("Spalten:")
        for name in fieldnames:
            print(f"- {name}")
        return

    if not args.query and not args.months:
        parser.print_help(sys.stdout)
        return

    selected_fields = None
    if args.fields:
        missing = [field for field in args.fields if field not in fieldnames]
        if missing:
            print(f"Unbekannte Spaltennamen: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
        selected_fields = args.fields

    matcher = build_matcher(args.query or "", args.regex, not args.no_ignore_case)
    matches = []
    for row in rows:
        if args.query:
            if not row_matches(row, matcher, selected_fields):
                continue
        if args.months and not month_matches(row, args.months, args.month_value):
            continue
        matches.append(row)

    if args.count:
        print(len(matches))
        return

    if not matches:
        print("Keine Treffer gefunden.")
        return

    print(format_row(dict(zip(fieldnames, fieldnames)), fieldnames))
    for row in matches:
        print(format_row(row, fieldnames))


if __name__ == "__main__":
    main()
