# FaceIQ

**FaceIQ** est une application Windows locale destinée à détecter automatiquement les visages présents dans des photos, les extraire, puis les noter selon leur qualité visuelle.

L'objectif est de faciliter le tri de grandes quantités de photos, notamment des photos de groupe, afin de récupérer rapidement les visages les plus exploitables.

## Objectif principal

L'application doit permettre de :

- sélectionner un dossier contenant des photos ;
- détecter tous les visages présents ;
- extraire chaque visage dans une image séparée ;
- attribuer une note qualité à chaque visage ;
- classer les résultats par niveau de qualité ;
- générer un rapport d'analyse exploitable.

## Critères de notation

La note qualité sera basée sur plusieurs critères techniques :

- netteté du visage ;
- luminosité ;
- taille du visage dans l'image ;
- cadrage ;
- orientation du visage ;
- confiance de détection.

## Classement prévu

| Score | Classement |
|---:|---|
| 85 à 100 | Excellent |
| 65 à 84 | Bon |
| 45 à 64 | Moyen |
| 0 à 44 | Mauvais |

## Fonctionnement cible

```text
Photos source
    ↓
Détection des visages
    ↓
Extraction des visages
    ↓
Notation qualité
    ↓
Classement automatique
    ↓
Export rapport
```

## Plateforme cible

- Windows 10 / Windows 11
- PC portable type HP G8
- Fonctionnement local
- Aucune dépendance cloud obligatoire

## Statut du projet

Projet en phase de cadrage.

Les premières étapes sont :

1. définir les fonctionnalités ;
2. créer la structure du projet ;
3. choisir les technologies ;
4. développer une première version fonctionnelle ;
5. améliorer l'interface et l'expérience utilisateur.
