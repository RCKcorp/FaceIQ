# Architecture — FaceIQ

## Structure cible du projet

```text
FaceIQ/
├── README.md
├── requirements.txt
├── .gitignore
├── docs/
│   ├── PROJECT_SPEC.md
│   ├── ROADMAP.md
│   ├── ARCHITECTURE.md
│   ├── SOURCES.md
│   └── WORKFLOW_PHOTOGRAPHES.md
├── src/
│   └── faceiq/
│       ├── __init__.py
│       ├── app.py
│       ├── detector.py
│       ├── extractor.py
│       ├── quality.py
│       ├── exporter.py
│       ├── config.py
│       └── logger.py
├── tests/
│   └── .gitkeep
├── samples/
│   └── .gitkeep
├── output/
│   └── .gitkeep
└── FaceIQ_Workspace/        # données locales, ignorées par Git
    ├── 00_A_RECEVOIR/
    ├── 01_EVENEMENTS/
    └── 02_ARCHIVES/
```

`samples` ne doit contenir que des images de test. Les vraies sources photographes passent par `FaceIQ_Workspace\00_A_RECEVOIR`.

## Rôle des modules

### app.py

Point d'entrée de l'application.

Dans la V1, ce fichier pourra lancer le traitement en console.

Dans la V2, il lancera l'interface graphique.

### detector.py

Responsable de la détection des visages dans les images.

### extractor.py

Responsable du découpage et de l'export temporaire des visages détectés.

### quality.py

Responsable du calcul de la note qualité.

Critères prévus :

- netteté ;
- luminosité ;
- taille ;
- cadrage ;
- orientation ;
- confiance de détection.

### exporter.py

Responsable de l'export des résultats :

- images classées ;
- rapport CSV ;
- futur rapport Excel ou HTML.

### config.py

Responsable des paramètres de l'application :

- seuils de notation ;
- formats d'images acceptés ;
- noms des dossiers de sortie ;
- marge autour du visage.

### logger.py

Responsable des logs techniques et des erreurs.

## Organisation des résultats

```text
FaceIQ_Resultats/
├── Excellent/
├── Bon/
├── Moyen/
├── Mauvais/
├── Tous_les_visages/
└── rapport_analyse.csv
```

## Philosophie technique

Le projet doit rester :

- simple ;
- lisible ;
- local ;
- maintenable ;
- facilement transformable en exécutable Windows.

La priorité est d'obtenir une V1 fiable avant d'ajouter des fonctions avancées.
