# FICHE MÉMO – SCRIPT DE RENOMMAGE (dossier spécifique) AVEC PATHLIB

## Structure générale

```python
from pathlib import Path

dossier = Path(r"C:\Users\JiJi\Pictures\Vac")
prefixe = "Vacances_2025_Mai_Grde_Motte"
compteur = 1
extensions_autorisees = {".jpg", ".mp4"}

for image in dossier.iterdir():
    if image.is_file():
        extension = image.suffix.lower()
        if extension in extensions_autorisees:
            nouveau_nom = f"{prefixe}_{compteur:03d}{extension}"
            nouvelle_image = image.with_name(nouveau_nom)
            print(image.name, "->", nouveau_nom)
            image.rename(nouvelle_image)
            compteur += 1
```

## Import et chemin du dossier

```python
from pathlib import Path
dossier = Path(r"C:\Users\JiJi\Pictures\Vac")
```

Explications :

- `from pathlib import Path` : importe la classe Path du module pathlib pour manipuler les chemins.  
- `Path(r"...")` : crée un objet Path vers le dossier `Vac`. Le `r` devant la chaîne évite les problèmes avec les backslashes Windows.

## Préfixe, compteur, extensions

```python
prefixe = "Vacances_2025_Mai_Grde_Motte"
compteur = 1
extensions_autorisees = {".jpg", ".mp4"}
```

Explications :

- `prefixe` : texte commun au début de tous les nouveaux noms de fichiers.  
- `compteur = 1` : nombre de départ pour la numérotation (1, 2, 3, ...).  
- `extensions_autorisees` : ensemble des extensions que l’on veut traiter (ici `.jpg` et `.mp4`).

## Parcourir les fichiers du dossier

```python
for image in dossier.iterdir():
    if image.is_file():
        ...
```

Explications :

- `dossier.iterdir()` : liste tous les éléments du dossier (fichiers et sous-dossiers).  
- `for image in dossier.iterdir()` : boucle sur chaque élément et l’appelle `image`.  
- `image.is_file()` : vérifie que `image` est un fichier (et pas un sous-dossier). On place la suite du code à l’intérieur de ce `if`.

## Récupérer et filtrer l’extension

```python
extension = image.suffix.lower()
if extension in extensions_autorisees:
    ...
```

Explications :

- `image.suffix` : récupère l’extension du fichier, par exemple `.jpg` ou `.mp4`.  
- `.lower()` : met l’extension en minuscule pour éviter les problèmes (`.JPG` → `.jpg`).  
- `if extension in extensions_autorisees` : ne continue que si l’extension fait partie de l’ensemble autorisé.

## Construire le nouveau nom

```python
nouveau_nom = f"{prefixe}_{compteur:03d}{extension}"
```

Explications :

- `f"...{variable}..."` : f-string, permet d’insérer des variables dans une chaîne.  
- `{compteur:03d}` : affiche le compteur sur 3 chiffres avec des zéros devant (001, 002, 010, 123, etc.).  
- Le nouveau nom a la forme : `prefixe_compteur.extension` (ex : `Vacances_2025_Mai_Grde_Motte_005.jpg`).

## Créer le nouveau chemin et renommer

```python
nouvelle_image = image.with_name(nouveau_nom)
print(image.name, "->", nouveau_nom)
image.rename(nouvelle_image)
compteur += 1
```

Explications :

- `image.with_name(nouveau_nom)` : crée un nouveau Path dans le même dossier avec le nouveau nom.  
- `print(image.name, "->", nouveau_nom)` : affiche l’ancien nom et le nouveau dans le terminal.  
- `image.rename(nouvelle_image)` : renomme réellement le fichier sur le disque (ancien nom → nouveau nom).  
- `compteur += 1` : incrémente le compteur pour le fichier suivant.

## Résumé schéma mental

Pour refaire ce type de script :

**Chemin**

```python
from pathlib import Path
dossier = Path(r"...")
```

**Paramètres**

```python
prefixe = "..."
compteur = 1
extensions_autorisees = {...}
```

**Boucle**

```python
for f in dossier.iterdir():
    if f.is_file():
        ...
```

**Extension**

```python
ext = f.suffix.lower()
if ext in extensions_autorisees:
    ...
```

**Nouveau nom**

```python
nouveau_nom = f"{prefixe}_{compteur:03d}{ext}"
```

**Renommage**

```python
nouveau_f = f.with_name(nouveau_nom)
f.rename(nouveau_f)
compteur += 1
```
