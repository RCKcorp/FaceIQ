# Workflow photographes

Ce document décrit le process recommandé pour éviter les échanges flous, les doublons et les pertes de temps.

## Objectif

Recevoir des photos d'événements, conserver les originaux par photographe, extraire uniquement les visages exploitables et produire un rapport clair.

## Règle des dossiers sources

- `samples` : uniquement des images de test pour vérifier que FaceIQ fonctionne.
- `FaceIQ_Workspace\00_A_RECEVOIR` : zone d'arrivée des vraies livraisons photographes.
- `FaceIQ_Workspace\01_EVENEMENTS\...\01_Photos_originales` : archive propre créée automatiquement après import.
- `FaceIQ_Workspace\01_EVENEMENTS\...\02_Visages_extraits` : visages livrables.
- `FaceIQ_Workspace\02_ARCHIVES` : événements terminés à conserver.

Ne mets pas de nouvelles photos client dans `samples`. Ce dossier peut être nettoyé, remplacé ou ignoré sans impacter la production.

## Process standard

1. Créer une seule fois l'espace de travail :

   ```powershell
   faceiq init "C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace"
   ```

2. Pour chaque événement, créer un dossier dans `00_A_RECEVOIR`.

   ```text
   FaceIQ_Workspace/
   └── 00_A_RECEVOIR/
       └── 2026-06-25_Gala_Client/
           ├── Alice/
           └── Bob/
   ```

3. Demander à chaque photographe de déposer ses photos dans son propre dossier.

4. Lancer le traitement complet :

   ```powershell
   faceiq run "Gala Client" "C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace\00_A_RECEVOIR\2026-06-25_Gala_Client" --workspace "C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace" --date 2026-06-25
   ```

5. Récupérer les visages dans :

   ```text
   FaceIQ_Workspace\01_EVENEMENTS\2026-06-25_gala_client\02_Visages_extraits\Tous_les_visages
   ```

6. Contrôler le rapport CSV :

   ```text
   FaceIQ_Workspace\01_EVENEMENTS\2026-06-25_gala_client\03_Rapports\rapport_analyse.csv
   ```

## Livraison photographe attendue

- Un dossier ou ZIP par photographe.
- Photos originales non compressées si possible.
- Formats acceptés : JPG, JPEG, PNG, WEBP.
- Ne pas mélanger plusieurs événements dans le même dossier.
- Ne pas envoyer de captures WhatsApp si les fichiers originaux existent.
- Nom conseillé : `AAAA-MM-JJ_Evenement_Photographe`.

## Ajouter une livraison après coup

Si un photographe renvoie des photos plus tard :

```powershell
faceiq ingest "Gala Client" "C:\Livraisons\Alice_Suite" --photographer "Alice" --workspace "C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace" --date 2026-06-25
faceiq process "Gala Client" --workspace "C:\Users\m.senerchia\Documents\app\FaceIQ\FaceIQ_Workspace"
```

FaceIQ garde un inventaire dans `inventaire_photos.csv` et ignore les doublons déjà importés.

## Cycle de vie d'une source

```text
Photographe
  ↓
00_A_RECEVOIR\Nom_Evenement\Nom_Photographe
  ↓ faceiq run / faceiq ingest
01_EVENEMENTS\AAAA-MM-JJ_nom_evenement\01_Photos_originales\Nom_Photographe
  ↓ faceiq process
01_EVENEMENTS\AAAA-MM-JJ_nom_evenement\02_Visages_extraits
```

## Ce que tu transmets en interne

- `02_Visages_extraits\Tous_les_visages` si tu veux tous les visages.
- `02_Visages_extraits\Excellent` et `02_Visages_extraits\Bon` si tu veux seulement les meilleurs.
- `03_Rapports\rapport_analyse.csv` pour tracer la photo source, le photographe et le score.

## Règles pratiques

- Garder `01_Photos_originales` comme archive brute de l'événement.
- Ne jamais travailler directement dans `00_A_RECEVOIR` après import.
- Relancer `process` après chaque nouvelle livraison.
- Archiver le dossier événement complet quand le client est livré.
- Vérifier les droits/consentements liés aux visages selon le cadre de l'événement.
