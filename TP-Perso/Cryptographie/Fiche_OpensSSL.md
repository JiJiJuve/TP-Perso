# 🗝️ FICHE MÉMO – OpenSSL (Windows / Linux)


<img width="1439" height="764" alt="TP_Chiffrement_Symetrique_OpenSSL" src="https://github.com/user-attachments/assets/46d1176e-66ad-4201-8d2a-9fcc19b87464" />

---

## 1. Installation rapide

### Windows (winget)

```bash
winget install openssl
```

Puis vérifier :

```bash
openssl version
```

Si besoin, ajouter au `PATH` :

- `C:\Program Files\OpenSSL-Win64\bin`

(Optionnel) variable système :

- Nom : `OPENSSL_CONF`  
- Valeur : `C:\Program Files\OpenSSL-Win64\bin\openssl.cfg`

### Ubuntu / Linux

```bash
sudo apt update
sudo apt install openssl
openssl version
```

---

## 2. Chiffrer / déchiffrer un FICHIER (AES‑256‑CBC + PBKDF2)

### Chiffrement

```bash
openssl enc -e -aes-256-cbc -pbkdf2 -iter 100000 -salt -in "NomDuFichier" -out "NomDuFichier.enc"
```

- `-e` : encrypt (chiffrer)  
- `-aes-256-cbc` : algorithme symétrique robuste  
- `-pbkdf2 -iter 100000` : dérivation de clé renforcée (mot de passe → clé)  
- `-salt` : ajoute un sel aléatoire pour éviter les attaques par dictionnaire

Exemple :

```bash
openssl enc -e -aes-256-cbc -pbkdf2 -iter 100000 -salt -in "Secret.docx" -out "Secret.docx.enc"
```

Un mot de passe fort est demandé (à retenir impérativement).

### Déchiffrement

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -salt -in "NomDuFichier.enc" -out "NomDuFichier_dechiffre"
```

- `-d` : decrypt (déchiffrer)  
- Options identiques au chiffrement  
- Utiliser le **même mot de passe**

Exemple :

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -salt -in "Secret.docx.enc" -out "Secret.docx"
```

---

## 3. Chiffrer un DOSSIER (ZIP/TAR + OpenSSL)

OpenSSL ne chiffre que des fichiers. Pour un dossier, on le compresse d’abord.

### 3.1 Windows – compression en ZIP

Se placer dans le dossier parent :

```bash
cd "%USERPROFILE%\Documents"
```

Créer l’archive ZIP :

```bash
tar -a -c -f cv.zip cv
```

- `-a` : choisit le format ZIP automatiquement  
- `-c` : crée une archive  
- `-f cv.zip` : nom de l’archive  
- `cv` : nom du dossier

Chiffrer l’archive :

```bash
openssl enc -e -aes-256-cbc -pbkdf2 -iter 100000 -salt -in cv.zip -out cv.zip.enc
```

(Optionnel) supprimer l’archive non chiffrée :

```bash
del cv.zip
```

Déchiffrer plus tard :

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -salt -in cv.zip.enc -out cv.zip
tar -a -x -f cv.zip
```

### 3.2 Ubuntu / Linux – compression en ZIP ou TAR.GZ

ZIP :

```bash
zip -r cv.zip cv
```

TAR.GZ :

```bash
tar -czf cv.tar.gz cv
```

Puis chiffrement identique :

```bash
openssl enc -e -aes-256-cbc -pbkdf2 -iter 100000 -salt -in cv.zip -out cv.zip.enc
# ou
openssl enc -e -aes-256-cbc -pbkdf2 -iter 100000 -salt -in cv.tar.gz -out cv.tar.gz.enc
```

Déchiffrer puis extraire :

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -salt -in cv.zip.enc -out cv.zip
unzip cv.zip

# ou

openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -salt -in cv.tar.gz.enc -out cv.tar.gz
tar -xzf cv.tar.gz
```

---

## 4. RSA de base (clés publique/privée)

### Générer une clé privée RSA (2048 bits)

```bash
openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048
```

### Extraire la clé publique

```bash
openssl rsa -pubout -in private.pem -out public.pem
```

### Protéger la clé privée par mot de passe

```bash
openssl rsa -aes256 -in private.pem -out private_protected.pem
```

On te demandera un mot de passe pour protéger la clé privée. 

---

## 5. Chiffrement HYBRIDE (gros fichiers)

Principe :  
- AES‑256 (symétrique) pour chiffrer le gros fichier (rapide)  
- RSA pour chiffrer la clé symétrique (sécurisé pour l’échange)

### 5.1 Générer la clé symétrique (32 octets = AES‑256)

```bash
openssl rand -out key.bin 32
# ou pour affichage hex
openssl rand -hex 32
```

### 5.2 Chiffrer le gros fichier avec cette clé

```bash
openssl enc -e -aes-256-cbc -salt -in gros_fichier.zip -out gros_fichier.enc -pass file:key.bin
```

### 5.3 Chiffrer la clé symétrique avec la clé publique (pkeyutl recommandé)

```bash
openssl pkeyutl -encrypt -pubin -inkey public.pem -in key.bin -out key.enc
```

Tu envoies au destinataire :
- `gros_fichier.enc`  
- `key.enc`  

### 5.4 Déchiffrement côté destinataire

1. Déchiffrer la clé symétrique avec la clé privée :

```bash
openssl pkeyutl -decrypt -inkey private.pem -in key.enc -out key.bin
```

2. Déchiffrer le gros fichier :

```bash
openssl enc -d -aes-256-cbc -in gros_fichier.enc -out gros_fichier.zip -pass file:key.bin
```

---

## 6. ZIP vs TAR (rappel rapide)

- **ZIP** :  
  - très compatible (surtout Windows)  
  - accès fichier par fichier  
  - compression correcte  
- **TAR + gzip (.tar.gz)** :  
  - surtout Linux/Unix  
  - meilleure compression pour gros dossiers  
  - conserve mieux les permissions et métadonnées

Choix pratique :
- Windows / partage simple → ZIP  
- Linux / sauvegarde avancée → TAR.GZ

---

## 7. Résumé express (à retenir)

- Fichier seul :  

```bash
openssl enc -e -aes-256-cbc -pbkdf2 -iter 100000 -salt -in fichier -out fichier.enc
openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -salt -in fichier.enc -out fichier_dechiffre
```

- Dossier (Windows) :  

```bash
tar -a -c -f dossier.zip dossier
openssl enc -e -aes-256-cbc -pbkdf2 -iter 100000 -salt -in dossier.zip -out dossier.zip.enc
```

- Générer clé RSA :  

```bash
openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private.pem -out public.pem
```

- Hybride (clé symétrique + RSA) :  

```bash
openssl rand -out key.bin 32
openssl enc -e -aes-256-cbc -salt -in gros_fichier.zip -out gros_fichier.enc -pass file:key.bin
openssl pkeyutl -encrypt -pubin -inkey public.pem -in key.bin -out key.enc
```

Pense toujours à :
- utiliser des mots de passe **forts**,  
- conserver les paramètres (`-pbkdf2`, `-iter`, `-salt`),  
- sauvegarder les clés privées en lieu sûr.
