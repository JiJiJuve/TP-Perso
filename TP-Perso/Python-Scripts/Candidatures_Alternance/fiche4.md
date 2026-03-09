# FICHE MÉMO – SCRIPT CANDIDATURES AUTOMATISÉES

## Structure du script

```python
import smtplib
from email.message import EmailMessage
import time


def main():
    # Connexion SMTP Laposte
    server = smtplib.SMTP("smtp.laposte.net", 587)
    server.starttls()

    email = input("Ton email laposte.net : ")
    password = input("Ton mot de passe : ")
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
        msg["Subject"] = "Urgence alternance AIS – Saint-Étienne (42)"
        msg["From"] = email

        msg.set_content(
            """Bonjour,

Actuellement en formation par alternance en Administrateur d'Infrastructures Sécurisées (AIS), débutée le 13/10/2025, je me permets de vous proposer ma candidature pour un contrat d'alternance au sein de votre entreprise.

Mon entreprise a fermé définitivement le 30 novembre 2025, interrompant mon alternance. Je suis donc en recherche urgente d'un nouveau contrat afin de poursuivre ma formation dans les meilleures conditions. Basé à Saint-Étienne, je suis disponible immédiatement pour une alternance dans la Loire (42) et ses environs.

Au travers de ma formation AIS, je me forme à l'administration et à la sécurisation des infrastructures systèmes et réseaux (environnements virtualisés, supervision, gestion des incidents, bonnes pratiques de cybersécurité). Motivé, sérieux et impliqué, je souhaite mettre ces compétences en pratique au service de vos projets et continuer à progresser sur des cas concrets.

Pour vous permettre d'apprécier davantage mon profil technique, je vous invite à consulter mes projets personnels et professionnels :
- GitHub : https://lnkd.in/dX8KtzaA
- LinkedIn : https://www.linkedin.com/in/jimmypaulin/

Je serais ravi d'échanger avec vous afin d'étudier la manière dont je pourrais contribuer à vos activités au sein de votre équipe informatique ou cybersécurité. Vous pouvez me contacter par mail à : jimmy.paulin@laposte.net

Je vous remercie par avance pour l'attention portée à ma candidature et reste à votre disposition pour tout complément d'information ou entretien.

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

## 🔧 Ligne par ligne

### Imports

```python
import smtplib
from email.message import EmailMessage
import time
```

- `smtplib` : dialogue avec le serveur SMTP Laposte.  
- `EmailMessage` : construit un mail moderne (texte + pièces jointes).  
- `time` : permet `time.sleep(5)` pour faire une pause entre les mails.

### Connexion SMTP

```python
server = smtplib.SMTP("smtp.laposte.net", 587)
server.starttls()
```

- Serveur sortant Laposte : `smtp.laposte.net`, port `587`, chiffrement STARTTLS.

```python
email = input("Ton email laposte.net : ")
password = input("Ton mot de passe : ")
server.login(email, password)
print("✅ Connecté !")
```

- Demande ton adresse et ton mot de passe à l’exécution.  
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
    msg["Subject"] = "Urgence alternance AIS – Saint-Étienne (42)"
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
cd "C:\Ton\Dossier\Script"
python candidatures.py
```

---

## ⚠️ Erreurs courantes

- `FileNotFoundError`  
  → Un des PDF ou `entreprises.txt` n’existe pas / mauvais nom.  
  → Vérifier les noms exacts dans le dossier.

- `smtplib.SMTPAuthenticationError`  
  → Mauvais mot de passe ou problème côté Laposte.  
  → Vérifier email / mdp, éventuel blocage du compte.

- `smtplib.SMTPRecipientsRefused`  
  → Adresse destinataire invalide.  
  → Corriger `entreprises.txt`.

- `ConnectionRefusedError` / `timeout`  
  → Problème réseau ou blocage SMTP.  
  → Vérifier connexion Internet / pare-feu.
