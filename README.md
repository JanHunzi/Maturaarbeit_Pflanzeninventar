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
- `Notizen`
- `Monat`

Du kannst zusätzlich einen Freitext in allen Spalten suchen.

### Externen Zugriff ermöglichen

1. Wenn du in einer lokalen Umgebung arbeitest, musst du sicherstellen, dass Port 8000 vom Netzwerk zugänglich ist.
2. In einer Cloud- oder Codespace-Umgebung kannst du den Port 8000 weiterleiten.
3. Verwende die ausgegebene externe URL oder den Tunnel deiner Umgebung, um von außen auf die Weboberfläche zuzugreifen.

Beispiel: In GitHub Codespaces kannst du `http://<externe-url>:8000/` verwenden, nachdem Port 8000 weitergeleitet wurde.
