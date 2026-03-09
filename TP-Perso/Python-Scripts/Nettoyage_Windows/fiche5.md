# 🧹 FICHE MÉMO – NETTOYEUR TEMP WINDOWS

## 🎯 À quoi ça sert ?

Nettoie automatiquement `%TEMP%` + `C:\Windows\Temp` + le cache LibreWolf (environ 147 fichiers typiques dans ton cas).

## 📂 Fichiers nécessaires

- `nettoyeur_temp.py` ← le seul fichier (copie-colle le script complet)

---

## Structure du script

```python
import os
from pathlib import Path


def main():
    total = 0
    dossiers = [
        os.environ["TEMP"],                      # %TEMP% utilisateur
        "C:/Windows/Temp",                       # Temp système
        os.environ["LOCALAPPDATA"] + "/Temp",    # Temp applis
        os.environ["LOCALAPPDATA"] + "/LibreWolf/Cache"  # Cache LibreWolf
    ]

    for dossier in dossiers:
        for fichier in Path(dossier).glob("*"):
            try:
                fichier.unlink()
                total += 1
            except:
                pass

    print(f"✅ {total} fichiers supprimés !")
    input("Appuie Entrée...")


if __name__ == "__main__":
    main()
```

---

## 🔧 LIGNE PAR LIGNE – Mémorisation rapide

### 1–3. Imports

```python
import os                    # Parle au système Windows
from pathlib import Path     # Objets chemins intelligents
```

### 5. Ossature "pro"

```python
def main(): ...              # Toute la logique
if __name__ == "__main__":   # Lance si double-clic
    main()
```

### 7. Compteur

```python
total = 0                    # Avant les boucles !
```

### 9. Liste des dossiers (tes 4 cibles)

```python
dossiers = [
    os.environ["TEMP"],                    # %TEMP% utilisateur
    "C:/Windows/Temp",                     # Temp système
    os.environ["LOCALAPPDATA"] + "/Temp",  # Temp applis
    os.environ["LOCALAPPDATA"] + "/LibreWolf/Cache"  # TON navigateur
]
```

### 12. Boucle principale (comme tes emails !)

```python
for dossier in dossiers:                          # Chaque dossier
    for fichier in Path(dossier).glob("*"):       # Chaque fichier dedans
        try:
            fichier.unlink()                      # SUPPRIME !
            total += 1                            # +1 compteur
        except:                                   # Erreur ?
            pass                                  # Ignore + suivant
```

### 16. Résultat final

```python
print(f"✅ {total} fichiers supprimés !")
```

---

## 🚀 Lancement

Dans PowerShell :

```bash
cd "C:\Ton\Dossier"
python nettoyage_Fichiers.py
```

Résultat attendu typique :

```text
✅ 147 fichiers supprimés !
```

---

## ⚠️ Erreurs courantes

- **FileNotFoundError**  
  → Dossier LibreWolf absent.  
  → Commenter la ligne `os.environ["LOCALAPPDATA"] + "/LibreWolf/Cache"`.

- **PermissionError**  
  → Fichier système verrouillé.  
  → Le `try/except` gère tout, le script continue.

- **0 fichiers**  
  → Dossiers déjà propres.  
  → Normal, relance dans 1 semaine.

> Évolution possible : rajouter le vidage de la corbeille.
