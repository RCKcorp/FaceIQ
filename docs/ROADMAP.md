# Roadmap — FaceIQ

## V1.0 — Application Windows

- [x] Interface graphique et traitement asynchrone
- [x] Détection frontale et profils gauche/droit
- [x] Suppression des détections en double
- [x] Extraction et score technique sur 100
- [x] Classement et galerie de résultats
- [x] Rapports CSV et HTML
- [x] Annulation, logs et gestion des images invalides
- [x] Identité visuelle, icône et métadonnées Windows
- [x] Tests unitaires et validation sur photos réelles publiques
- [x] EXE PyInstaller et installateur Inno Setup
- [x] Publication automatique d'une Release GitHub
- [x] Licence MIT et notices tierces

## V1.1 — Calibration

- [ ] Ajouter des réglages simples de sensibilité dans l'interface
- [ ] Afficher le détail des sous-scores au clic
- [ ] Ajouter HEIC si une dépendance locale fiable est retenue
- [ ] Élargir le corpus de calibration
- [ ] Signer numériquement le setup

## V2 — Lots photographiques

La PR historique #7 reste une référence de conception, mais son code divergent
n'est pas fusionné dans la V1.

- [ ] Créer un espace de travail par événement
- [ ] Importer les originaux avec détection des doublons de fichiers
- [ ] Ajouter un historique des analyses

## V2 — Vidéo

La PR historique #8 valide le principe d'échantillonnage vidéo, mais sa
structure et sa couverture de tests ne permettent pas une fusion directe.

- [ ] Réimplémenter le traitement vidéo sur le moteur V1
- [ ] Choisir l'intervalle d'échantillonnage
- [ ] Limiter les doublons entre images successives
- [ ] Exporter vidéo source et timecode

## V3 — Sélection assistée

- [ ] Regrouper optionnellement les visages similaires
- [ ] Détecter les doublons visuels
- [ ] Sélectionner le meilleur visage d'une série
- [ ] Ajouter comparaison et export de sélection
