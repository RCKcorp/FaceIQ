# Validation V1

Date de validation : 13 septembre 2026.

## Suite automatisée

Commande :

~~~powershell
python -m pytest
~~~

Résultat : **13 tests réussis**.

La suite couvre la configuration, la découverte des fichiers, le score,
l'extraction, les exports CSV/HTML, le miroir des coordonnées, la suppression
des doublons et la détection sur photographies réelles.

## Photographies réelles

La validation d'intégration utilise les jeux de données publics fournis par
scikit-image. Les images sont chargées depuis la dépendance de développement
et ne sont pas enregistrées dans ce dépôt.

| Jeu | Attendu | Résultat V1 |
|---|---|---:|
| LFW subset — 100 images avec visage | Détection d'au moins 80 images | 88/100 |
| LFW subset — 100 images sans visage | Au plus 10 images détectées | 5/100 |
| camera — photographie de profil | Au moins un profil détecté | Réussi |
| astronaut — visage frontal | Analyse complète + export + capture | Réussi |

Les résultats LFW sont mesurés après agrandissement uniforme des petites
vignettes à 250 × 250 pixels. Ce test vérifie une régression technique ; ce
n'est pas un benchmark scientifique de précision.

## Limites connues

- les très petits visages restent difficiles à détecter ;
- les profils très prononcés, les fortes occultations et les rotations
  importantes peuvent être manqués ;
- la cascade de profil peut produire quelques faux positifs ;
- la note dépend de la résolution et doit être considérée comme une aide au
  tri, pas comme une vérité absolue ;
- les résultats peuvent légèrement varier selon la version d'OpenCV.

## Confidentialité

Aucune photographie personnelle n'a été utilisée ou publiée. La capture du
README est générée à partir de l'image d'exemple **astronaut** de
scikit-image.
