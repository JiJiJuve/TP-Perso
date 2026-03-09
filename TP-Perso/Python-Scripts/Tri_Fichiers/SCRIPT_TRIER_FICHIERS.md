# FICHE MÉMO – SCRIPT TRIER FICHIERS (Argparse / Pathlib)

Lancer depuis PowerShell :

```bash
python Tri_Fichiers.py --source "G:\Mon Drive\Maison"
```

- Parcourir le dossier `--source`.  
- Pour chaque fichier, créer un sous-dossier par extension (PDF, JPG, XLS, GDOC, …) et déplacer le fichier dedans.

---

## 1. Structure générale

Juste pour avoir tout au même endroit dans ta fiche (tu l’as déjà, mais là c’est ton récap) :

```python
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Dossier à trier")
    args = parser.parse_args()

    source = Path(args.source)
    print("Dossier source :", source)

    for i in source.iterdir():
        if i.is_file():
            extension = i.suffix.lower()
            if not extension:
                # fichier sans extension, à traiter plus tard si tu veux
                continue

            sous_dossier_nom = extension[1:].upper()
            sous_dossier = source / sous_dossier_nom
            sous_dossier.mkdir(exist_ok=True)

            destination = sous_dossier / i.name

            print(
                "FICHIER :", i.name,
                "| Extension :", extension,
                "| DOSSIER :", sous_dossier_nom,
                "| DESTINATION :", destination
            )

            i.replace(destination)
        else:
            print("DOSSIER :", i.name)


if __name__ == "__main__":
    main()
```

---

## 2. Squelette de base

Importer les modules nécessaires :

```python
import argparse          # gérer les arguments en ligne de commande
from pathlib import Path # manipuler les chemins proprement
```

Structure “bonne pratique” :

```python
def main():
    # code principal ici
    ...

if __name__ == "__main__":
    main()
```

Création du parser + argument `--source` :

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Dossier à trier")  # --source obligatoire
    args = parser.parse_args()

    source = Path(args.source)  # transforme la string en objet Path
    print("Dossier source :", source)
```

---

## 3. Parcourir le dossier avec pathlib

Boucler sur le contenu du dossier :

```python
for i in source.iterdir():      # i = chaque entrée dans source (fichier ou dossier)
    if i.is_file():             # ne garder que les fichiers, pas les sous-dossiers
        ...
    else:
        print("DOSSIER :", i.name)
```

- `i.name` = juste le nom du fichier/dossier.

---

## 4. Récupérer l’extension et calculer le nom de dossier

Dans le `if i.is_file()` :

```python
extension = i.suffix.lower()          # ".PDF" -> ".pdf"
sous_dossier_nom = extension[1:].upper()  # ".pdf" -> "PDF"
```

Idée :

- `suffix` donne l’extension avec le point (`.pdf`, `.jpg`).  
- `lower()` normalise en minuscules.  
- `extension[1:]` enlève le point.  
- `upper()` met en majuscules pour le nom du sous-dossier.

---

## 5. Construire et créer le sous-dossier

Toujours dans le `if i.is_file()` :

```python
sous_dossier = source / sous_dossier_nom      # G:\Mon Drive\Maison\PDF
sous_dossier.mkdir(exist_ok=True)             # crée PDF, JPG, etc. sans erreur si ça existe déjà
```

- L’opérateur `/` sur un `Path` sert à joindre les morceaux de chemin (version objet de `os.path.join`).  
- `mkdir(exist_ok=True)` = “crée le dossier s’il n’existe pas, ne plante pas s’il existe déjà”.

---

## 6. Calculer la destination du fichier

Toujours dans le même bloc :

```python
destination = sous_dossier / i.name  # G:\Mon Drive\Maison\PDF\facture.pdf
```

- On reprend la même logique : chemin du dossier + nom du fichier.

---

## 7. Déplacer le fichier

Enfin, déplacement réel :

```python
print(
    "FICHIER :", i.name,
    "| Extension :", extension,
    "| DOSSIER :", sous_dossier_nom,
    "| DESTINATION :", destination
)

i.replace(destination)  # déplace le fichier vers destination (et écrase si déjà présent)
```

- `replace()` sur un `Path` déplace/renomme le fichier vers le nouveau chemin.
