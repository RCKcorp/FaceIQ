# Spécification projet — FaceIQ

## 1. Vision du projet

FaceIQ est une application locale permettant d'analyser automatiquement des dossiers de photos pour détecter, extraire et noter les visages selon leur qualité technique.

Le projet doit rester simple à utiliser : l'utilisateur choisit un dossier, lance l'analyse, puis récupère un dossier de résultats organisé.

## 2. Problème à résoudre

Quand on possède beaucoup de photos de groupe, il est long de retrouver les visages exploitables.

FaceIQ doit automatiser cette tâche en extrayant tous les visages détectés et en donnant une note qualité pour aider à sélectionner les meilleurs portraits.

## 3. Utilisateurs cibles

- utilisateur Windows souhaitant trier des photos personnelles ;
- photographe amateur ;
- service communication interne ;
- administrateur ou technicien ayant besoin d'un outil local simple ;
- usage hors cloud ou environnement isolé.

## 4. Fonctionnalités principales V1

### 4.1 Sélection du dossier source

L'utilisateur doit pouvoir sélectionner un dossier contenant des images.

Formats visés :

- JPG ;
- JPEG ;
- PNG ;
- WEBP.

### 4.2 Analyse automatique

L'application doit parcourir les images du dossier source et détecter les visages présents.

### 4.3 Extraction des visages

Chaque visage détecté doit être exporté dans une image séparée.

Le découpage doit garder une marge autour du visage pour éviter un rendu trop serré.

### 4.4 Notation qualité

Chaque visage reçoit un score sur 100.

Critères prévus :

| Critère | Description | Poids |
|---|---|---:|
| Netteté | Détection du flou | 35 |
| Luminosité | Image trop sombre ou trop claire | 20 |
| Taille | Visage assez grand pour être exploitable | 20 |
| Cadrage | Visage complet ou coupé | 10 |
| Orientation | Visage de face ou trop tourné | 10 |
| Confiance | Fiabilité de la détection | 5 |

### 4.5 Classement automatique

Les visages extraits doivent être classés dans des dossiers :

- Excellent ;
- Bon ;
- Moyen ;
- Mauvais.

### 4.6 Rapport d'analyse

Un rapport CSV doit être généré avec au minimum :

- nom de la photo source ;
- numéro du visage détecté ;
- score total ;
- classement ;
- score de netteté ;
- score de luminosité ;
- taille du visage ;
- chemin du fichier exporté.

## 5. Fonctionnalités V2

- interface graphique Windows ;
- barre de progression ;
- aperçu des visages extraits ;
- bouton d'ouverture du dossier résultat ;
- réglage des seuils de notation ;
- export Excel ;
- journalisation des erreurs ;
- mode sombre.

## 6. Fonctionnalités V3

- regroupement des visages par personne ;
- détection des doublons ;
- sélection automatique du meilleur visage par personne ;
- comparaison entre deux visages ;
- rapport HTML ;
- export ZIP ;
- mode traitement de masse.

## 7. Contraintes

- fonctionnement local ;
- pas de cloud obligatoire ;
- compatible Windows ;
- utilisable sur un HP G8 ;
- installation simple ;
- projet maintenable ;
- architecture claire.

## 8. Critères de réussite V1

La V1 est considérée comme réussie si elle permet de :

1. sélectionner un dossier photo ;
2. détecter au moins un visage sur une photo de groupe ;
3. extraire les visages détectés ;
4. noter les visages ;
5. classer les résultats ;
6. générer un rapport CSV ;
7. fonctionner sans connexion Internet.
