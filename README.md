# FaceIQ

FaceIQ est une application Windows locale qui détecte les visages présents dans un dossier de photos, extrait chaque visage, évalue sa qualité technique puis classe les résultats.

## Fonctionnalités V1

- interface graphique Windows ;
- sélection d'un dossier et traitement optionnel des sous-dossiers ;
- détection des visages entièrement locale avec OpenCV ;
- extraction automatique avec marge autour du visage ;
- score de qualité sur 100 ;
- détail du score : netteté, luminosité, taille, cadrage, orientation et confiance ;
- classement `Excellent`, `Bon`, `Moyen`, `Mauvais` ;
- galerie de résultats dans l'application ;
- export CSV et rapport HTML local ;
- gestion des images invalides sans interrompre tout le lot ;
- bouton d'annulation ;
- build Windows avec PyInstaller ;
- script Inno Setup pour obtenir un vrai installateur avec désinstallation Windows.

Aucune photo n'est envoyée dans le cloud.

## Installation développeur

Prérequis : Python 3.11 x64.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:PYTHONPATH="src"
python -m faceiq
```

## Build Windows

```powershell
.\build.ps1
```

Le build produit `dist\FaceIQ.exe`. Pour produire l'installateur, compiler `installer\FaceIQ.iss` avec Inno Setup 6. L'installation apparaît ensuite dans **Applications installées** de Windows et peut être désinstallée normalement.

## Résultats

```text
FaceIQ_Resultats_YYYYMMDD_HHMMSS/
├── Excellent/
├── Bon/
├── Moyen/
├── Mauvais/
├── Tous_les_visages/
├── rapport_analyse.csv
└── rapport_analyse.html
```

## Score qualité

| Critère | Poids |
|---|---:|
| Netteté | 35 |
| Luminosité | 20 |
| Taille | 20 |
| Cadrage | 10 |
| Orientation | 10 |
| Confiance de détection | 5 |

La note est technique et sert au tri. Elle ne mesure ni l'identité, ni l'attractivité, ni des caractéristiques personnelles.

## Confidentialité

FaceIQ fonctionne localement. Les photos et visages extraits restent sur la machine de l'utilisateur.

## Suite prévue

La V2 pourra remplacer le backend OpenCV classique par YuNet et ajouter, de manière optionnelle, le regroupement de photos d'une même personne afin de sélectionner le meilleur cliché d'une série.
