# Architecture — FaceIQ

## État

La V1 est implémentée. L’application sépare l’interface, le moteur d’analyse, la détection, la notation et les exports.

## Structure

```text
FaceIQ/
├── run_faceiq.py
├── FaceIQ.spec
├── build.ps1
├── installer/
│   └── FaceIQ.iss
├── src/faceiq/
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py
│   ├── analyzer.py
│   ├── config.py
│   ├── detector.py
│   ├── exporter.py
│   ├── extractor.py
│   ├── logger.py
│   ├── models.py
│   └── quality.py
└── tests/
```

## Flux de traitement

```text
Dossier source
    ↓
Découverte des images
    ↓
Chargement + correction EXIF
    ↓
Détection locale OpenCV
    ↓
Extraction avec marge
    ↓
Notation qualité
    ↓
Classement
    ↓
Galerie + CSV + HTML
```

## Modules

- `app.py` : interface PySide6 et traitement asynchrone.
- `analyzer.py` : orchestration du lot, annulation et gestion des erreurs.
- `detector.py` : backend de détection isolé et remplaçable.
- `extractor.py` : découpage et sauvegarde des visages.
- `quality.py` : score sur 100.
- `exporter.py` : dossiers de classement, CSV et rapport HTML.
- `config.py` : seuils, poids et paramètres.
- `logger.py` : journal local.
- `models.py` : objets de données partagés.

## Détection

La V1 utilise les cascades livrées avec OpenCV afin de rester entièrement hors ligne et de ne nécessiter aucun téléchargement de modèle au premier lancement. Le backend est encapsulé pour permettre un passage ultérieur à YuNet sans modifier le reste de l’application.

## Distribution Windows

`run_faceiq.py` sert de point d’entrée de package pour PyInstaller. `FaceIQ.spec` produit `FaceIQ.exe`, puis `installer/FaceIQ.iss` permet de créer un installateur Windows avec désinstallation standard.
