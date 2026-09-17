# Security

## Confidentialité

FaceIQ est conçu pour fonctionner localement. Les photos analysées, visages extraits et rapports générés restent sur la machine de l'utilisateur tant que celui-ci ne les partage pas lui-même.

Le dépôt public ne doit contenir aucune photo personnelle, aucun corpus de test privé et aucun rapport généré à partir de données réelles.

## Données à ne pas versionner

- photos ou visages d'utilisateurs ;
- répertoires de résultats FaceIQ ;
- fichiers `.env` réels ;
- clés privées, certificats privés ou credentials ;
- journaux contenant des chemins ou données personnelles ;
- corpus soumis à des conditions de redistribution incompatibles.

Les dossiers `samples/` et `output/` sont ignorés par Git à l'exception de leurs fichiers `.gitkeep`.

## Signalement d'une vulnérabilité

N'ajoutez pas de photo personnelle, secret, chemin privé ou autre donnée sensible dans une issue publique. Décrivez le problème avec des données synthétiques lorsque c'est possible.

## Chaîne de livraison

Le dépôt exécute un scan Gitleaks sur l'historique Git afin de détecter les secrets ajoutés accidentellement. Les dépendances et workflows de build doivent rester épinglés et revus lors de leurs mises à jour.
