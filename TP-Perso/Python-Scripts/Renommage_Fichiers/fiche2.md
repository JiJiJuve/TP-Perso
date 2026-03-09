# FICHE MÉMO – Script général avec argparse + pathlib

But du script : renommer automatiquement tous les fichiers d’un dossier en  
`PREFIXE_001.ext`, `PREFIXE_002.ext`, etc., en passant le dossier et le préfixe en arguments de ligne de commande (`--dossier`, `--prefixe`).

## Script complet

```python
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dossier", required=True, help="Chemin du dossier à traiter")
    parser.add_argument("--prefixe", required=True, help="Préfixe pour les nouveaux noms")
    args = parser.parse_args()

    dossier = Path(args.dossier)
    prefixe = args.prefixe
    compteur = 1
    extensions_autorisees = {".jpg", ".mp4"}

    for i in dossier.iterdir():
        if i.is_file():
            extension = i.suffix.lower()
            if extension in extensions_autorisees:
                nouveau_nom = f"{prefixe}_{compteur:03d}{extension}"
                nouvelle_image = i.with_name(nouveau_nom)
                print(i.name, "->", nouveau_nom)
                i.rename(nouvelle_image)
                compteur += 1

if __name__ == "__main__":
    main()
```

## Imports

```python
import argparse
from pathlib import Path
```

Explications :

- `argparse` : module standard qui sert d’analyseur des arguments de la ligne de commande (`--dossier`, `--prefixe`, etc.).  
- `Path` (de `pathlib`) : objet haut niveau pour manipuler les chemins de fichiers/dossiers (`iterdir()`, `is_file()`, `suffix`, `rename()`, etc.), plus pratique que de simples chaînes.

## Fonction main() et structure

```python
def main():
    ...
```

- Regroupe tout le code principal du script dans une fonction.  
- Bonne pratique : facilite la réutilisation et les imports.

```python
if __name__ == "__main__":
    main()
```

- Quand tu exécutes : `python renomme_generique.py`, `__name__` vaut `"__main__"`, donc `main()` est appelée.  
- Si tu fais un jour `import renomme_generique` dans un autre fichier, ce bloc ne s’exécute pas automatiquement.  
- C’est le standard Python pour faire des scripts propres et réutilisables.

## Partie argparse : lire les arguments

```python
parser = argparse.ArgumentParser()
```

- Crée un objet `parser` qui va comprendre les options passées en ligne de commande.

```python
parser.add_argument("--dossier", required=True, help="Chemin du dossier à traiter")
parser.add_argument("--prefixe", required=True, help="Préfixe pour les nouveaux noms")
```

- `--dossier` : argument que l’utilisateur devra fournir.  
- `required=True` : rend cet argument obligatoire (sinon : erreur + message d’aide).  
- `help="..."` : texte d’aide affiché par `--help`.  
- Même chose pour `--prefixe`, qui contient la partie texte du nom de fichier.

```python
args = parser.parse_args()
```

- Lit ce que l’utilisateur a passé après : `python script.py ...`.  
- Remplit un objet `args` avec par exemple :  
  - `args.dossier` → valeur de `--dossier`  
  - `args.prefixe` → valeur de `--prefixe`

Exemple d’appel (ligne de commande) :

```bash
python renomme_generique.py --dossier "C:\Images" --prefixe "Vacances"
# → args.dossier = "C:\Images"
# → args.prefixe = "Vacances"
```

## Préparation des variables

```python
dossier = Path(args.dossier)
prefixe = args.prefixe
compteur = 1
extensions_autorisees = {".jpg", ".mp4"}
```

- `dossier = Path(args.dossier)` : transforme la chaîne passée en argument en objet `Path`, ce qui permet d’utiliser `iterdir()`, `is_file()`, `suffix`, etc.  
- `prefixe = args.prefixe` : récupère la chaîne du préfixe à utiliser pour les nouveaux noms.  
- `compteur = 1` : démarre le compteur de numérotation à 1.  
- `extensions_autorisees = {".jpg", ".mp4"}` : ensemble des extensions autorisées, ce qui permet un test rapide avec `if extension in extensions_autorisees`.

## Parcourir les fichiers et filtrer

```python
for i in dossier.iterdir():
    if i.is_file():
        extension = i.suffix.lower()
        if extension in extensions_autorisees:
            ...
```

- `dossier.iterdir()` : liste tous les éléments (fichiers + sous-dossiers) du dossier.  
- `for i in dossier.iterdir()` : boucle sur chaque élément, un par un.  
- `i.is_file()` : vérifie que l’élément est un fichier (ignore les dossiers).  
- `i.suffix.lower()` : récupère l’extension (`.jpg`, `.mp4`, etc.) en minuscule pour comparer proprement.  
- `if extension in extensions_autorisees` : ne traite que les fichiers avec une extension listée dans l’ensemble.

À retenir :

- `iterdir()` → parcours du dossier.  
- `is_file()` → filtre les fichiers.  
- `suffix` → récupère l’extension.

## Construire le nouveau nom et renommer

```python
nouveau_nom = f"{prefixe}_{compteur:03d}{extension}"
nouvelle_image = i.with_name(nouveau_nom)
print(i.name, "->", nouveau_nom)
i.rename(nouvelle_image)
compteur += 1
```

- `f"{prefixe}_{compteur:03d}{extension}"` : f-string qui construit la chaîne à partir des variables.  
- `compteur:03d` :
  - `d` = entier  
  - `3` = largeur 3  
  - `0` = complété avec des zéros  
  → 1 → `001`, 2 → `002`, etc.  
- Exemple : `prefixe = "Vacances"`, `compteur = 1`, `extension = ".jpg"` → `"Vacances_001.jpg"`.  
- `i.with_name(nouveau_nom)` : crée un nouvel objet `Path` avec le même dossier mais un autre nom de fichier.  
- `print(i.name, "->", nouveau_nom)` : affiche l’ancien nom et le nouveau dans le terminal (log de ce qui est fait).  
- `i.rename(nouvelle_image)` : renomme réellement le fichier sur le disque.  
- `compteur += 1` : incrémente le compteur pour le fichier suivant (`001`, `002`, `003`, ...).

## Exemple d’utilisation (PowerShell)

Dossier Vacances :

```bash
python renomme_generique.py --dossier "C:\Users\JiJi\Pictures\Vac" --prefixe "Vacances_2025_Mai_Grde_Motte"
```

Dossier Chauffage :

```bash
python renomme_generique.py --dossier "G:\Mon Drive\Maison\GrosFichiers - Marlène Rey" --prefixe "Chauffage au sol"
```

Rappel :

- `--dossier` : chemin du dossier à traiter.  
- `--prefixe` : texte utilisé pour construire les nouveaux noms.
