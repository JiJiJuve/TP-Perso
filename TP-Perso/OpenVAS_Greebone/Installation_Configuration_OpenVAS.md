# Installation et configuration d’OpenVAS / Greenbone

## Sommaire
- [Introduction](#introduction)
- [Schéma de principe](#schéma-de-principe)
- [Préparation de la VM](#préparation-de-la-vm)
- [Installation et activation de SSH](#installation-et-activation-de-ssh)
- [Connexion SSH et changement de VM](#connexion-ssh-et-changement-de-vm)
- [Configuration d’une IP fixe](#configuration-dune-ip-fixe)
- [Installation de GVM / OpenVAS](#installation-de-gvm--openvas)
- [Vérification des services](#vérification-des-services)
- [Synchronisation des feeds](#synchronisation-des-feeds)
- [Accès à l’interface web](#accès-à-linterface-web)
- [Premier scan](#premier-scan)
- [Exploitation des résultats](#exploitation-des-résultats)
- [CVE et CVSS](#cve-et-cvss)
- [Plan de remédiation](#plan-de-remédiation)
- [Accès LAN à l’interface Greenbone](#accès-lan-à-linterface-greenbone)
- [Transfert des rapports](#transfert-des-rapports)
- [Conclusion](#conclusion)

## Introduction

Ce document présente l’installation et la configuration de **Greenbone Vulnerability Management (GVM) / OpenVAS** sur une machine Kali Linux. L’objectif est de mettre en place un environnement de scan de vulnérabilités, de vérifier son fonctionnement, d’interpréter les résultats obtenus et de préparer un plan de correction adapté.

OpenVAS est le moteur de scan de l’écosystème Greenbone. Il s’appuie sur des feeds de vulnérabilités pour détecter des failles connues sur des machines du réseau.

## Schéma de principe

Le schéma ci-dessous présente le fonctionnement général d’OpenVAS / Greenbone :

![Schéma de principe OpenVAS](Images/schema_principe_OpenVAS.png)

## Préparation de la VM

Avant de commencer, il est important de s’assurer que la VM est correctement préparée, avec un utilisateur administrateur, un accès réseau fonctionnel et une structure de travail claire.

### Vérification des droits administrateur

Après l’installation de Kali, vérifier que l’utilisateur possède bien les droits nécessaires :

```bash
sudo whoami
sudo -i
sudo passwd root
```

Si la commande `sudo whoami` répond `root`, les droits sont corrects. Sur Kali récent, l’usage recommandé reste celui d’un utilisateur standard avec `sudo`.

![Vérification des droits root](Images/Verif_droits_root_vm_kali.png)

### Installation et activation de SSH

Si SSH n’a pas été installé pendant la mise en place de la VM, il peut être ajouté ensuite :

```bash
sudo apt update
sudo apt install openssh-server -y
sudo systemctl enable --now ssh
sudo systemctl status ssh
```

Le service doit apparaître en `active (running)` et `enabled`.

```bash
ssh ton_user@IP_DE_LA_VM
```

![Statut SSH en cours d’exécution](Images/Verif_statut_ssh_running.png)

## Connexion SSH et changement de VM

Si une VM est recréée avec la même adresse IP, le client SSH peut détecter une différence de clé d’hôte. Dans ce cas, il faut supprimer l’ancienne entrée connue pour cette IP.

```bash
ssh-keygen -R 192.168.1.XXX
ssh celduc@192.168.1.XXX
```

Une autre méthode consiste à supprimer manuellement la ligne correspondante dans le fichier `known_hosts` du poste client.

## Configuration d’une IP fixe

Pour une VM, il est pratique d’utiliser une IP fixe afin de retrouver facilement la machine en SSH et pour l’accès à l’interface web.

### Méthode graphique

- Ouvrir les paramètres réseau.
- Aller dans l’onglet IPv4.
- Passer de `Automatique (DHCP)` à `Manuel`.
- Renseigner l’adresse IP, le préfixe, la passerelle et les DNS.
- Enregistrer puis redémarrer la connexion.

### Méthode CLI

```bash
nmcli con show
nmcli con mod "NOM_DE_LA_CONNEXION" ipv4.addresses 192.168.1.XXX/24
nmcli con mod "NOM_DE_LA_CONNEXION" ipv4.gateway 192.168.1.XXX
nmcli con mod "NOM_DE_LA_CONNEXION" ipv4.dns "1.1.1.1 8.8.8.8"
nmcli con mod "NOM_DE_LA_CONNEXION" ipv4.method manual
nmcli con down "NOM_DE_LA_CONNEXION"
nmcli con up "NOM_DE_LA_CONNEXION"
ip a
ip route
```

## Installation de GVM / OpenVAS

Une fois la VM prête, installer GVM :

```bash
sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y
sudo apt install gvm -y
sudo gvm-setup
sudo gvm-check-setup
sudo gvm-start
```

Ces commandes installent GVM/OpenVAS, initialisent l’environnement, vérifient que tout est correctement configuré, puis démarrent les services nécessaires à l’utilisation de l’interface web et du scanner.

![Initialisation GVM](Images/initialise_GVM_cr%C3%A9ation_configuration_de_base_%26_t%C3%A9l%C3%A9charge_feeds.png)

![Extrait gvm-start](Images/Extrait_gmv_start.png)

## Vérification des services

Après l’installation, il faut vérifier que les services essentiels sont bien démarrés :

```bash
systemctl status redis
systemctl status postgresql
systemctl status gvmd
systemctl status ospd-openvas
systemctl status gsad
```

Les services attendus sont généralement :

- `redis` : `active (running)`
- `gvmd` : `active (running)`
- `ospd-openvas` : `active (running)`
- `gsad` : `active (running)`
- `postgresql` : disponible pour `gvmd`

![Extrait Status Redis](Images/Extrait_Status_redis.png)

## Synchronisation des feeds

Lors du premier lancement, les feeds de vulnérabilités sont normalement téléchargés et importés automatiquement pendant l’initialisation de GVM. Dans mon cas, la synchronisation est restée bloquée, j’ai donc dû relancer manuellement la mise à jour des feeds pour finaliser l’installation.

```bash
greenbone-nvt-sync
greenbone-scapdata-sync
greenbone-certdata-sync
greenbone-feed-sync --type GVMD_DATA
```

Ces feeds n’apportent pas tous la même chose :

- **NVT** : tests de vulnérabilité réseau.
- **SCAP** : données de conformité et de vulnérabilités.
- **CERT** : références et alertes de sécurité.
- **GVMD_DATA** : configurations et données de gestion utilisées par `gvmd`.

Pour suivre l’avancement :

```bash
ps ax | grep greenbone
ps ax | grep -E 'gvmd|ospd-openvas|openvas|scap|cert|nvt|postgres'
top
sudo journalctl -u gvmd -f
```

## Accès à l’interface web

Une fois l’installation validée et les services lancés, l’interface web est accessible dans la VM à :

```text
https://127.0.0.1:9392
```

Lors de la connexion :

- Identifiant : `admin`
- Mot de passe : celui généré pendant `gvm-setup`

![Creation_User_Password_Openvas](Images/Creation_User_Password_Openvas.png)

![Connexion première fois](Images/Connexion_prmeiere_fois_openvas_gui.png)

## Premier scan

Une fois l’interface disponible, il est possible de créer une cible, lancer un scan et analyser les premiers résultats.

![Premier scan](Images/1ie_scan_test_vm_openvas.png)

![Résultats du scan](Images/resultats_1ier_scan_test_vm_openvas.png)

## Exploitation des résultats

Le rapport de scan peut être exporté en PDF ou CSV. Le fichier CSV est particulièrement utile pour trier les vulnérabilités, filtrer les niveaux de gravité et préparer un plan de remédiation.

### 1. Vérifier l’emplacement du rapport

Dans Kali, rechercher le rapport téléchargé :

```
find "/home/celduc/Téléchargements" -type f -iname "*openvas*"
```

Vérifier ensuite ses droits et son nom exact :

```
ls -lh "/home/celduc/Téléchargements/rapport_openvas_02_09_26.pdf"
```

### 2. Copier le rapport dans le dossier personnel (facultatif)

Pour simplifier le transfert, copier le fichier directement dans `/home/celduc/` :

```
cp "/home/celduc/Téléchargements/rapport_openvas_02_09_26.pdf" "/home/celduc/"
```

Cette étape évite les problèmes liés aux caractères accentués du dossier `Téléchargements`.

### 3. Transférer le fichier vers Windows

Depuis **PowerShell sur le PC local**, et non depuis la session SSH déjà ouverte, exécuter :

```
scp "celduc@192.168.1.129:/home/celduc/rapport_openvas_02_09_26.pdf" "$HOME\Downloads\"
```

Le mot de passe demandé est celui de l’utilisateur Kali `celduc`.

Le fichier sera copié dans le dossier **Téléchargements** de Windows. La commande `scp` utilise la connexion SSH pour transférer un fichier entre la VM et l’ordinateur local.


![Transfert du rapport](Images/Importation_resultats_scan_depuis_vm_vers_local.png)

## CVE et CVSS

Une **CVE** (*Common Vulnerabilities and Exposures*) est un identifiant standard attribué à une vulnérabilité connue.  
Le **CVSS** (*Common Vulnerability Scoring System*) mesure sa gravité technique sur une échelle de 0 à 10.

### Exemple

```
CVE-2024-12345 — CVSS : 9,8 — Critique
```

Cela signifie :

- `CVE-2024-12345` : identifiant de la vulnérabilité ;
- `9,8` : score de gravité très élevé ;
- `Critique` : vulnérabilité à examiner et à traiter en priorité.

Le score CVSS ne doit toutefois pas être utilisé seul pour décider de l’ordre des corrections. Il faut aussi prendre en compte l’exposition du service, la présence d’un exploit connu, le nombre de machines concernées et l’importance de l’équipement.

![Résultat OpenCVE](Images/OpenCVE_Resultat_%26_Description_CVE.png)

![Référence OpenCVE](Images/_Depuis_Reference_OpenCVE.png)


## Filtrer les vulnérabilités prioritaires

Dans la colonne **Severity** :

1.  Cliquer sur la flèche du filtre.
    
2.  Désélectionner **Tout sélectionner**.
    
3.  Sélectionner :
    
    - **Critical** ;
    - puis **High**.
  
![Extrait tableau CSV résultats scan OpenVAS](Images/Etrait_Tableau_CSV_resulats_Scan_OpenVAS2.png)

## Accès LAN à l’interface Greenbone

Par défaut, `gsad` écoute en local sur `127.0.0.1`. Pour rendre l’interface accessible depuis le LAN, il faut modifier le service.


### Procédure

1. Créer un snapshot VMware.
2. Ouvrir une session SSH sur la VM.
3. Sauvegarder le fichier de service.
4. Modifier la ligne `ExecStart`.
5. Recharger `systemd`.
6. Redémarrer le service.
7. Vérifier l’état.
8. Tester depuis une autre machine du LAN.

### Fichier de service

```bash
/usr/lib/systemd/system/gsad.service
```

### Sauvegarde

```bash
cp /usr/lib/systemd/system/gsad.service /usr/lib/systemd/system/gsad.service.bak
```

### Modification

```bash
nano /usr/lib/systemd/system/gsad.service
```

Ligne à utiliser :

```ini
ExecStart=/usr/sbin/gsad --foreground --listen 0.0.0.0 --port 9392 --no-redirect
```

### Recharge et redémarrage

```bash
systemctl daemon-reload
systemctl restart greenbone-security-assistant
systemctl status greenbone-security-assistant
```

### Test LAN

Depuis une autre machine du réseau local :

```text
https://192.168.1.XXX:9392
```

![Modification GSAD](Images/Recharge_systemd_redemarrage_service_verif_etat.png)

![Connexion LAN OK](Images/Connexion_OK_depuis_PC_LAN.png)

## Conclusion

Ce TP a permis de mettre en place un environnement complet de scan de vulnérabilités avec GVM / OpenVAS, de vérifier son bon fonctionnement, d’exécuter un premier audit, puis d’exploiter les résultats pour préparer un plan de correction. L’ensemble de la démarche illustre la logique d’un processus de gestion de vulnérabilités : détection, qualification, priorisation et remédiation.
