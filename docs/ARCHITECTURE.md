# Architecture — FaceIQ

## Vue d'ensemble

FaceIQ sépare l'interface, l'orchestration du lot, la détection, la notation et
les exports. L'application fonctionne hors ligne et ne transmet aucune image.

~~~text
Dossier source
    ↓
Chargement + correction EXIF
    ↓
Détection frontal / profils gauche et droit
    ↓
Suppression des détections en double
    ↓
Extraction + score technique
    ↓
Galerie + dossiers classés + CSV + HTML
~~~

## Modules

- **app.py** : interface PySide6 et traitement dans un thread dédié ;
- **analyzer.py** : parcours du lot, annulation et gestion des erreurs ;
- **detector.py** : cascades frontale et profil, miroir gauche/droit et
  déduplication par intersection sur union ;
- **extractor.py** : découpage et sauvegarde JPEG ;
- **quality.py** : score pondéré sur 100 ;
- **exporter.py** : dossiers, rapport CSV et galerie HTML ;
- **resources.py** : accès aux ressources en développement et dans PyInstaller ;
- **config.py** : seuils, poids et paramètres ;
- **logger.py** : journal local ;
- **models.py** : objets de données.

## Détection

La V1 utilise trois passages OpenCV :

1. cascade frontale ;
2. cascade de profil sur l'image originale ;
3. même cascade sur l'image miroir pour l'autre orientation.

Les rectangles qui se chevauchent sont fusionnés afin de ne pas exporter
plusieurs fois le même visage. Cette solution reste légère, embarquée et
entièrement hors ligne. Un backend YuNet pourra être ajouté plus tard si une
précision supérieure justifie l'ajout d'un modèle ONNX à distribuer.

## Distribution Windows

**FaceIQ.spec** produit un exécutable graphique autonome avec les cascades
OpenCV, l'icône et les ressources de marque. **installer/FaceIQ.iss** transforme
cet exécutable en setup pour l'utilisateur courant.

Le workflow Windows :

1. installe les dépendances ;
2. exécute tous les tests ;
3. construit l'EXE avec PyInstaller ;
4. compile le setup avec Inno Setup ;
5. sur **main**, crée ou met à jour la Release **v1.0.0**.

Le setup est publié comme actif de Release et non comme artifact GitHub
Actions, afin de ne pas dépendre du quota de stockage des artifacts.
