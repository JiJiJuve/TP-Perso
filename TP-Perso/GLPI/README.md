# Installation de GLPI 11 sur Debian

Ce guide décrit l’installation de GLPI 11 sur une VM Debian (serveur web Apache, PHP‑FPM et base MariaDB), ainsi que la mise en place de la configuration minimale pour accéder à l’interface web et commencer à gérer le parc informatique.  
Il est pensé pour un **lab pédagogique** reproduisant une petite infrastructure d’entreprise (gestion de parc, tickets, demandes utilisateurs).

> 📄 Fiche synthèse : [GLPI – Installation et configuration](Installation-configuration-GLPI.md)
---

## Sommaire

- [1. Prérequis du lab](#1-prérequis-du-lab)
- [2. Rappels sur GLPI](#2-rappels-sur-glpi)
- [3. Vérification de l’intégrité des ISO (hash)](#3-vérification-de-lintégrité-des-iso-hash)
- [4. Préparation : utilisateur sudo et SSH](#4-préparation--utilisateur-sudo-et-ssh)
- [5. Installation des paquets nécessaires (LAMP + PHP-FPM)](#5-installation-des-paquets-nécessaires-lamp--php-fpm)
- [6. Préparation de la base de données MariaDB](#6-préparation-de-la-base-de-données-mariadb)
- [7. Téléchargement et installation de GLPI](#7-téléchargement-et-installation-de-glpi)
- [8. Configuration d’Apache et de PHP-FPM (VirtualHost GLPI)](#8-configuration-dapache-et-de-php-fpm-virtualhost-glpi)
- [9. Installation de GLPI via l’interface web](#9-installation-de-glpi-via-linterface-web)
- [10. Sécurisation rapide de l’instance](#10-sécurisation-rapide-de-linstance)

---

## 1. Prérequis du lab

- 1 VM **Debian 13** (ou 12), 2 vCPU, 2–4 Go de RAM, 20 Go de disque.  
- Accès réseau (IP fixe ou réservation DHCP) et accès Internet pour télécharger les paquets.  
- Poste client sur le même réseau (navigateur web + client SSH).  
- Droits administrateur (sudo) sur la VM Debian.

---

## 2. Rappels sur GLPI

GLPI est une application web open‑source de **gestion de parc** et de **helpdesk**.  
Elle permet notamment :

- L’inventaire des postes et équipements.  
- La gestion des tickets d’incidents et demandes.  
- Le suivi du parc (matériel, licences, contrats, etc.).  

Dans ce TP, GLPI servira d’**application centrale de gestion du parc et des tickets**.

---

## 3. Vérification de l’intégrité des ISO (hash)

Objectif : vérifier l’authenticité des ISO utilisées (Debian, Windows Server) avant installation.

![Vérification du hash ISO Debian](images/verif_hash_iso_debian_13-1-0.png)  
![Hash attendu ISO Debian](images/hash_iso_debian_13-1-0.png)  

![Vérification du hash ISO Windows Server](images/verif_hash_iso_WindServer25.png)  
![Hash attendu ISO Windows Server](images/hash_iso_26100.32230.260111-0550.lt_release_svc_refresh_SERVER_EVAL_x64FRE_fr-fr.iso.png)  

---

## 4. Préparation : utilisateur sudo et SSH

Objectif : ne pas travailler en root et pouvoir administrer la VM à distance.

- Installation de `sudo` et ajout de l’utilisateur au groupe `sudo`.  
- Installation et activation du serveur SSH (`openssh-server`).  
- Vérification de l’accès SSH et des droits sudo.

![Donner les droits sudo et installer OpenSSH](images/donne_droit_user_installation_oppenssh.png)  
![Connexion SSH depuis le PC hôte](images/connexion_ssh_depuis_pc_hote.png)  
![Vérification de SSH](images/verif_ssh.png)  

---

## 5. Installation des paquets nécessaires (LAMP + PHP-FPM)

Objectif : installer le serveur web Apache, la base MariaDB, PHP, PHP‑FPM et les extensions utiles à GLPI.

- Mise à jour du système (`apt update && apt upgrade`).  
- Installation d’Apache, MariaDB et PHP de base.  
- Installation de PHP‑FPM et des modules PHP requis par GLPI.

![Mise à jour du serveur Debian](images/maj_server_debian.png)  
![Installation du LAMP](images/installation_LAMP.png)  
![Installation des dépendances PHP](images/installation_dependances_php.png)  
![Installation de la gestion des processus PHP (PHP-FPM)](images/installation_gestio_processus_php.png)  

---

## 6. Préparation de la base de données MariaDB

Objectif : créer une base dédiée à GLPI + un utilisateur SQL avec les droits dessus.

- Création de la base `glpi_npt`.  
- Création de l’utilisateur SQL `neptunet_glpi` avec un mot de passe dédié.  
- Attribution de tous les privilèges sur la base GLPI.

![Création de la base et de l’utilisateur MariaDB](images/creation_base_donnée_mariadb_utilisateur_motpass.png)  

---

## 7. Téléchargement et installation de GLPI

Objectif : télécharger l’archive GLPI, la décompresser dans `/var/www/html` et mettre les bons droits.

- Téléchargement de l’archive GLPI (ex. 11.0.5) dans `/tmp`.  
- Décompression vers `/var/www/html`.  
- Changement de propriétaire sur `/var/www/html/glpi` vers `www-data`.

![Téléchargement de la dernière version de GLPI](images/dowload_last_version_glpi.png)  
![Décompression de l’archive GLPI](images/decompression_archive_glpi.png)  
![www-data propriétaire des fichiers GLPI](images/utilisateur_services_web_proprietaire_new_files.png)  

---

## 8. Configuration d’Apache et de PHP-FPM (VirtualHost GLPI)

Objectif : créer un VirtualHost propre pour GLPI, lier Apache à PHP‑FPM, et activer les bons modules.

- Vérification de la version PHP (`php -v`) pour identifier le socket PHP‑FPM.  
- Création du fichier `/etc/apache2/sites-available/glpi.conf` avec `DocumentRoot /var/www/html/glpi/public`.  
- Activation des modules nécessaires (`proxy_fcgi`, `rewrite`), de la conf PHP‑FPM et du vhost GLPI.

![Vérification de la version de PHP](images/verif_version_php.png)  
![Création du VirtualHost GLPI](images/creation_fichier_virtualhost_glpi.png)  
![VirtualHost GLPI dans Apache](images/virtualhost_glpi.png)  
![Activation des modules PHP pour Apache](images/activation_modules_php_apache.png)  

---

## 9. Installation de GLPI via l’interface web

Objectif : finaliser l’installation avec le navigateur (tests prérequis, connexion DB, création des tables).

- Accès à `http://192.168.1.47/` ou `http://glpi_tp/`.  
- Vérification des prérequis PHP/permissions.  
- Saisie des informations de base de données (serveur `localhost`, base `glpi_npt`, utilisateur `neptunet_glpi`).  
- Création des tables et première connexion avec le compte `glpi/glpi`.

![Accès à l’installation GLPI (1)](images/acces_installation_glpi_GUI.png)  
![Accès à l’installation GLPI (2)](images/acces_installation_glpi_GUI2.png)  
![Accès à l’installation GLPI (3)](images/acces_installation_glpi_GUI3.png)  
![Accès à l’installation GLPI (4)](images/acces_installation_glpi_GUI4.png)  
![Accès à l’installation GLPI (5)](images/acces_installation_glpi_GUI5.png)  
![Accès à l’installation GLPI (6)](images/acces_installation_glpi_GUI6.png)  
![Accès à l’installation GLPI (7)](images/acces_installation_glpi_GUI7.png)  

![Connexion par défaut glpi/glpi](images/connexion_defaut_glpi_glpi.png)  
![Tableau de bord de GLPI](images/tableau_bord_glpi.png)  

---

## 10. Sécurisation rapide de l’instance

Après l’installation :

- Changer les mots de passe des comptes par défaut (`glpi`, `tech`, `normal`, `post-only`).  
- Supprimer le répertoire d’installation :  
  ```bash
  sudo rm -rf /var/www/html/glpi/install
  ```  
- Mettre en place des sauvegardes régulières de la base GLPI et du répertoire applicatif.
```

Ça reprend exactement la logique de ta fiche AD‑DS :  
- Titre / intro / lien fiche synthèse  
- Sommaire cliquable  
- Sections numérotées avec texte + captures.  

