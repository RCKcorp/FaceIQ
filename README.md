# FaceIQ

**FaceIQ** est une application Windows locale destinée à détecter automatiquement les visages présents dans des photos et des vidéos, les extraire, puis les noter selon leur qualité visuelle.

L'objectif est de faciliter le tri de grandes quantités de photos ou vidéos, notamment des photos de groupe, afin de récupérer rapidement les visages les plus exploitables.

## Objectif principal

L'application permet de :

- sélectionner un fichier ou un dossier contenant des photos et/ou des vidéos ;
- détecter tous les visages présents ;
- extraire chaque visage dans une image séparée ;
- attribuer une note qualité à chaque visage ;
- classer les résultats par niveau de qualité ;
- générer un rapport d'analyse exploitable au format CSV.

## Formats supportés

### Images

- `.jpg`
- `.jpeg`
- `.png`
- `.bmp`
- `.webp`
- `.tif`
- `.tiff`

### Vidéos

- `.mp4`
- `.avi`
- `.mov`
- `.mkv`
- `.wmv`
- `.m4v`

## Critères de notation

La note qualité est basée sur plusieurs critères techniques :

- netteté du visage ;
- luminosité ;
- taille du visage dans l'image ;
- cadrage / centrage ;
- confiance de détection.

## Classement prévu

| Score | Classement |
|---:|---|
| 85 à 100 | Excellent |
| 65 à 84 | Bon |
| 45 à 64 | Moyen |
| 0 à 44 | Mauvais |

## Fonctionnement

```text
Photos / vidéos source
    ↓
Échantillonnage vidéo, si nécessaire
    ↓
Détection des visages
    ↓
Extraction des visages
    ↓
Notation qualité
    ↓
Classement automatique
    ↓
Export rapport CSV
```

Pour les vidéos, FaceIQ n'analyse pas toutes les frames. Par défaut, il analyse une frame par seconde afin d'éviter un traitement trop lourd.

## Installation

Créer un environnement Python puis installer les dépendances :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Utilisation

Analyser tout le dossier `samples` :

```bash
python main.py samples
```

Analyser un fichier vidéo :

```bash
python main.py samples/videos/video.mp4
```

Analyser une frame toutes les 2 secondes :

```bash
python main.py samples --frame-interval 2
```

Conserver seulement les visages avec un score minimum de 60 :

```bash
python main.py samples --min-score 60
```

Limiter les vidéos aux 10 meilleurs visages détectés :

```bash
python main.py samples --max-faces-per-video 10
```

Changer le dossier de sortie :

```bash
python main.py samples -o FaceIQ_Resultats
```

## Résultats générés

Les visages extraits sont enregistrés dans :

```text
output/faces/
```

Le rapport CSV est généré dans :

```text
output/reports/rapport_faceiq.csv
```

Le rapport contient notamment :

- le fichier source ;
- le type de source : image ou vidéo ;
- le timestamp vidéo, si applicable ;
- le numéro de frame, si applicable ;
- le chemin du visage extrait ;
- le score global ;
- le classement qualité ;
- les scores techniques détaillés.

## Plateforme cible

- Windows 10 / Windows 11
- PC portable type HP G8
- Fonctionnement local
- Aucune dépendance cloud obligatoire

## Statut du projet

Première base fonctionnelle en ligne de commande.

Étapes suivantes recommandées :

1. tester sur un dossier réel de photos et vidéos ;
2. ajuster les seuils de qualité ;
3. ajouter une interface Windows simple ;
4. ajouter une suppression des doublons vidéo ;
5. générer un `.exe` avec PyInstaller.
