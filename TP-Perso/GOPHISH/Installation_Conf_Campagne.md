# Campagne Phishing Entreprise

Ce dépôt documente une simulation de phishing interne basée sur une VM Kali, GoPhish, un serveur Python pour la page de sensibilisation, et l’import d’utilisateurs AD depuis un CSV.

## Sommaire

- [Objectif](#objectif)
- [Prérequis](#prérequis)
- [1. Création de la VM Kali](#1-création-de-la-vm-kali)
- [2. Extraction des utilisateurs AD](#2-extraction-des-utilisateurs-ad)
- [3. Installation et configuration de GoPhish](#3-installation-et-configuration-de-gophish)
- [4. Serveur Python et page de sensibilisation](#4-serveur-python-et-page-de-sensibilisation)
- [5. Configuration de la campagne](#5-configuration-de-la-campagne)
- [6. Flux utilisateur complet](#6-flux-utilisateur-complet)
- [7. Commandes de secours](#7-commandes-de-secours)
- [8. Nettoyage](#8-nettoyage)
- [Captures d’écran](#captures-décran)

## Objectif

Mettre en place un environnement de test pour simuler une campagne de phishing interne, servir une page de sensibilisation, et suivre les interactions dans GoPhish.

## Prérequis

- Une installation de VirtualBox.
- Une image ISO officielle de Kali Linux.
- Un accès réseau sur le même LAN que le serveur ou les postes cibles.
- Un compte administrateur sur le contrôleur de domaine pour exporter les utilisateurs.
- GoPhish.
- Python 3.

## 1. Création de la VM Kali

### VirtualBox
J’ai utilisé VirtualBox comme hyperviseur pour créer la machine virtuelle Kali Linux.  
VirtualBox permet d’exécuter un système invité dans un environnement isolé, sans modifier la machine hôte.

Avant installation, j’ai téléchargé VirtualBox depuis le site officiel d’Oracle, puis j’ai vérifié le hash du fichier d’installation.  
Cette vérification permet de contrôler l’intégrité du fichier et de s’assurer qu’il provient bien de la version publiée officiellement.

![Hash VirtualBox](Phishing/Hash_VirtualBox.png)

![Verif Hash VirtualBox](Phishing/Verif_Hash_VirtualBox.png)

### Téléchargement de l’ISO Kali
J’ai ensuite téléchargé l’image ISO officielle de Kali Linux depuis le site officiel de Kali.  
Le but était d’utiliser une image propre, fiable et identique à celle publiée par l’éditeur.

Avant installation, j’ai vérifié le hash SHA-256 de l’ISO Kali.  
Cette étape permet de vérifier l’intégrité du fichier et son authenticité.

![Hash ISO Kali](Phishing/Hash_ISO_Kali.png)

![Verif Hash ISO Kali](Phishing/Verif_Hash_ISO_Kali.png)

### Installation
J’ai créé une nouvelle machine virtuelle dans VirtualBox, puis j’ai monté l’ISO Kali dans le lecteur virtuel.  
J’ai alloué suffisamment de mémoire, de processeurs et d’espace disque pour que la VM soit confortable à utiliser.

![Création VM Kali](Phishing/Creation_VM_Kali.png)

### Vérification réseau
Une fois Kali démarré, j’ai vérifié l’adresse IP de la VM avec :

```bash
ip addr show eth0
```

Puis j’ai testé la connectivité avec :

```bash
ping 192.168.1.10
```

![Vérification IP et ping AD](Phishing/Check_IP_Kali_Ping_AD.png)

### Mise à jour des paquets Kali
Avant de continuer, j’ai mis à jour les paquets du système afin de partir sur un environnement propre et à jour.

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

Cette étape permet de mettre à jour la liste des paquets, d’appliquer les correctifs disponibles et de supprimer les paquets devenus inutiles.

![Mise à jour des paquets Kali](Phishing/MAJ_Installation_Paquet_Remove_Vieux_Paquets.png)

## 2. Extraction des utilisateurs AD

Sur le contrôleur de domaine, j’ai exporté les utilisateurs dans un CSV compatible GoPhish.

```powershell
"First Name,Last Name,Email,Position`n" | Out-File "$env:USERPROFILE\Desktop\Gophish_CELDUC.csv" -Encoding UTF8
Get-ADUser -Filter "givenName -like '*' -and sn -like '*'" -Properties givenName,sn,Department |
Select-Object @{n='First Name';e={$_.givenName}},@{n='Last Name';e={$_.sn}},@{n='Email';e={"$($_.SAMAccountName)@celduc.com"}},@{n='Position';e={$_.Department}} |
Export-Csv -Path "$env:USERPROFILE\Desktop\temp.csv" -NoTypeInformation -Encoding UTF8
Get-Content "$env:USERPROFILE\Desktop\temp.csv" | Select-Object -Skip 1 | Add-Content "$env:USERPROFILE\Desktop\Gophish_CELDUC.csv"
Remove-Item "$env:USERPROFILE\Desktop\temp.csv"
```

Le fichier obtenu contient les utilisateurs du domaine dans un format directement réutilisable dans GoPhish.

![Exportation liste utilisateurs AD](Phishing/Exportation_Liste_User_Email_AD.PNG)

## 3. Installation et configuration de GoPhish

J’ai téléchargé et décompressé la version Linux de GoPhish dans `/opt`.

```bash
cd /opt
sudo wget https://github.com/gophish/gophish/releases/download/v0.12.1/gophish-v0.12.1-linux-64bit.zip
sudo unzip gophish-v0.12.1-linux-64bit.zip
cd gophish
sudo chmod +x gophish
sudo ./gophish
```

![Téléchargement et décompression GoPhish](Phishing/dowload_gophish_zip_decompresse.png)

![Rendre GoPhish exécutable](Phishing/Check_gophish_rendre_Executable_lancer_gophish.png)

### Premier lancement de GoPhish
J’ai lancé GoPhish pour la première fois afin de récupérer les identifiants initiaux de l’interface d’administration.

```bash
sudo ./gophish
```

GoPhish affiche alors les informations de connexion de départ.  
J’ai ensuite modifié le mot de passe administrateur pour sécuriser l’accès à l’interface.

![Premier lancement GoPhish](Phishing/Prmeiere_login_Gophish.png)

![Premier lancement GoPhish](Phishing/premier_lancement_Gophish.png)

![Réinitialisation du mot de passe GoPhish](Phishing/Réinitialisation_Login_Gophish.png)

### Configuration du compte Gmail pour l’envoi des emails
Avant de configurer le profil SMTP dans GoPhish, j’ai préparé un compte Gmail dédié à l’envoi des emails de campagne.

Ce compte servait de compte expéditeur pour le `Sending Profile` de GoPhish.

#### Activation de la vérification en deux étapes
J’ai d’abord activé la vérification en deux étapes sur le compte Gmail afin de sécuriser l’accès et de pouvoir générer un mot de passe d’application.

![Activation 2FA Gmail](Phishing/Activation_2FA_Gmail.png)

#### Génération du mot de passe d’application
Une fois la vérification en deux étapes activée, j’ai créé un mot de passe d’application spécifique pour GoPhish.

J’ai donné un nom explicite à l’application pour identifier facilement ce mot de passe dans la configuration Gmail.

![Nom de l’application GoPhish](Phishing/nom_appli_Gophish.png)

Gmail a ensuite généré un mot de passe d’application que j’ai utilisé dans la configuration SMTP de GoPhish.

![Mot de passe application GoPhish Gmail](Phishing/password_appli_Gophish_Gmail.png)

### Configuration réseau
J’ai ouvert le fichier `config.json` situé dans `/etc/gophish/`, puis j’ai modifié les paramètres d’écoute de GoPhish pour l’adapter à mon réseau local.

Pour cela, j’ai utilisé l’éditeur `nano` :

```bash
sudo nano /etc/gophish/config.json
```

J’ai ensuite :
- configuré l’interface d’administration sur `0.0.0.0:3333` afin de pouvoir y accéder depuis le réseau local ;
- conservé l’interface d’administration en TLS pour sécuriser l’accès ;
- configuré le serveur de phishing sur `0.0.0.0:80` pour le rendre accessible depuis les postes cibles ;
- laissé la base de données en SQLite avec le chemin par défaut de GoPhish.

Le fichier de configuration utilisé est le suivant :

```json
{
  "admin_server": {
    "listen_url": "0.0.0.0:3333",
    "use_tls": true,
    "cert_path": "/var/lib/gophish/gophish_admin.crt",
    "key_path": "/var/lib/gophish/gophish_admin.key",
    "trusted_origins": []
  },
  "phish_server": {
    "listen_url": "0.0.0.0:80",
    "use_tls": false
  },
  "db_name": "sqlite3",
  "db_path": "/var/lib/gophish/gophish.db"
}
```

Le choix de `0.0.0.0` permet à GoPhish d’écouter sur toutes les interfaces réseau de la machine Kali, ce qui rend l’interface d’administration et le serveur de phishing accessibles depuis le LAN.

![Vérification fichier config.json](Phishing/Conf_Fichier_config_json.png)

Après cette modification, j’ai redémarré GoPhish puis vérifié que les ports 3333 et 80 étaient bien en écoute.

```bash
sudo systemctl restart gophish
sudo netstat -tlnp | grep -E "3333|80"
```

![Vérification ports 3333 et 80](Phishing/Verif_Port_3333_80.png)

## 4. Serveur Python et page de sensibilisation

J’ai placé le fichier `sensibilisation.html` dans mon dossier de travail, puis j’ai lancé un serveur HTTP simple avec Python.

```bash
cd /home/jiji
sudo python3 -m http.server 8080 --bind 0.0.0.0
```

Le paramètre `--bind 0.0.0.0` permet d’écouter sur toutes les interfaces réseau.  
Cela rend la page accessible depuis le réseau local, et pas seulement depuis la machine Kali elle-même.

![Création serveur page sensibilisation](Phishing/Creation_server_heberge_page_sensibilisation_html.png)

![Lancement serveur Python](Phishing/lancement_server.png)

![Extraction fichier sensibilisation](Phishing/extrait_fichier_sensibilisation_html.png)

L’URL utilisée pour la page de sensibilisation est la suivante :

```text
http://192.168.1.198:8080/sensibilisation.html
```

## 5. Configuration de la campagne

Dans GoPhish, j’ai créé une landing page qui enregistre l’interaction de l’utilisateur avant de le rediriger vers la page de sensibilisation.

J’ai ensuite :
- importé le CSV des utilisateurs au format attendu par GoPhish ;
- sélectionné le profil SMTP ;
- sélectionné le template email ;
- choisi la landing page ;
- lancé d’abord un test, puis la campagne complète.

![Importation CSV dans Kali](Phishing/Importation_Fichier_CSV_User_AD_VM_Kali.png)

![Importation du CSV dans GoPhish](Phishing/Importation_fichier_csv_userAD_dans_Gophish.png)

![Importation CSV réussie](Phishing/Importation_fichier_csv_userAD_dans_Gophish_OK.png)

![Configuration landing page sensibilisation](Phishing/Conf_Landpage_Sensibilisation_HTML.png)

![Configuration landing page Outlook](Phishing/Conf_Landpage_outlook_HTML.png)

![Template email](Phishing/new_email_template.png)

![Profil d’envoi OK](Phishing/Sending_profile_OK.png)

![Configuration test campagne](Phishing/Conf_Test_Campagne_Phishing.png)

## 6. Flux utilisateur complet

1. L’utilisateur reçoit l’email.
2. Il clique sur le lien GoPhish.
3. Il arrive sur la fausse page de connexion.
4. GoPhish capture la saisie.
5. L’utilisateur est redirigé vers la page de sensibilisation.

![Email reçu](Phishing/Email_Test_Campagne_Recu.png)

![Email de test OK](Phishing/Email_Test_recu_OK.png)

![Email faux login](Phishing/Email_Test_Campagne_Fake_Login.png)

![Page de login fake](Phishing/resultat_landpage_outlook_Login_Fake.png)

![Redirection sensibilisation](Phishing/Redirection_Sensibilisation_%20apres_Fake_Login.png)

![Redirection vers site de sensibilisation](Phishing/Redirection_Sensibilisation_Cybermalveillance_gouv_fr.png)

![Résultat final campagne](Phishing/Resultat_Final_Test_Campagne.png)

## 7. Commandes de secours

Si un service ne répond plus, j’utilise les commandes suivantes :

```bash
sudo systemctl restart gophish
sudo pkill python3
cd /home/jiji && sudo python3 -m http.server 8080 --bind 0.0.0.0
```

## 8. Nettoyage

Après la campagne, j’arrête les services et j’archive les résultats.

```bash
sudo systemctl stop gophish
sudo pkill python3
```

## Captures d’écran

Le dossier `Phishing/` contient toutes les captures utilisées pour documenter chaque étape :
- vérification des hashes,
- installation de Kali,
- installation de GoPhish,
- configuration des landing pages,
- import CSV,
- envoi des emails,
- page de sensibilisation,
- tableau de bord et résultats.
```
