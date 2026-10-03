@echo off
setlocal enabledelayedexpansion

:: 1. Ustawienie wartosci domyslnej
set DEFAULT_FILE=pomorskie.osm.pbf
set OSM_FILE_NAME=%DEFAULT_FILE%

:: 2. Wczytanie zmiennych z pliku .env (jesli istnieje)
if exist .env (
    echo [INFO] Znaleziono plik .env. Wczytywanie konfiguracji...
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "KEY=%%A"
        set "VAL=%%B"
        if not "!KEY!"=="" (
            if not "!KEY:~0,1!"=="#" (
                if "!KEY!"=="OSM_FILE_NAME" (
                    set "OSM_FILE_NAME=!VAL!"
                )
            )
        )
    )
) else (
    echo [OSTRZEZENIE] Brak pliku .env. Uzywam domyslnej nazwy: %OSM_FILE_NAME%
)

:: Upewnij sie, ze katalog geojsons istnieje
if not exist "%cd%\geojsons" mkdir "%cd%\geojsons"

:: 3. Sprawdzanie i ewentualne pobieranie pliku .pbf
if not exist "%cd%\geojsons\%OSM_FILE_NAME%" (
    echo [INFO] Brak pliku geojsons\%OSM_FILE_NAME%. Proba pobrania...
    
    for %%F in ("%OSM_FILE_NAME%") do set "RAW_NAME=%%~nF"
    for %%F in ("!RAW_NAME!") do set "REGION_NAME=%%~nF"

    set "DOWNLOAD_URL=https://download.geofabrik.de/europe/poland/!REGION_NAME!-latest.osm.pbf"
    echo [POBIERANIE] !DOWNLOAD_URL!
    curl -L --fail "!DOWNLOAD_URL!" -o "%cd%\geojsons\%OSM_FILE_NAME%"

    if !ERRORLEVEL! neq 0 (
        echo [OSTRZEZENIE] Nie udalo sie pobrac %OSM_FILE_NAME%.
        echo [INFO] Pobieram domyslny wyciag Pomorskie...
        set "OSM_FILE_NAME=%DEFAULT_FILE%"
        curl -L --fail "https://download.geofabrik.de/europe/poland/pomorskie-latest.osm.pbf" -o "%cd%\geojsons\%DEFAULT_FILE%"
        if !ERRORLEVEL! neq 0 (
            echo [BLAD KRYTYCZNY] Nie udalo sie pobrac pliku OSM.
            pause
            exit /b 1
        )
    )
)

:: 4. Wyciagniecie nazwy wyjsciowej
for %%F in ("%OSM_FILE_NAME%") do set "BASE_NAME=%%~nF"
for %%F in ("!BASE_NAME!") do set "OUTPUT_NAME=%%~nF"

echo ========================================================
echo Plik zrodlowy OSM: %OSM_FILE_NAME%
echo Plik wynikowy:    !OUTPUT_NAME!.pmtiles
echo Katalog roboczy:  %cd%\geojsons
echo ========================================================

:: 5. Uruchomienie Planetilera z flagami --download oraz --force
docker run -e JAVA_OPTS="-Xmx4g" --rm ^
  -v "%cd%\geojsons:/data" ^
  ghcr.io/onthegomap/planetiler:latest ^
  --osm-path="/data/%OSM_FILE_NAME%" ^
  --output="/data/!OUTPUT_NAME!.pmtiles" ^
  --download ^
  --force

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUKCES] Pomyslnie wygenerowano plik geojsons\!OUTPUT_NAME!.pmtiles
    
    :: Sprzatanie cache Planetilera
    if exist "%cd%\geojsons\tmp" rd /s /q "%cd%\geojsons\tmp"
    if exist "%cd%\geojsons\tile_weights.tsv.gz" del /f /q "%cd%\geojsons\tile_weights.tsv.gz"
    
    echo.
    echo ========================================================
    echo Uruchamianie lokalnego serwera kafelkow: npx http-server
    echo Otworz w przegladarce: http://localhost:8080/maps/tile_map.html
    echo Aby zatrzymac serwer, wcisnij Ctrl + C
    echo ========================================================
    npx http-server . -p 8080 --cors
) else (
    echo.
    echo [BLAD] Wystapil problem podczas generowania kafelkow.
    pause
)