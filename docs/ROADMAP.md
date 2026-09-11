# Roadmap — FaceIQ

## V1 — Application locale Windows

- [x] Définir le projet et l’architecture
- [x] Lire un dossier d’images
- [x] Inclure optionnellement les sous-dossiers
- [x] Détecter les visages localement
- [x] Extraire les visages avec marge
- [x] Calculer netteté, luminosité, taille, cadrage, orientation et confiance
- [x] Générer un score sur 100
- [x] Classer Excellent / Bon / Moyen / Mauvais
- [x] Générer un rapport CSV
- [x] Générer un rapport HTML
- [x] Créer l’interface Windows
- [x] Ajouter barre de progression et annulation
- [x] Afficher les résultats dans l’application
- [x] Ajouter logs et gestion d’erreurs
- [x] Ajouter tests unitaires
- [x] Préparer le build PyInstaller
- [x] Préparer un installateur Inno Setup
- [x] Ajouter une CI Windows

## V1.1 — Calibration

- [ ] Tester le score sur un corpus de photos réelles variées
- [ ] Ajuster les courbes de netteté et luminosité
- [ ] Ajouter un panneau détaillant les sous-scores dans l’interface
- [ ] Ajouter une icône et les métadonnées Windows de l’exécutable
- [ ] Ajouter des tests d’intégration sur un petit corpus non sensible

## V2 — Détection améliorée

- [ ] Ajouter un backend YuNet local
- [ ] Conserver le backend OpenCV classique en secours
- [ ] Améliorer l’estimation de pose du visage
- [ ] Ajouter les réglages de seuils dans l’interface

## V3 — Regroupement optionnel

- [ ] Regrouper les visages similaires par personne
- [ ] Détecter les doublons
- [ ] Sélectionner automatiquement le meilleur visage d’une série
- [ ] Ajouter comparaison et export de sélection
