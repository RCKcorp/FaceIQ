# Spécification projet — FaceIQ

## Vision

FaceIQ est une application Windows locale destinée à analyser un dossier de photos, détecter les visages, extraire chaque visage et attribuer une note de qualité technique afin d’accélérer le tri.

## V1 livrée

La V1 permet de :

1. sélectionner un dossier photo ;
2. analyser JPG, JPEG, PNG et WEBP ;
3. parcourir optionnellement les sous-dossiers ;
4. détecter les visages sans service cloud ;
5. extraire les visages avec marge ;
6. attribuer une note sur 100 ;
7. classer les résultats ;
8. afficher les visages dans l’interface ;
9. produire un CSV et un rapport HTML ;
10. continuer le traitement si une image est illisible ;
11. annuler une analyse en cours ;
12. construire un exécutable Windows et un installateur.

## Score

| Critère | Poids |
|---|---:|
| Netteté | 35 |
| Luminosité | 20 |
| Taille | 20 |
| Cadrage | 10 |
| Orientation | 10 |
| Confiance | 5 |

Classement :

- 85–100 : Excellent ;
- 65–84,9 : Bon ;
- 45–64,9 : Moyen ;
- moins de 45 : Mauvais.

La note mesure uniquement des propriétés techniques de l’image. Elle ne cherche pas à évaluer l’identité, l’attractivité ou des attributs personnels.

## Contraintes

- Windows 10 / 11 ;
- fonctionnement local ;
- aucune dépendance cloud obligatoire ;
- interface simple ;
- architecture maintenable ;
- traitement de lot robuste ;
- installation et désinstallation Windows classiques.

## Hors périmètre V1

Le regroupement par personne, la reconnaissance faciale, la détection de doublons et la sélection du meilleur visage d’une même personne sont reportés aux versions ultérieures.
