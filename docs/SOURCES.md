# Process sources FaceIQ

## Décision

Les vraies photos ne vont plus dans `samples`.

À partir de maintenant :

- `samples` = tests techniques uniquement ;
- `FaceIQ_Workspace\00_A_RECEVOIR` = photos reçues des photographes ;
- `FaceIQ_Workspace\01_EVENEMENTS` = photos importées proprement + visages extraits ;
- `FaceIQ_Workspace\02_ARCHIVES` = événements terminés.

## Où déposer les photos

```text
C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace\00_A_RECEVOIR\Nom_Evenement\Nom_Photographe\
```

Exemple :

```text
C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace\00_A_RECEVOIR\Gala_Client\
├── Alice\
│   ├── IMG_001.jpg
│   └── IMG_002.jpg
└── Bob\
    └── DSC_1001.jpg
```

## Commande de traitement

```powershell
cd "C:\Users\m.senerchia\Documents\app\FaceIQ"
.\.venv\Scripts\faceiq.exe run "Gala Client" ".\FaceIQ_Workspace\00_A_RECEVOIR\Gala_Client" --workspace ".\FaceIQ_Workspace" --date 2026-06-25
```

## Ce que FaceIQ fait automatiquement

1. Copie les photos sources dans l'événement.
2. Range les originaux par photographe.
3. Ignore les doublons déjà importés.
4. Extrait les visages.
5. Classe les visages par qualité.
6. Génère `inventaire_photos.csv` et `rapport_analyse.csv`.

## Où récupérer les résultats

```text
C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace\01_EVENEMENTS\2026-06-25_gala_client\02_Visages_extraits\
```

Le dossier `Tous_les_visages` contient tous les visages extraits. Les dossiers `Excellent` et `Bon` sont les plus utiles pour une livraison rapide.
