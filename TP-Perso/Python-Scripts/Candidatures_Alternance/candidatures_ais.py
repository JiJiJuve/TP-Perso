import smtplib
from email.message import EmailMessage
import time


def main():
    # Connexion SMTP Gmail
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    email = input("Ton email Gmail : ")
    password = input("Ton mot de passe d'application Gmail  : ")
    server.login(email, password)
    print("Connecté !")

    with open("entreprises.txt", "r", encoding="utf-8") as f:
        recipients = f.read().splitlines()
    print(f"{len(recipients)} entreprises trouvées !")

    for recipient in recipients:
        msg = EmailMessage()
        msg["To"] = recipient
        msg["Subject"] = "alternance AIS – Saint-Étienne (42)"
        msg["From"] = email
        msg["Reply-To"] = "ton adresse mail"

        msg.set_content(
            """Ton message...

Cordialement,
Jimmy PAULIN
"""
        )

        with open("CV_Jimmy_PAULIN.pdf", "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="CV_Jimmy_Paulin.pdf",
            )

        with open("Programme - Alternance Administrateur d-infrastructures securisees - 2025 (1).pdf", "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="Programme_Alternance_AIS.pdf",
            )

        with open("Calendrier - Alternance Administrateur d-infrastructures securisees - octobre 2025 (1).pdf", "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="Calendrier_Alternance_2026.pdf",
            )

        server.send_message(msg)
        print(f"ENVOYÉ à {recipient} !")
        time.sleep(30)

    server.quit()
    print("TOUS les mails envoyés !")


if __name__ == "__main__":
    main()
