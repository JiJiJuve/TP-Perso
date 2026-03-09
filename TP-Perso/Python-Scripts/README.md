# Scripts Python d’automatisation

Ce dossier regroupe plusieurs petits scripts Python utilisés en pratique pour automatiser des tâches du quotidien (renommage de fichiers, tri, nettoyage, envoi de mails de candidature).

## 1. Renommage de fichiers (Pathlib / Argparse)

Scripts pour renommer automatiquement des photos ou vidéos dans un dossier avec un préfixe et une numérotation.

- Un script où le dossier est défini directement dans le code (cas simple, toujours le même dossier).  
- Un script plus flexible où tu choisis le dossier et le préfixe à utiliser avec les options `--dossier` et `--prefixe` dans la commande.

## 2. Tri de fichiers par extension

Scripts pour ranger un dossier en créant des sous-dossiers par extension (PDF, JPG, DOCX, etc.).

- Un script qui trie vraiment les fichiers en les déplaçant dans des sous-dossiers par extension.  
- Un script avec une option `--dry-run` qui montre ce qu’il ferait, sans modifier ni déplacer aucun fichier.

## 3. Candidatures alternance automatisées

Script pour envoyer automatiquement le même mail de candidature à une liste d’entreprises lue dans `entreprises.txt`.

- Ajoute le CV, le programme de formation et le calendrier en pièces jointes.  
- Fait une pause entre chaque envoi pour limiter les risques de blocage SMTP.

## 4. Nettoyage de fichiers temporaires Windows

Script pour vider plusieurs dossiers temporaires Windows afin de libérer de l’espace disque.

- Cible par exemple `%TEMP%`, `C:\Windows\Temp` et des caches applicatifs.  
- Affiche le nombre total de fichiers supprimés en fin d’exécution.
