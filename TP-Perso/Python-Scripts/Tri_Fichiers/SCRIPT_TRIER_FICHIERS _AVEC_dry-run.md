# FICHE MÉMO – SCRIPT TRIER FICHIERS AVEC --dry-run (Argparse / Pathlib)

## Objectif

Lancer en mode normal (déplacement réel) :

```bash
python V2Bis.py --source "G:\Mon Drive\Projet_Telcora"
```

Lancer en simulation (aucun fichier déplacé) :

```bash
python V2Bis.py --source "G:\Mon Drive\Projet_Telcora" --dry-run
```

Le script parcourt le dossier `--source`, crée des sous-dossiers par extension (DOCX, PNG, PDF, …) et déplace les fichiers dedans, sauf en mode `--dry-run` où il affiche seulement ce qu’il ferait.

---

## Structure générale (script complet)

Importer les modules :

```python
import argparse
from pathlib import Path
```

Script :

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Dossier à trier")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simuler le tri sans déplacer les fichiers"
    )
    args = parser.parse_args()

    source = Path(args.source)
    print("Dossier source :", source)

    for i in source.iterdir():
        if i.is_file():
            extension = i.suffix.lower()
            sous_dossier_nom = extension[1:].upper()
            sous_dossier = source / sous_dossier_nom
            sous_dossier.mkdir(exist_ok=True)

            destination = sous_dossier / i.name

            print(
                "FICHIER :", i.name,
                "| EXTENSION :", extension,
                "| DOSSIER :", sous_dossier_nom,
                "| DESTINATION :", destination
            )

            if args.dry_run:
                print("MODE DRY-RUN : Fichier NON déplacé")
            else:
                i.replace(destination)
        else:
            print("DOSSIER :", i.name)


if __name__ == "__main__":
    main()
```

---

## 2) Squelette de base (à retenir)

### Imports

```python
import argparse          # gérer les arguments en ligne de commande
from pathlib import Path # manipuler les chemins proprement
```

### Structure standard

```python
def main():
    # code principal ici
    ...

if __name__ == "__main__":
    main()
```

### Arguments

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        required=True,
        help="Dossier à trier"      # --source obligatoire
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",        # présent => True, absent => False
        help="Simuler le tri sans déplacer les fichiers"
    )
    args = parser.parse_args()

    source = Path(args.source)      # transforme la string en objet Path
    print("Dossier source :", source)
```

---

## 3) Parcourir le dossier avec pathlib

Boucle principale :

```python
for i in source.iterdir():      # i = chaque entrée (Path) dans source
    if i.is_file():             # ne garder que les fichiers, pas les dossiers
        ...
    else:
        print("DOSSIER :", i.name)
```

- `i` = chemin complet (`Path`).  
- `i.name` = juste le nom du fichier/dossier.

---

## Extension et nom du sous-dossier

Dans le bloc `if i.is_file()` :

```python
extension = i.suffix.lower()              # ".PDF" -> ".pdf"
sous_dossier_nom = extension[1:].upper()  # ".pdf" -> "PDF"
```

Idées :

- `suffix` donne l’extension avec le point (`.pdf`, `.jpg`).  
- `lower()` normalise (`.PDF` -> `.pdf`).  
- `extension[1:]` enlève le point.  
- `upper()` sert à nommer les dossiers en majuscules (PDF, JPG, …).

---

## Construire et créer le sous-dossier

Toujours dans `if i.is_file()` :

```python
sous_dossier = source / sous_dossier_nom   # ex : G:\...\Projet_Telcora\PDF
sous_dossier.mkdir(exist_ok=True)          # crée PDF, PNG, etc. sans erreur si déjà présents
```

- `/` sur un `Path` = joint proprement les morceaux de chemin (équivalent de `os.path.join`).  
- `mkdir(exist_ok=True)` = crée si absent, ne plante pas si déjà là.

---

## Calculer la destination du fichier

```python
destination = sous_dossier / i.name  # ex : G:\...\Projet_Telcora\PDF\facture.pdf
```

- Même logique : chemin du dossier + nom du fichier.

---

## Gestion du --dry-run et déplacement

Affichage commun :

```python
print(
    "FICHIER :", i.name,
    "| EXTENSION :", extension,
    "| DOSSIER :", sous_dossier_nom,
    "| DESTINATION :", destination
)
```

Puis :

```python
if args.dry_run:
    print("MODE DRY-RUN : Fichier NON déplacé")  # prévisualisation, aucune modification
else:
    i.replace(destination)                       # déplace le fichier vers destination (écrase si déjà présent)
```

- `args.dry_run` est `True` si `--dry-run` est présent, sinon `False`.  
- `replace()` sur un `Path` déplace / renomme réellement le fichier.
