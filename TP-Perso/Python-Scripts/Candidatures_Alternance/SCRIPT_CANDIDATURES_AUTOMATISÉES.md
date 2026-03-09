# FICHE MÉMO – SCRIPT CANDIDATURES AUTOMATISÉES

## Structure du script

```python
import smtplib
from email.message import EmailMessage
import time


def main():
    # Connexion SMTP Gmail
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    email = input("Ton email Gmail : ")
    password = input("Ton mot de passe d'application Gmail : ")
    server.login(email, password)
    print("Connecté !")

    # Lecture des destinataires (1 email par ligne dans entreprises.txt)
    with open("entreprises.txt", "r", encoding="utf-8") as f:
        recipients = f.read().splitlines()
    print(f"{len(recipients)} entreprises trouvées !")

    # Boucle d'envoi
    for recipient in recipients:
        msg = EmailMessage()
        msg["To"] = recipient
        msg["Subject"] = "alternance AIS – Saint-Étienne (42)"
        msg["From"] = email

        msg.set_content(
            """Bonjour,

blablabla...

Cordialement,
Jimmy PAULIN
"""
        )

        # Pièces jointes
        with open("CV_Jimmy_Paulin.pdf", "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="CV_Jimmy_Paulin.pdf",
            )

        with open("Programme_Alternance_AIS.pdf", "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="Programme_Alternance_AIS.pdf",
            )

        with open("Calendrier_Alternance_2026.pdf", "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="Calendrier_Alternance_2026.pdf",
            )

        # Envoi + pause anti-spam
        server.send_message(msg)
        print(f"ENVOYÉ à {recipient} !")
        time.sleep(5)  # Pause entre mails pour limiter le risque de blocage SMTP

    server.quit()
    print("TOUS les mails envoyés !")


if __name__ == "__main__":
    main()
```

---

## 🎯 À quoi ça sert ?

- Envoie automatiquement le même mail de candidature à une liste d’entreprises.  
- Ajoute 3 pièces jointes : CV, programme de formation, calendrier.  
- Lit les adresses dans `entreprises.txt` (1 email par ligne).

---

## 📂 Fichiers nécessaires (même dossier que le script)

- `candidatures.py` (ou `candidatures_ais.py`)  
- `entreprises.txt`  
- `CV_Jimmy_Paulin.pdf`  
- `Programme_Alternance_AIS.pdf`  
- `Calendrier_Alternance_2026.pdf`

---

## 🔐 Préparer le compte Gmail

Pour que le SMTP Gmail fonctionne, il faut :

1. Activer la **validation en 2 étapes** sur ton compte Google (2‑Step Verification). [web:410][web:408]  
2. Générer un **mot de passe d’application** (16 caractères) dans la section *Mots de passe des applications*. [web:406][web:412]  
3. Quand Google affiche quelque chose comme `nydp hmfj rqkq ocua`, tu l’utilises **sans les espaces** : `nydphmfjrqkqocua`. [cite:397][web:408]  
4. Dans le script, quand il demande `Ton mot de passe d'application Gmail :`, tu tapes ce mot de passe d’application (pas ton mot de passe normal). [web:387][web:406]

---

## 🔧 Ligne par ligne

### Imports

```python
import smtplib
from email.message import EmailMessage
import time
```

- `smtplib` : dialogue avec le serveur SMTP Gmail. [web:387]  
- `EmailMessage` : construit un mail moderne (texte + pièces jointes).  
- `time` : permet `time.sleep(5)` pour faire une pause entre les mails.

### Connexion SMTP

```python
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
```

- Serveur sortant Gmail : `smtp.gmail.com`, port `587`, chiffrement TLS via STARTTLS. [web:387][web:385]

```python
email = input("Ton email Gmail : ")
password = input("Ton mot de passe d'application Gmail : ")
server.login(email, password)
print("✅ Connecté !")
```

- Demande ton adresse Gmail et ton mot de passe d’application. [web:387][web:406]  
- `login()` authentifie ta session SMTP.

### Lecture des destinataires

```python
with open("entreprises.txt", "r", encoding="utf-8") as f:
    recipients = f.read().splitlines()
print(f"{len(recipients)} entreprises trouvées !")
```

- Ouvre `entreprises.txt`.  
- Chaque ligne devient une adresse email dans la liste `recipients`.

### Construction du mail

```python
for recipient in recipients:
    msg = EmailMessage()
    msg["To"] = recipient
    msg["Subject"] = "alternance AIS – Saint-Étienne (42)"
    msg["From"] = email
```

- Crée un mail par destinataire.  
- `From` = l’email que tu as saisi.

```python
msg.set_content(
    """... ton texte de candidature ..."""
)
```

- Corps du mail en texte brut multi-ligne.  
- Tu peux modifier facilement le texte plus tard.

### Pièces jointes

```python
with open("CV_Jimmy_Paulin.pdf", "rb") as f:
    msg.add_attachment(
        f.read(),
        maintype="application",
        subtype="pdf",
        filename="CV_Jimmy_Paulin.pdf",
    )
```

- Ouvre le PDF en binaire (`"rb"`).  
- `add_attachment()` ajoute le contenu comme pièce jointe.  
- Même logique pour le programme et le calendrier.

### Envoi + anti‑spam

```python
server.send_message(msg)
print(f"ENVOYÉ à {recipient} !")
time.sleep(5)
```

- Envoie le mail complet (texte + PJ).  
- Pause de 5 s entre chaque envoi pour limiter le risque de blocage ou de détection spam.

### Fermeture

```python
server.quit()
print("TOUS les mails envoyés !")
```

- Ferme proprement la connexion SMTP.

---

## 🚀 Lancement

Dans PowerShell :

```bash
cd "C:\\Ton\\Dossier\\Script"
python candidatures.py
```

---

## ⚠️ Erreurs courantes

- `FileNotFoundError`  
  → Un des PDF ou `entreprises.txt` n’existe pas / mauvais nom.  
  → Vérifier les noms exacts dans le dossier.

- `smtplib.SMTPAuthenticationError`  
  → Mauvais mot de passe d’appli ou problème côté Gmail. [web:387][web:412]  
  → Vérifier email, mot de passe d’application, et que la 2FA est bien activée.

- `smtplib.SMTPRecipientsRefused`  
  → Adresse destinataire invalide.  
  → Corriger `entreprises.txt`.

- `ConnectionRefusedError` / `timeout`  
  → Problème réseau ou blocage SMTP.  
  → Vérifier connexion Internet / pare-feu.
