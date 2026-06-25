# FaceIQ

FaceIQ est une application Windows locale qui détecte les visages d'un dossier de photos, les extrait, leur attribue une note technique et génère un rapport CSV. Elle ne transmet aucune image dans le cloud.

## Fonctionnalités V1

- Analyse les formats JPG, JPEG, PNG et WEBP, y compris dans les sous-dossiers.
- Détecte les visages frontaux avec le modèle OpenCV inclus dans l'installation.
- Exporte chaque visage avec une marge configurable.
- Calcule un score sur 100 à partir de la netteté, de la luminosité, de la taille, du cadrage et de la fiabilité de détection.
- Classe les visages dans `Excellent`, `Bon`, `Moyen` ou `Mauvais`.
- Produit un rapport `rapport_analyse.csv` lisible dans Excel.

Les scores d'orientation et de confiance constituent une estimation issue du détecteur frontal dans cette V1. Ils seront améliorés par un modèle à points de repère dans une version ultérieure.

## Installation

Ouvrir PowerShell dans le dossier du projet, puis lancer :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Workflow événement

Le mode recommandé pour travailler avec des photographes est de créer un espace de travail FaceIQ, puis un dossier par événement. Les originaux restent séparés des visages extraits, des rapports et des logs.

Règle simple :

- `samples` sert uniquement aux tests et démonstrations.
- `FaceIQ_Workspace\00_A_RECEVOIR` est la seule zone où déposer les vraies photos reçues.
- `FaceIQ_Workspace\01_EVENEMENTS` devient l'archive propre après import.
- `FaceIQ_Workspace\02_ARCHIVES` sert aux événements terminés.

```powershell
faceiq init "C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace"
```

Structure créée :

```text
FaceIQ_Workspace/
├── 00_A_RECEVOIR/
├── 01_EVENEMENTS/
└── 02_ARCHIVES/
```

Demander aux photographes de livrer un dossier par événement, avec un sous-dossier par photographe :

```text
00_A_RECEVOIR/
└── Gala_Client/
    ├── Alice/
    │   ├── IMG_001.jpg
    │   └── IMG_002.jpg
    └── Bob/
        └── DSC_1001.jpg
```

Lancer l'import et l'extraction en une commande :

```powershell
faceiq run "Gala Client" "C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace\00_A_RECEVOIR\Gala_Client" --workspace "C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace" --date 2026-06-25
```

Pour ajouter plus tard une nouvelle livraison au même événement :

```powershell
faceiq ingest "Gala Client" "C:\Livraisons\Alice_Suite" --photographer "Alice" --workspace "C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace" --date 2026-06-25
faceiq process "Gala Client" --workspace "C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace"
```

Résultat d'un événement :

```text
01_EVENEMENTS/
└── 2026-06-25_gala_client/
    ├── 01_Photos_originales/
    ├── 02_Visages_extraits/
    │   ├── Excellent/
    │   ├── Bon/
    │   ├── Moyen/
    │   ├── Mauvais/
    │   └── Tous_les_visages/
    ├── 03_Rapports/
    │   ├── inventaire_photos.csv
    │   ├── rapport_analyse.csv
    │   └── manifest_event.json
    └── 04_Logs/
        └── faceiq.log
```

FaceIQ copie les photos dans l'événement, ignore les doublons déjà importés grâce au hash SHA-256, puis génère uniquement les visages et les rapports utiles.

## Utilisation simple

Ce mode reste disponible pour tester vite fait un dossier quelconque. Pour un vrai événement avec photographes, utiliser plutôt le workflow événement ci-dessus.

```powershell
faceiq "C:\Photos\A_trier"
```

Par défaut, les résultats sont créés dans `C:\Photos\FaceIQ_Resultats`. Pour choisir un autre emplacement :

```powershell
faceiq "C:\Photos\A_trier" --output "C:\Resultats\FaceIQ"
```

Options utiles :

```text
--no-recursive    Ignore les sous-dossiers.
--margin 0.35     Ajoute 35 % de marge autour du visage.
--verbose         Affiche les détails de traitement.
```

## Résultats

```text
FaceIQ_Resultats/
├── Excellent/
├── Bon/
├── Moyen/
├── Mauvais/
├── Tous_les_visages/
├── rapport_analyse.csv
└── faceiq.log
```

Le même recadrage est placé dans `Tous_les_visages` et dans son dossier de classement, afin de faciliter les deux modes de consultation.

## Développement

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```
