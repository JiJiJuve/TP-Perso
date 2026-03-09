# Fiches mémo et comptes-rendus de TP liés à la cryptographie (OpenSSL, AES‑GCM en Python, RSA, certificats, etc.).

---

## 1. À quoi sert la cryptographie ?

La cryptographie sert à protéger les données et les communications : confidentialité (rendre les données illisibles sans clé), intégrité (détecter les modifications), authentification (s’assurer de l’identité) et non-répudiation (prouver qu’un auteur ne peut nier avoir envoyé un message).

Dans ce dossier, elle est utilisée pour :
- chiffrer des fichiers et dossiers (OpenSSL, AES‑GCM en Python) ;
- échanger des clés en sécurité (RSA, chiffrement hybride) ;
- signer des scripts PowerShell pour garantir leur intégrité et leur origine.

---

## 2. Chiffrement symétrique vs asymétrique

- **Chiffrement symétrique** :  
  - une seule clé secrète pour chiffrer et déchiffrer ;  
  - très rapide, adapté aux gros volumes de données (fichiers, archives, flux) ;  
  - exemples : AES‑256‑CBC avec OpenSSL, AES‑GCM en Python.

- **Chiffrement asymétrique (à clé publique)** :  
  - deux clés différentes mais liées : clé publique (chiffre) et clé privée (déchiffre) ;  
  - plus lent, utilisé pour échanger une clé symétrique ou pour les signatures ;  
  - exemple : RSA (génération de `private.pem` / `public.pem`).

En pratique, les deux sont souvent combinés : asymétrique pour échanger la clé symétrique, puis symétrique pour chiffrer les gros fichiers (chiffrement hybride).

---

## 3. Fiches disponibles dans ce dossier

- [Fiche – AES‑GCM en Python](./Fiche%20-%20AES-GCM%20Python.md)  
  Chiffrement et déchiffrement d’un fichier avec AES‑GCM, dérivation de clé avec scrypt, format de fichier `[salt][nonce][tag][ciphertext]`.

- [Fiche – OpenSSL (Windows / Linux)](./Fiche%20-%20OpenSSL.md)  
  Chiffrement de fichiers et dossiers avec AES‑256‑CBC, création de clés RSA, chiffrement hybride (clé symétrique + RSA).

- [Fiche – Signature scripts PowerShell](./Fiche%20-%20Signature%20scripts%20PowerShell.md)  
  Certificat auto-signé de code signing, import dans les magasins de confiance, signature et vérification de scripts PowerShell.
```
