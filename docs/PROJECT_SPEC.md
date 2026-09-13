# Spécification projet — FaceIQ

## Vision

FaceIQ accélère le tri technique de lots de photographies en donnant une vue
immédiate des visages les plus nets, correctement éclairés et suffisamment
grands. L'application n'effectue aucune identification.

## Périmètre V1

La V1 permet de :

1. sélectionner un dossier de photos ;
2. analyser JPG, JPEG, PNG et WEBP ;
3. inclure optionnellement les sous-dossiers ;
4. détecter les visages frontaux et de profil sans service cloud ;
5. extraire chaque visage avec marge ;
6. calculer et expliquer un score sur 100 ;
7. classer les résultats ;
8. afficher les visages dans l'interface ;
9. produire un CSV et un rapport HTML ;
10. poursuivre le lot si une image est illisible ;
11. annuler une analyse ;
12. installer et désinstaller l'application comme un logiciel Windows.

## Score

| Critère | Poids |
|---|---:|
| Netteté | 35 |
| Luminosité | 20 |
| Taille | 20 |
| Cadrage | 10 |
| Orientation | 10 |
| Confiance | 5 |

| Score | Classement |
|---:|---|
| 85–100 | Excellent |
| 65–84,9 | Bon |
| 45–64,9 | Moyen |
| moins de 45 | Mauvais |

La note mesure uniquement des propriétés techniques de la photographie.

## Contraintes

- Windows 10 ou 11 x64 ;
- fonctionnement local et hors ligne ;
- aucune télémétrie ni compte ;
- architecture maintenable ;
- gestion robuste des images invalides ;
- installation par utilisateur sans élévation ;
- données de test réelles non copiées dans le dépôt.

## Hors périmètre V1

- analyse vidéo ;
- organisation avancée d'événements photographiques ;
- regroupement par personne ;
- reconnaissance faciale ;
- détection de doublons entre photos ;
- sélection du meilleur cliché d'une même personne.
