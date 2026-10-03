# Naper 🗺️

Ten projekt służy do parsowania danych lokalizacyjnych w formacie **NMEA** i wizualizacji ich na interaktywnej mapie przy użyciu biblioteki **Lonboard**. Dodatkowo aplikacja przetwarza i wyświetla informacje przestrzenne z plików **PBF** (OpenStreetMap).

---

## Jak to działa?

1. Parsowanie NMEA (data/raw.txt):
   - Skrypt odczytuje surowe logi NMEA z pliku data/raw.txt.
   - Śledzi postęp i numer ostatnio sparsowanej linii w pliku data/state.txt, co pozwala na inkrementalne wznawianie pracy.
   - Pozycje i epoki są serializowane w data/epochs.pkl w celu przyspieszenia kolejnych uruchomień.
   - Wynikowy ślad przestrzenny GPS jest zapisywany jako geojsons/driven.geojson.

2. Przetwarzanie OpenStreetMap (PBF):
   - Aplikacja wczytuje wskazany w konfiguracji plik źródłowy .osm.pbf (np. wyciąg dla województwa pomorskiego) i generuje z niego warstwy pomocnicze w katalogu geojsons/.

3. Wizualizacja:
   - Na podstawie danych z driven.geojson oraz przetworzonych danych OSM generowana jest jedna, spójna mapa maps/driven.html (oparta o Lonboard).

---

## Struktura projektu

```text
naper/
├── data/
│   ├── raw.txt          # Surowe logi NMEA z urządzenia GPS
│   ├── state.txt        # Numer ostatnio przetworzonej linii z raw.txt
│   └── epochs.pkl       # Zrzut obiektów epok (pickle) dla szybkiego wznawiania
├── geojson/             # Pliki GeoJSON wygenerowane z PBF oraz:
│   ├── driven.geojson   # Przetworzony ślad z NMEA
│   └── *.osm.pbf        # Pobrany wyciąg OSM (ignorowany przez Git)
├── maps/
│   └── driven.html      # Wyjściowa interaktywna mapa (Lonboard)
├── src/
│   ├── constants.py     # Stałe, niezmienne dane konfiguracyjne projektu
│   ├── geography.py     # Narzędzia i funkcje pomocnicze do obliczeń geograficznych
│   ├── main.py          # Główny punkt startowy aplikacji
│   ├── map.py           # Tworzenie i generowanie mapy
│   ├── osm.py           # Wyciąganie danych przestrzennych z pliku PBF
│   ├── parser.py        # Parsowanie danych NMEA wraz z dedykowaną klasą
│   └── utils.py         # Ogólne funkcje pomocnicze (utilsy)            
├── .env.example         # Wzór pliku zmiennych środowiskowych
├── pyproject.toml       # Konfiguracja środowiska i zależności
└── README.md
```

---

## Stos technologiczny

### Obecny stan:
- Język i środowisko: Python 3.14, menedżer pakietów uv
- Przetwarzanie danych: GeoPandas
- Wizualizacja: Lonboard
- Formaty danych: NMEA, PBF (OpenStreetMap), GeoJSON, Pickle

### Docelowa architektura (Roadmap):
- Baza danych: PostgreSQL + PostGIS (zastąpienie lokalnych plików GeoJSON i Pickle)
- Serwowanie danych: Kafelki wektorowe (MVT) generowane w locie funkcją ST_AsMVT
- Frontend / Aplikacja webowa: Interfejs webowy (np. MapLibre GL JS) z obsługą kont i edycją punktów

---

## Wymagania wstępne

- Python 3.14+
- Zainstalowane narzędzie uv (https://docs.astral.sh/uv/)

---

## Konfiguracja i uruchomienie

1. Przygotowanie repozytorium:
   ```bash
   git clone https://github.com/Tryczyk/naper.git
   cd naper
   ```

2. Zmienne środowiskowe:
   Skopiuj wzorzec konfiguracji:
   ```bash
   cp .env.example .env
   ```
   W pliku .env wskaż nazwę pliku PBF umieszczonego w data/geojson/:
   OSM_FILE_NAME=pomorskie.osm.pbf

   Uwaga: Pliki .pbf, archiwa .pkl oraz duże logi raw.txt nie powinny być commitowane do repozytorium Git ze względu na swój rozmiar.

3. Uruchomienie:
   Projekt wykorzystuje uv do automatycznego zarządzania środowiskiem i zależnościami:
   ```bash
   uv run src/main.py
   ```
Po zakończeniu działania otwórz plik maps/driven.html w przeglądarce internetowej.