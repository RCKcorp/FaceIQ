# Utilisation FaceIQ

## Lancer une analyse complète

```bash
python main.py samples
```

FaceIQ parcourt récursivement le dossier et analyse les images et vidéos supportées.

## Analyser uniquement une vidéo

```bash
python main.py samples/videos/video.mp4
```

## Réduire la charge sur les vidéos

Par défaut, FaceIQ analyse une frame toutes les secondes.

Pour analyser une frame toutes les 2 secondes :

```bash
python main.py samples --frame-interval 2
```

## Éviter les mauvais visages

Pour ne garder que les visages avec un score supérieur ou égal à 60 :

```bash
python main.py samples --min-score 60
```

## Limiter les doublons vidéo

Pour garder seulement les 10 meilleurs visages par vidéo :

```bash
python main.py samples --max-faces-per-video 10
```

## Sorties générées

```text
output/faces/
output/reports/rapport_faceiq.csv
```

Le CSV contient le fichier source, le type image/vidéo, le timestamp vidéo, le numéro de frame, le score et les détails de notation.
