# Architecture vidéo FaceIQ

FaceIQ traite les photos et les vidéos avec le même moteur central.

Une vidéo est considérée comme une suite d'images. Le module vidéo extrait une frame toutes les X secondes, puis transmet cette frame au moteur commun.

```text
image ou frame vidéo
    -> détection visage
    -> extraction visage
    -> notation qualité
    -> export CSV
```

## Modules

- `main.py` : point d'entrée en ligne de commande.
- `faceiq/media.py` : détection des formats supportés.
- `faceiq/detector.py` : détection et extraction des visages avec OpenCV.
- `faceiq/quality.py` : calcul de la note qualité.
- `faceiq/frame_processor.py` : moteur commun image/frame vidéo.
- `faceiq/image_processor.py` : traitement des images.
- `faceiq/video_processor.py` : traitement des vidéos.
- `faceiq/exporter.py` : génération du rapport CSV.

## Évolution recommandée

1. Ajouter une interface graphique simple.
2. Ajouter un rapport HTML avec aperçu des visages.
3. Ajouter la suppression des doublons vidéo.
4. Ajouter un export `.exe` avec PyInstaller.
