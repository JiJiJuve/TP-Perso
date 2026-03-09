# 🔐 FICHE MÉMO – Chiffrement de fichier en AES‑GCM avec Python (PyCryptodome + scrypt)

Objectif : chiffrer et déchiffrer un fichier (`monfichier.txt`) avec **AES‑256‑GCM** en Python, à partir d’un **mot de passe** dérivé en clé via **scrypt**, en utilisant deux scripts :  
- `chiffrer-gcm.py` → création de `monfichier.txt.enc`  
- `dechiffrer-gcm.py` → recrée le fichier en clair à partir de `monfichier.txt.enc`

---

## 1. Bibliothèques utilisées

```python
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes   # seulement dans le script de chiffrement
import getpass
```

- `AES` : chiffrement symétrique (mode GCM).  
- `scrypt` : dérivation de clé à partir d’un mot de passe (KDF).  
- `get_random_bytes` : génération de `salt` et `nonce` pour le chiffrement.  
- `getpass` : saisie du mot de passe **sans l’afficher**.

Le mot de passe est toujours récupéré ainsi :

```python
password = getpass.getpass("Mot de passe : ").encode()
```

---

## 2. Script 1 – CHIFFREMENT (`chiffrer-gcm.py`)

### 2.1 Lecture du fichier à chiffrer

```python
with open("monfichier.txt", "rb") as f:
    message = f.read()
```

- Ouverture en mode binaire (`"rb"`).  
- Le contenu complet du fichier est chargé dans `message`.

### 2.2 Génération du sel + dérivation de la clé (scrypt)

```python
salt = get_random_bytes(16)
key = scrypt(password, salt, key_len=32, N=2**14, r=8, p=1)
```

- `salt` : 16 octets aléatoires, indispensable à conserver.  
- `key_len=32` : clé de 32 octets → **AES‑256**.  
- Paramètres scrypt : `N=2**14`, `r=8`, `p=1` (coût CPU/mémoire contre le bruteforce).  
- Pour déchiffrer, il faudra **exactement** les mêmes paramètres et le même `salt`.

### 2.3 Initialisation d’AES en mode GCM

```python
cipher = AES.new(key, AES.MODE_GCM)
nonce = cipher.nonce
```

- `AES.MODE_GCM` : Galois/Counter Mode = chiffrement + authentification (AEAD).  
- `nonce` : valeur unique générée automatiquement par la librairie, à conserver avec le ciphertext.

### 2.4 Chiffrement + tag d’authentification

```python
ciphertext, tag = cipher.encrypt_and_digest(message)
```

- `ciphertext` : texte chiffré.  
- `tag` : tag d’authentification GCM, protège l’intégrité et le mot de passe.

### 2.5 Fichier de sortie : `[salt][nonce][tag][ciphertext]`

```python
with open("monfichier.txt.enc", "wb") as f:
    f.write(salt)       # 16 octets
    f.write(nonce)      # taille du nonce GCM (ex. 16 octets)
    f.write(tag)        # 16 octets de tag
    f.write(ciphertext) # le texte chiffré

print("Fichier chiffré : monfichier.txt.enc")
```

Le fichier `monfichier.txt.enc` contient donc, dans cet ordre :

1. `salt`  
2. `nonce`  
3. `tag`  
4. `ciphertext`

---

## 3. Script 2 – DÉCHIFFREMENT (`dechiffrer-gcm.py`)

### 3.1 Lecture des éléments depuis `monfichier.txt.enc`

```python
password = getpass.getpass("Mot de passe : ").encode()

with open("monfichier.txt.enc", "rb") as f:
    salt = f.read(16)
    nonce = f.read(16)
    tag = f.read(16)
    ciphertext = f.read()
```

- On lit les 16 premiers octets pour le `salt`,  
- les 16 suivants pour le `nonce`,  
- les 16 suivants pour le `tag`,  
- tout le reste du fichier est le `ciphertext`.

### 3.2 Redérivation de la clé avec scrypt

```python
key = scrypt(password, salt, key_len=32, N=2**14, r=8, p=1)
```

- Doit utiliser **exactement** les mêmes paramètres que le script de chiffrement.  
- Le même mot de passe + le même `salt` → la même clé.

### 3.3 Déchiffrement + vérification du tag

```python
cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

try:
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

    with open("monfichier_dechiffre.txt", "wb") as f:
        f.write(plaintext)

    print("Fichier déchiffré : monfichier_dechiffre.txt")

except ValueError:
    print("Mot de passe incorrect ou fichier modifié")
```

- `decrypt_and_verify(ciphertext, tag)` :
  - déchiffre le `ciphertext`,  
  - vérifie que le `tag` correspond (intégrité + mot de passe correct).  
- Si le mot de passe est faux ou que le fichier a été altéré, une `ValueError` est levée, et le message d’erreur est affiché.

---

## 4. Résumé du flux complet

- **Chiffrement (`chiffrer-gcm.py`)**  
  - Entrées : `monfichier.txt` + mot de passe.  
  - Sortie : `monfichier.txt.enc` contenant `[salt][nonce][tag][ciphertext]`.

- **Déchiffrement (`dechiffrer-gcm.py`)**  
  - Entrées : `monfichier.txt.enc` + (le même) mot de passe.  
  - Sortie : `monfichier_dechiffre.txt` si tout est correct, ou message d’erreur si mot de passe faux / fichier modifié.

---

## 5. Points clés à retenir

- Ne jamais stocker le **mot de passe**, seulement le `salt` et le `nonce` avec le ciphertext.  
- Toujours garder la même structure de fichier : `[salt][nonce][tag][ciphertext]`.  
- Les paramètres scrypt (`N=2**14, r=8, p=1`) doivent être identiques côté chiffrement et déchiffrement.  
- GCM vérifie l’intégrité : si le fichier est modifié ou le mot de passe erroné, `decrypt_and_verify` échoue.  
- Chiffrement et déchiffrement fonctionnent en paire : ne pas changer l’ordre d’écriture/lecture dans le fichier.
