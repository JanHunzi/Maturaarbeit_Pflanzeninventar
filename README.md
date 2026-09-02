# Maturaarbeit_Pflanzeninventar

Dieses Projekt enthält eine Pflanzenliste im CSV-Format und eine Suchfunktion für alle Spalten.

## Lokale Suche

Mit dem Skript `search_plants.py` kannst du in allen Spalten nach einem Begriff suchen.

Beispiele:

- Suche nach "Wasser":
  `python3 search_plants.py Wasser`
- Suche nach dem lateinischen Namen "Salvia":
  `python3 search_plants.py Salvia`
- Zeige alle Spaltennamen:
  `python3 search_plants.py --columns`
- Suche als regulären Ausdruck:
  `python3 search_plants.py --regex "^Hydro"`
- Zähle nur die Treffer:
  `python3 search_plants.py --count Wasser`

Hinweis: Das Skript erkennt automatisch das Semikolon als Feldtrenner.

## Weboberfläche mit Dropdown-Filtern

Mit dem Skript `web_search.py` kannst du eine Weboberfläche starten, die den CSV-Inhalt in allen Spalten durchsucht.

- Starte den Webserver lokal:
  `python3 web_search.py`
- Verwende einen anderen Port:
  `python3 web_search.py --port 8080`
- Öffne im Browser:
  `http://localhost:8000/`

Die Oberfläche bietet Dropdown-Felder für:

- `Name Deutsch`
- `Name Latein`
- `Pflanzenfamilie`
- `Wuchsform`
- `Blütenfarbe`
- `Gepflanzt`
- `Monat`

Du kannst zusätzlich einen Freitext in allen Spalten suchen.

### Neue Pflanzen hinzufügen

Oben in der Weboberfläche gibt es den Button **Neue Pflanze hinzufügen**. Damit kannst du neue Pflanzen samt Fotos direkt im Browser erfassen; die Einträge werden lokal im Browser gespeichert.

### Bilder für die Webseite

Wenn du Pflanzenbilder hinzufügen möchtest, lege sie in einem Ordner `images/` ab. Die Seite sucht nach Dateien im Format:

- `PF-001.jpg`
- `PF-001.png`
- `PF-001.1.jpg`
- `PF-001.2.png`

Die Nummer entspricht der `ID` der Pflanze aus der CSV-Datei.

Welche Bilder tatsächlich angezeigt werden, steht in `images/image_index.json`.
Diese Datei wird nicht von Hand gepflegt, sondern mit

```
python3 scripts/build_image_index.py
```

aus dem Inhalt von `images/` neu erzeugt. Das Skript ordnet Dateien robust
ihrer Pflanzen-ID zu: Gross-/Kleinschreibung, das Trennzeichen zwischen `PF`
und der Nummer (`-`, `_`, Leerzeichen oder keins), führende Nullen sowie
Umlaute/Akzente im restlichen Dateinamen spielen keine Rolle. Unterstützt
werden die Endungen `.jpg`, `.jpeg`, `.png` und `.webp`. Dateien ohne
erkennbare `PF-<Nummer>`-ID (z.B. Referenzbilder wie `Z.1_web.webp`) werden
übersprungen. Führt eine Pflanze zu keinem passenden Bild, zeigt die
Weboberfläche stattdessen den Hinweis „kein Bild vorhanden“ an, statt einen
Fehler zu verursachen.

Beim Deployment auf GitHub Pages (`.github/workflows/pages.yml`) wird dieses
Skript automatisch vor dem Veröffentlichen ausgeführt, damit der Index nie
veraltet.

### Externen Zugriff ermöglichen

1. Wenn du in einer lokalen Umgebung arbeitest, musst du sicherstellen, dass Port 8000 vom Netzwerk zugänglich ist.
2. In einer Cloud- oder Codespace-Umgebung kannst du den Port 8000 weiterleiten.
3. Verwende die ausgegebene externe URL oder den Tunnel deiner Umgebung, um von außen auf die Weboberfläche zuzugreifen.

Beispiel: In GitHub Codespaces kannst du `http://<externe-url>:8000/` verwenden, nachdem Port 8000 weitergeleitet wurde.
