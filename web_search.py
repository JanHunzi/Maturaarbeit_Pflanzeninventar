#!/usr/bin/env python3
import csv
import html
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

CSV_PATH = Path(__file__).with_name("Pflanzenliste_Maturaarbeit_DBV2.0_cvs.csv")
FILTER_FIELDS = ["Name Deutsch", "Name Latein", "Pflanzenfamilie", "Wuchsform", "Blütenfarbe", "Gepflanzt"]
MONTH_FIELDS = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


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
        return list(reader)


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


def row_matches(row, matcher):
    for value in row.values():
        if value is None:
            continue
        if matcher(str(value)):
            return True
    return False


def unique_values(rows, field):
    values = sorted({str(row.get(field, "")).strip() for row in rows if str(row.get(field, "")).strip()})
    return values


def build_select(name, label, options, selected):
    items = [f'<option value="all">Alle</option>']
    for value in options:
        escaped_value = html.escape(value)
        selected_attr = " selected" if value == selected else ""
        items.append(f'<option value="{escaped_value}"{selected_attr}>{escaped_value}</option>')
    return f'<label for="{html.escape(name)}">{html.escape(label)}:</label><select id="{html.escape(name)}" name="{html.escape(name)}">' + "".join(items) + "</select>"


def build_page(query, regex, ignore_case, selected_filters, selected_months, results, fieldnames, dropdowns):
    query_html = html.escape(query or "")
    regex_checked = "checked" if regex else ""
    case_sensitive_checked = "checked" if not ignore_case else ""

    filter_html = []
    for field in FILTER_FIELDS:
        selected_value = selected_filters.get(field, "all")
        values = dropdowns.get(field, [])
        filter_html.append(build_select(field, field, values, selected_value))

    selected_months_set = set(selected_months or [])
    month_items = [f'<option value="all"{" selected" if "all" in selected_months_set else ""}>Alle Monate</option>']
    for month in MONTH_FIELDS:
        selected_attr = " selected" if month in selected_months_set else ""
        month_items.append(f'<option value="{html.escape(month)}"{selected_attr}>{html.escape(month)}</option>')
    month_select = '<label for="month">Monat(e):</label><select id="month" name="month" multiple size="4">' + "".join(month_items) + "</select>"

    result_count = len(results) if results is not None else 0
    result_info = f"<p>{result_count} Zeile(n) gefunden.</p>" if results is not None else ""
    results_html = render_rows(results, fieldnames) if results is not None else ""

    return f"""
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Pflanzenliste Suche</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 1rem; line-height: 1.5; }}
    input[type=text], select {{ width: 100%; padding: 0.5rem; margin-bottom: 0.5rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.4rem; text-align: left; }}
    th {{ background: #efefef; }}
    .filters {{ display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
    .filter-block {{ display: flex; flex-direction: column; }}
    .controls {{ display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; margin-bottom: 1rem; }}
    button {{ padding: 0.6rem 1rem; }}
  </style>
</head>
<body>
  <h1>Pflanzenliste Suche</h1>
  <form method="get" action="/">
    <div class="controls">
      <div style="flex:1; min-width:200px;">
        <label for="q">Freitext:</label>
        <input type="text" id="q" name="q" value="{query_html}" placeholder="z. B. Wasser, Salvia, gelb" />
      </div>
      <label><input type="checkbox" name="regex" {regex_checked} /> Regulärer Ausdruck</label>
      <label><input type="checkbox" name="case" value="sensitive" {case_sensitive_checked} /> Groß-/Kleinschreibung beachten</label>
      <button type="submit">Suchen</button>
    </div>
    <div class="filters">
      {''.join(filter_html)}
      <div class="filter-block">{month_select}</div>
    </div>
  </form>
  {result_info}
  <section>
    {results_html}
  </section>
</body>
</html>
"""


def render_rows(rows, fieldnames):
    if not rows:
        return '<p>Keine Treffer gefunden.</p>'

    head = '<tr>' + ''.join(f'<th>{html.escape(name)}</th>' for name in fieldnames) + '</tr>'
    body_rows = []
    for row in rows:
        row_cells = ''.join(f'<td>{html.escape(str(row.get(field, "")).strip())}</td>' for field in fieldnames)
        body_rows.append(f'<tr>{row_cells}</tr>')
    body = '\n'.join(body_rows)
    return f'<table>{head}{body}</table>'


class SearchHandler(BaseHTTPRequestHandler):
    rows = None
    fieldnames = None
    dropdowns = None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/":
            self.send_error(404)
            return

        params = parse_qs(parsed.query)
        query = params.get("q", [""])[0].strip()
        regex = "regex" in params
        ignore_case = params.get("case", [""])[0] != "sensitive"
        selected_filters = {field: params.get(field, ["all"])[0] for field in FILTER_FIELDS}
        selected_months = params.get("month", ["all"])
        if "all" in selected_months:
            selected_months = ["all"]

        if SearchHandler.rows is None:
            SearchHandler.rows = load_rows(CSV_PATH)
            SearchHandler.fieldnames = list(SearchHandler.rows[0].keys()) if SearchHandler.rows else []
            SearchHandler.dropdowns = {field: unique_values(SearchHandler.rows, field) for field in FILTER_FIELDS}

        matcher = build_matcher(query, regex, ignore_case) if query else None
        results = []
        for row in SearchHandler.rows:
            if matcher and not row_matches(row, matcher):
                continue
            match_filters = True
            for field, value in selected_filters.items():
                if value != "all" and str(row.get(field, "")).strip() != value:
                    match_filters = False
                    break
            if not match_filters:
                continue
            if selected_months != ["all"]:
                if not any(str(row.get(month, "")).strip() == "1" for month in selected_months):
                    continue
            results.append(row)

        page = build_page(query, regex, ignore_case, selected_filters, selected_months, results, SearchHandler.fieldnames, SearchHandler.dropdowns)

        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Starte eine lokale Weboberfläche für die Pflanzen-Suche.")
    parser.add_argument("--host", default="0.0.0.0", help="Host, auf dem der Server lauscht. Standard: 0.0.0.0")
    parser.add_argument("--port", type=int, default=8000, help="Port für den Webserver. Standard: 8000")
    args = parser.parse_args()

    if not CSV_PATH.exists():
        print(f"CSV-Datei nicht gefunden: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    server = ThreadingHTTPServer((args.host, args.port), SearchHandler)
    print(f"Websuche gestartet: http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer beendet.")
        server.server_close()


if __name__ == "__main__":
    main()
