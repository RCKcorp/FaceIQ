# Roadmap — FaceIQ

## Phase 0 — Cadrage

Objectif : définir clairement le projet avant de coder.

- [x] Choisir le nom du projet
- [x] Créer le dépôt GitHub
- [x] Rédiger le README initial
- [x] Rédiger la spécification projet
- [x] Valider les fonctionnalités V1
- [x] Choisir les technologies
- [ ] Créer les issues GitHub

## Phase 1 — Prototype moteur

Objectif : prouver que l'analyse fonctionne sans interface graphique.

- [x] Lire un dossier d'images
- [x] Détecter les visages
- [x] Extraire les visages
- [x] Calculer la netteté
- [x] Calculer la luminosité
- [x] Calculer la taille du visage
- [x] Générer un score sur 100
- [x] Classer les images par score
- [x] Générer un rapport CSV

## Phase 1.5 — Workflow événement

Objectif : organiser le travail réel avec plusieurs photographes.

- [x] Créer une structure d'espace de travail
- [x] Clarifier la zone source officielle
- [x] Créer un dossier par événement
- [x] Importer les livraisons par photographe
- [x] Détecter et ignorer les doublons importés
- [x] Séparer photos originales, visages, rapports et logs
- [x] Générer un inventaire des photos reçues
- [x] Documenter le process photographe

## Phase 2 — Application Windows simple

Objectif : rendre l'outil utilisable facilement.

- [ ] Créer une interface graphique
- [ ] Ajouter un bouton de sélection du dossier source
- [ ] Ajouter un bouton de lancement d'analyse
- [ ] Ajouter une barre de progression
- [ ] Afficher un résumé des résultats
- [ ] Ajouter un bouton pour ouvrir le dossier de sortie

## Phase 3 — Version propre et exécutable

Objectif : distribuer l'application facilement.

- [x] Nettoyer l'architecture
- [ ] Ajouter un fichier de configuration
- [x] Ajouter des logs
- [x] Ajouter une gestion d'erreurs propre
- [ ] Créer un exécutable Windows
- [ ] Ajouter une icône
- [x] Rédiger une documentation utilisateur

## Phase 4 — Améliorations avancées

Objectif : rendre l'application plus intelligente.

- [ ] Détecter les doublons
- [ ] Regrouper les visages similaires
- [ ] Sélectionner le meilleur visage d'une même personne
- [ ] Générer un rapport HTML
- [ ] Ajouter un mode sombre
- [ ] Ajouter un export Excel
