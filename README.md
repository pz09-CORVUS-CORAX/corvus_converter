## Zależności
- [fontforge](https://fontforge.org/en-US/downloads/)
- [node](https://nodejs.org/en/download/)
- [python](https://www.python.org/downloads/)

## Instalacja
Po instalacji [fontforge'a](https://fontforge.org/en-US/downloads/) należy dodać folder bin tego programu do PATHu.

Zależności pythona znajdują się w pliku requirements.txt i można zainstalować je następująco
```
pip install -r requirements.txt
```

Zależności node'a należy zainstalować następująco
```
cd svg_parser/mat-js
npm install
```

## Użycie
```
fontforge -script font_extractor.py ścieżka_do_pdfu kąt_frezu wysokość_aktywna_frezu prędkość_frezowania
```
