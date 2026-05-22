# Data Science RAG

Dieses Repository ist als Sammelpunkt fuer mehrere Bausteine des Projekts gedacht. Damit scraper-spezifischer Code nicht den Rest der Struktur dominiert, liegt der Web-Scraper jetzt in einem eigenen Verzeichnis.

## Projektstruktur

```text
.
|-- .github/
|-- README.md
`-- web_scraper/
    |-- README.md
    |-- requirements.txt
    |-- scraper.py
    `-- tests/
```

## Bereiche im Repository

### Web Scraper

Der Minecraft-Wiki-Scraper liegt gesammelt unter `web_scraper/`.

- Scraper: `web_scraper/scraper.py`
- Tests: `web_scraper/tests/`
- Abhaengigkeiten: `web_scraper/requirements.txt`
- Detaillierte Nutzung: siehe `web_scraper/README.md`

Der Web-Scraper ist bewusst einfach gehalten: eine Python-Datei fuer die Logik und Ausfuehrung, dazu ein Testordner.

## CI

Die Tests laufen jetzt auch automatisch in GitHub Actions bei `push` und `pull_request` ueber `.github/workflows/tests.yml`.

### Weitere Projektteile

Das Root-Verzeichnis bleibt bewusst schlank, damit hier spaeter weitere Komponenten des RAG-Projekts ergaenzt werden koennen, ohne dass scraper-spezifische Dateien alles vermischen.

## Installation

```bash
python3 -m pip install -r web_scraper/requirements.txt
```
