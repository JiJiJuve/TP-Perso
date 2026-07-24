# Zabbix Infrastructure Monitoring & Ansible

## Supervision centralisée et automatisation du déploiement

---

## 1. Présentation du projet

Ce projet présente la mise en place d'une infrastructure de supervision centralisée basée sur **Zabbix**, associée à l'automatisation de l'administration système avec **Ansible**.

L'infrastructure permet de superviser différents composants d'un environnement informatique tout en automatisant le déploiement et la configuration des agents de supervision.

La solution associe notamment :

* Zabbix ;
* Ansible ;
* Active Directory ;
* les GPO ;
* WinRM ;
* Zabbix Agent 2 ;
* l'API Zabbix ;
* SNMPv3.

---

## 2. Objectifs

Les principaux objectifs du projet sont les suivants :

* mettre en place un serveur Zabbix sur Debian 13 ;
* superviser les serveurs Windows avec Zabbix Agent 2 ;
* superviser un serveur Linux utilisé comme contrôleur Ansible ;
* automatiser le déploiement des agents avec Ansible ;
* préparer les serveurs Windows avec Active Directory et les GPO ;
* utiliser WinRM pour l'administration distante ;
* protéger les informations sensibles avec Ansible Vault ;
* créer et mettre à jour automatiquement les hôtes dans Zabbix via son API ;
* superviser un équipement réseau FortiGate avec SNMPv3 ;
* exploiter les métriques, les événements et les alertes générés par Zabbix.

---

## 3. Architecture globale

L'architecture repose sur quatre composants principaux :

* un serveur Zabbix central ;
* un contrôleur Ansible ;
* des serveurs Windows équipés de Zabbix Agent 2 ;
* un FortiGate supervisé avec SNMPv3.

```text
                         ┌────────────────────────────┐
                         │     Active Directory        │
                         │                            │
                         │  GPO                       │
                         │  ├─ Configuration WinRM    │
                         │  └─ Droits du compte        │
                         │     d'administration        │
                         └─────────────┬──────────────┘
                                       │
                                       │ TCP 5985
                                       │ WinRM / NTLM
                                       ▼
┌────────────────────────────┐   ┌────────────────────────────┐
│     Contrôleur Ansible      │   │      Serveurs Windows       │
│                            │   │                            │
│ Debian 13                  │──▶│ Zabbix Agent 2              │
│                            │   │                            │
│ Ansible                    │   │ Contrôleurs de domaine      │
│ Ansible Vault              │   │ Serveurs applicatifs        │
│ API Zabbix                 │   │ Serveurs de données          │
└──────────────┬─────────────┘   └─────────────┬──────────────┘
               │                               │
               │                               │ TCP 10050
               │                               │
               └───────────────┬───────────────┘
                               ▼
                   ┌────────────────────────────┐
                   │       Serveur Zabbix        │
                   │                            │
                   │ Debian 13                  │
                   │ Zabbix Server              │
                   │ MariaDB                    │
                   │ Apache2                    │
                   │ PHP-FPM                    │
                   │                            │
                   │ Supervision centralisée    │
                   └─────────────┬──────────────┘
                                 │
                                 │ SNMPv3
                                 │ UDP 161
                                 ▼
                       ┌──────────────────────┐
                       │       FortiGate        │
                       │                      │
                       │       SNMPv3         │
                       │       authPriv        │
                       │       SHA + AES       │
                       └──────────────────────┘
```

### Flux principaux

| Flux                                  | Protocole        | Utilisation                            |
| ------------------------------------- | ---------------- | -------------------------------------- |
| Contrôleur Ansible → Serveurs Windows | WinRM / TCP 5985 | Administration distante et déploiement |
| Serveur Zabbix → Agents               | TCP 10050        | Collecte des métriques                 |
| Serveur Zabbix → FortiGate            | SNMPv3 / UDP 161 | Supervision de l'équipement réseau     |
| Ansible → Serveur Zabbix              | API HTTP         | Création et mise à jour des hôtes      |

---

## 4. Rôles des composants

### Serveur Zabbix

Le serveur Zabbix constitue le point central de l'infrastructure de supervision.

Il assure notamment :

* la collecte des données ;
* l'analyse des métriques ;
* la gestion des templates ;
* la génération des problèmes et alertes ;
* la conservation des historiques ;
* la visualisation des données ;
* la supervision des agents Zabbix ;
* la supervision SNMP des équipements réseau.

---

### Contrôleur Ansible

Le contrôleur Ansible est utilisé pour automatiser l'administration des serveurs Windows.

Il permet notamment :

* d'exécuter les playbooks ;
* de gérer l'inventaire des serveurs ;
* de protéger les informations sensibles avec Ansible Vault ;
* de déployer Zabbix Agent 2 ;
* de configurer les services Windows ;
* de configurer le pare-feu ;
* d'interagir avec l'API Zabbix.

Le contrôleur Ansible est lui-même supervisé par le serveur Zabbix.

---

### Serveurs Windows

Les serveurs Windows sont supervisés à l'aide de **Zabbix Agent 2**.

La supervision permet notamment de suivre :

* l'utilisation du processeur ;
* la mémoire ;
* l'espace disque ;
* les interfaces réseau ;
* les processus ;
* les services Windows ;
* les performances système ;
* la disponibilité des serveurs.

---

### FortiGate

Le FortiGate est supervisé via **SNMPv3**.

La configuration utilise :

```text
Niveau de sécurité : authPriv
Authentification   : SHA
Chiffrement        : AES
```

Cette méthode permet de superviser les informations système et les métriques exposées par l'équipement via SNMP.

---

# Sommaire

* [1. Préparation de la machine virtuelle](#1-préparation-de-la-machine-virtuelle)
* [2. Installation et configuration de Debian](#2-installation-et-configuration-de-debian)
* [3. Installation du serveur Zabbix](#3-installation-du-serveur-zabbix)
* [4. Configuration de MariaDB](#4-configuration-de-mariadb)
* [5. Configuration d'Apache et PHP-FPM](#5-configuration-dapache-et-php-fpm)
* [6. Première connexion à l'interface Zabbix](#6-première-connexion-à-linterface-zabbix)
* [7. Préparation des serveurs Windows avec Active Directory et GPO](#7-préparation-des-serveurs-windows-avec-active-directory-et-gpo)
* [8. Configuration de WinRM](#8-configuration-de-winrm)
* [9. Déploiement de Zabbix Agent 2 avec Ansible](#9-déploiement-de-zabbix-agent-2-avec-ansible)
* [10. Protection des secrets avec Ansible Vault](#10-protection-des-secrets-avec-ansible-vault)
* [11. Création automatique des hôtes via l'API Zabbix](#11-création-automatique-des-hôtes-via-lapi-zabbix)
* [12. Déploiement sur plusieurs serveurs Windows](#12-déploiement-sur-plusieurs-serveurs-windows)
* [13. Cas particulier : Windows Server 2012 et PowerShell 3.0](#13-cas-particulier-windows-server-2012-et-powershell-30)
* [14. Déploiement sur les contrôleurs de domaine](#14-déploiement-sur-les-contrôleurs-de-domaine)
* [15. Supervision du contrôleur Ansible](#15-supervision-du-contrôleur-ansible)
* [16. Supervision du FortiGate avec SNMPv3](#16-supervision-du-fortigate-avec-snmpv3)
* [17. Exploitation de la supervision](#17-exploitation-de-la-supervision)
* [18. Bilan du projet](#18-bilan-du-projet)

---

# 1. Préparation de la machine virtuelle

La première étape du projet consiste à créer et préparer la machine virtuelle destinée à héberger le serveur Zabbix.

La machine virtuelle est déployée sous VMware et utilise Debian 13.

## 1.1 Configuration de la machine virtuelle

La machine virtuelle est créée avec une configuration adaptée à l'hébergement du serveur Zabbix.



La machine virtuelle constitue le socle de l'infrastructure de supervision.

---

## 1.2 Installation de Debian

Après la création de la machine virtuelle, Debian 13 est installé.

Une fois l'installation terminée, le système est mis à jour :

```bash
sudo apt update
sudo apt upgrade -y
```

---

## 1.3 Configuration du réseau

La machine utilise une adresse IP fixe afin de garantir la stabilité des communications avec les agents Zabbix et les équipements supervisés.

La configuration réseau est réalisée dans :

```text
/etc/network/interfaces
```

La configuration initiale utilise une adresse attribuée automatiquement par DHCP.

![Configuration réseau initiale avec DHCP](Images/fichier_conf_interfaces_Initial_ip_dhcp.png)

La configuration est ensuite modifiée afin d'utiliser une adresse IP statique.

![Configuration de l'adresse IP statique](Images/modification_fichier_conf_interfaces_ip_fixe.png)

La configuration finale utilisée est :

```text
Adresse IP : 192.168.1.230
Préfixe    : /24
Passerelle : 192.168.1.254
Interface  : ens192
```

La configuration réseau est séparée de la configuration DNS.

Le fichier :

```text
/etc/network/interfaces
```

est utilisé pour :

* l'adresse IP ;
* le préfixe réseau ;
* la passerelle ;
* la configuration de l'interface réseau.

Le fichier :

```text
/etc/resolv.conf
```

est utilisé pour la configuration du DNS.

![Configuration du DNS dans resolv.conf](Images/Configuration_fichier_resolv_conf_dns.png)

La configuration DNS permet notamment la résolution des noms nécessaires au fonctionnement de l'infrastructure.

---

## 1.4 Configuration du nom d'hôte

Le serveur est identifié dans l'infrastructure sous le nom :

```text
ZABBIX-SRV
```

Le nom d'hôte permet d'identifier clairement le serveur dans l'environnement réseau et dans les différents outils d'administration.

---

## 1.5 Installation de sudo

Le compte utilisateur utilisé pour l'administration du serveur est ajouté au groupe `sudo`.

Cette configuration permet d'exécuter des commandes nécessitant des privilèges administrateur sans utiliser directement le compte `root`.

![Ajout de l'utilisateur au groupe sudo](Images/installation_sudo_utilisateur_groupe_sudo.png)

---

## 1.6 Validation de la configuration

Une fois la configuration terminée, les éléments suivants sont vérifiés :

* l'adresse IP statique ;
* la passerelle ;
* la résolution DNS ;
* l'accès réseau ;
* le nom d'hôte ;
* les droits d'administration.

Le serveur est désormais prêt à recevoir les composants nécessaires à l'installation de Zabbix.

# 2. Installation du serveur Zabbix

Après la préparation de la machine Debian, les composants nécessaires au fonctionnement du serveur Zabbix sont installés.

L'architecture logicielle repose sur :

* le dépôt officiel Zabbix ;
* Zabbix Server ;
* Zabbix Frontend ;
* MariaDB ;
* Apache2 ;
* PHP-FPM.

---

## 2.1 Installation du dépôt officiel Zabbix

Le dépôt officiel Zabbix est installé afin de récupérer les paquets nécessaires à la version utilisée.

Le paquet du dépôt est téléchargé puis installé :

```bash
wget https://repo.zabbix.com/zabbix/7.4/release/debian/pool/main/z/zabbix-release/zabbix-release_latest+debian13_all.deb

sudo dpkg -i zabbix-release_latest+debian13_all.deb
```

Les dépôts sont ensuite actualisés :

```bash
sudo apt update
```

![Installation et mise à jour du dépôt Zabbix](Images/Installation_&_MaJ_paquets_depot_zabbix.png)

Le dépôt Zabbix est désormais disponible sur le système.

---

## 2.2 Installation de MariaDB

MariaDB est utilisé comme système de gestion de base de données pour stocker les données de supervision Zabbix.

Le serveur et le client MariaDB sont installés avec :

```bash
sudo apt install mariadb-server mariadb-client -y
```

![Installation de MariaDB](Images/extrait_Installation_server_MariaDB.png)

Le service est ensuite vérifié :

```bash
sudo systemctl status mariadb
```

Le service doit être actif :

```text
active (running)
```

![Vérification du service MariaDB](Images/Verification_apres_Installation_Server_Maria_Running.png)

---

## 2.3 Installation du serveur Zabbix et de ses composants

Les composants principaux de Zabbix sont installés avec :

```bash
sudo apt install \
zabbix-server-mysql \
zabbix-frontend-php \
zabbix-apache-conf \
zabbix-sql-scripts \
zabbix-agent2 \
-y
```

Ces paquets fournissent notamment :

| Composant             | Rôle                       |
| --------------------- | -------------------------- |
| `zabbix-server-mysql` | Serveur de supervision     |
| `zabbix-frontend-php` | Interface Web              |
| `zabbix-apache-conf`  | Configuration Apache       |
| `zabbix-sql-scripts`  | Schéma de base de données  |
| `zabbix-agent2`       | Agent local de supervision |

![Installation des composants Zabbix](Images/Extrait_Installation_composants_Zabbix.png)

---

## 2.4 Importation du schéma SQL Zabbix

Le paquet `zabbix-sql-scripts` fournit le schéma SQL nécessaire à la création de la structure de la base de données Zabbix.

Les fichiers installés par le paquet peuvent être vérifiés avec :

```bash
dpkg -L zabbix-sql-scripts
```

Le schéma MySQL/MariaDB utilisé par Zabbix se trouve notamment dans :

```text
/usr/share/zabbix-sql-scripts/mysql/server.sql.gz
```

Le schéma est compressé au format `gzip`.

Il est décompressé avec `zcat`, puis directement envoyé au client MariaDB afin d'être importé dans la base de données Zabbix :

```bash
zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | \
mariadb -uzabbix -p zabbix
```

Le mot de passe de l'utilisateur MariaDB `zabbix` est ensuite demandé.

![Importation du schéma SQL Zabbix](Images/Extrait_import_schema_SQL_Zabbix.png)

Une connexion directe à la base de données est ensuite effectuée afin de vérifier que l'utilisateur MariaDB `zabbix` peut y accéder correctement :

```bash
mariadb -uzabbix -p zabbix
```

Cette vérification confirme que :

* la base de données `zabbix` est accessible ;
* l'utilisateur MariaDB `zabbix` peut s'y connecter ;
* le schéma SQL Zabbix a bien été importé.


---

## 2.5 Configuration du serveur Zabbix

Le fichier de configuration principal du serveur Zabbix est :

```text
/etc/zabbix/zabbix_server.conf
```

Ce fichier contient notamment les paramètres nécessaires à la connexion du serveur Zabbix à la base de données MariaDB.

Le paramètre principal configuré est :

```text
DBPassword=<mot_de_passe_de_l_utilisateur_zabbix>
```

Le mot de passe utilisé correspond à celui défini précédemment pour l'utilisateur MariaDB :

```text
zabbix
```

Le fichier peut être édité avec :

```bash
sudo nano /etc/zabbix/zabbix_server.conf
```

![Configuration du fichier zabbix\_server.conf](Images/Extrait_fichier_zabbix_server_conf.png)

Cette configuration permet au processus `zabbix-server` de se connecter à la base de données `zabbix`.


---

## 2.6 Démarrage des services

Les services nécessaires au fonctionnement de la plateforme sont activés et démarrés :

```bash
sudo systemctl enable zabbix-server
sudo systemctl enable zabbix-agent2
sudo systemctl enable apache2
sudo systemctl enable mariadb
```

Les services peuvent ensuite être vérifiés :

```bash
systemctl status zabbix-server
systemctl status zabbix-agent2
systemctl status apache2
systemctl status mariadb
```

![Activation des services Zabbix](Images/extrait_Activation_Demarrage_Zabbix_Server.png)

---

## 2.7 Vérification des ports

Les ports utilisés par les différents composants sont vérifiés avec :

```bash
sudo ss -tulpn
```

Les principaux ports attendus sont :

| Port      | Service                       |
| --------- | ----------------------------- |
| TCP 80    | Apache / interface Web Zabbix |
| TCP 10050 | Zabbix Agent 2                |
| TCP 10051 | Zabbix Server                 |
| TCP 3306  | MariaDB                       |

La présence du service Web Apache peut également être vérifiée :

```bash
sudo ss -tulpn | grep :80
```

![Vérification du port 80 Apache](Images/Verification_Port_Ecoute_80_Apache.png)

La plateforme Zabbix est désormais installée et les services principaux sont opérationnels.

# 3. Configuration et première connexion à l'interface Zabbix

Une fois les composants du serveur installés et configurés, l'interface Web Zabbix est accessible depuis un navigateur.

L'installation finale est réalisée depuis l'interface Web.

---

## 3.1 Accès à l'interface Web

L'interface Zabbix est accessible à l'adresse :

```text
http://192.168.1.230/zabbix
```

La page d'installation de Zabbix est alors affichée.

---

## 3.2 Vérification des prérequis

L'installateur Web vérifie automatiquement les composants nécessaires au fonctionnement de Zabbix.

Les éléments contrôlés comprennent notamment :

* la version de PHP ;
* les extensions PHP nécessaires ;
* la configuration de PHP-FPM ;
* la configuration du fuseau horaire ;
* les composants nécessaires à l'accès à la base de données.

Les prérequis doivent être validés avant de poursuivre l'installation.

![Vérification des prérequis de l'interface Zabbix](Images/conf_gui_zabbix_verification_prerequis.png)

---

## 3.3 Configuration de la connexion à la base de données

L'interface Web demande ensuite les informations nécessaires pour se connecter à la base de données MariaDB.

Les paramètres utilisés sont :

```text
Type de base de données : MySQL
Serveur de base         : localhost
Port                    : 3306
Nom de la base           : zabbix
Utilisateur              : zabbix
Mot de passe             : mot de passe défini précédemment
```

Ces informations permettent à l'interface Web et au serveur Zabbix d'utiliser la base de données créée lors de l'installation.

---

## 3.4 Finalisation de l'installation

Après validation des paramètres, l'installateur termine la configuration de l'interface Zabbix.

La fin de l'installation est confirmée par l'affichage de la page de succès.

![Installation de Zabbix terminée](Images/felicitations_installation_zabbix_gui.png)

---

## 3.5 Première connexion

Une première connexion à l'interface Web est réalisée avec le compte administrateur initial :

```text
Utilisateur : Admin
Mot de passe : zabbix
```

![Première connexion à Zabbix](Images/1iere_connexion_zabbix_avec_Admin_password=zabbix.png)

Le mot de passe par défaut est ensuite modifié afin de sécuriser l'accès à l'interface d'administration.

![Modification du mot de passe par défaut](Images/Modification_Password_par_defaut_server_zabbix.png)

La plateforme Zabbix est désormais installée et accessible.

Le serveur est prêt à être configuré pour superviser les différents équipements et serveurs de l'infrastructure.


# 4. Validation opérationnelle du serveur Zabbix

Après l'installation et la configuration initiale, le fonctionnement général du serveur Zabbix est vérifié.

L'objectif est de confirmer que la plateforme est opérationnelle avant d'intégrer les premiers équipements et serveurs à superviser.

---

## 4.1 Vérification de la disponibilité du serveur Zabbix

Après l'installation et la configuration des composants, la disponibilité du serveur Zabbix est vérifiée depuis l'interface Web.

Dans le menu :

**Surveillance → Hôtes**

le serveur Zabbix apparaît avec son interface Zabbix disponible.

![Vérification de la disponibilité du serveur Zabbix](Images/Verification_Etat_Server_Zabbix_GUI.png)

L'indicateur **ZBX** apparaît en vert.

Cette vérification confirme que :

- l'agent Zabbix fonctionne sur le serveur ;
- le serveur Zabbix peut communiquer avec son agent ;
- la supervision du serveur Zabbix est opérationnelle.
---

## 4.2 Vérification des informations système

Les informations système du serveur Zabbix peuvent être consultées depuis l'interface d'administration.

Cette vue permet de vérifier les caractéristiques de l'environnement utilisé pour la supervision.

![Informations système du serveur Zabbix](Images/Verification_Info_Systeme_Server_Zabbix_GUI.png)

---

## 4.3 Vérification des services Web et base de données

Les services nécessaires au fonctionnement de l'interface Web et de la base de données sont vérifiés depuis le terminal.

Les services contrôlés sont :

- Apache2 ;
- MariaDB ;
- PHP-FPM.

La vérification est réalisée avec les commandes `systemctl status` correspondantes.

![Vérification des services de l'infrastructure](Images/verification_3services_running_glpi_apache2_mariadb_php_fpm.png)

Les trois services sont actifs et fonctionnels.

---

## 4.4 Première utilisation du tableau de bord

Après la validation de l'installation, le tableau de bord Zabbix est accessible.

Le dashboard permet de visualiser les informations principales de la plateforme de supervision.

![Dashboard Zabbix](Images/dashboard_zabbix.png)

Un tableau de bord personnalisé a également été créé afin de regrouper les informations utiles à la supervision de l'infrastructure.

![Dashboard personnalisé](Images/Dashboard_crée_par_moi_server_zabbix.png)

Le serveur Zabbix est désormais opérationnel et prêt à intégrer les premiers équipements et serveurs supervisés.


# 5. Première intégration manuelle d'un serveur Linux

Avant d'automatiser le déploiement de Zabbix Agent 2 sur les serveurs Windows avec Ansible, un premier serveur Linux est intégré manuellement à Zabbix.

Le serveur utilisé est le serveur GLPI.

Cette étape permet de valider le fonctionnement de la supervision d'un serveur Linux avant de passer à l'automatisation.

---

## 5.1 Vérification et installation de l'agent Zabbix

La disponibilité du paquet `zabbix-agent` est d'abord vérifiée avec :

```bash
apt policy zabbix-agent
```

![Vérification de la disponibilité du paquet Zabbix Agent](Images/verification_depot_zabbix_server_debian_glpi.png)

L'agent est ensuite installé manuellement :

```bash
sudo apt install zabbix-agent -y
```

Après l'installation, l'état du service est vérifié :

```bash
systemctl status zabbix-agent
```

Le service doit apparaître comme actif et fonctionnel.

![Installation et vérification de l'agent Zabbix](Images/Installation_&_Verification_depot_zabbix_agent.png)

---

## 5.2 Configuration de l'agent Zabbix

Le fichier de configuration utilisé est :

```text
/etc/zabbix/zabbix_agentd.conf
```

Le fichier est modifié manuellement avec :

```bash
sudo nano /etc/zabbix/zabbix_agentd.conf
```

Les principaux paramètres configurés sont ensuite vérifiés avec :

```bash
grep -E '^(Server|ServerActive|Hostname)=' \
/etc/zabbix/zabbix_agentd.conf
```

Les paramètres permettent notamment de définir :

* le serveur Zabbix autorisé à interroger l'agent ;
* le serveur Zabbix utilisé pour la supervision active ;
* le nom de l'hôte dans Zabbix.

![Configuration du fichier zabbix\_agentd.conf](Images/Conf_fichier_agent_zabbix_server_glpi.png)

---

## 5.3 Vérification du port d'écoute de l'agent

L'agent Zabbix utilise le port TCP :

```text
10050
```

La présence du service en écoute est vérifiée avec :

```bash
ss -tulpn | grep 10050
```

Cette vérification confirme que l'agent est correctement démarré et écoute sur le port prévu.

![Vérification du port TCP 10050](Images/Verification_port_10050_server_glpi.png)

---

## 5.4 Test de communication depuis le serveur Zabbix

L'accessibilité du port TCP 10050 est ensuite testée depuis le serveur Zabbix :

```bash
nc -zv 192.168.1.247 10050
```

Le résultat obtenu est :

```text
open
```

La communication réseau entre le serveur Zabbix et l'agent installé sur le serveur GLPI est donc fonctionnelle.

![Test de communication entre le serveur Zabbix et l'agent GLPI](Images/Verification_depuis_server_zabbix_voit_agent_sur_server_glpi.png)

---

## 5.5 Vérification de la disponibilité dans Zabbix

Le serveur GLPI est ajouté dans l'interface Zabbix et associé à un template Linux adapté.

Dans :

**Surveillance → Hôtes**

l'interface de l'agent apparaît comme disponible.

![Disponibilité de l'agent Zabbix sur le serveur GLPI](Images/Agent_GLPI_disponible_dans_surveillance_hotes.png)

L'indicateur vert confirme que le serveur Zabbix communique correctement avec l'agent installé sur le serveur GLPI.

---

## 5.6 Remontée des métriques

Une fois la communication établie, les premières métriques du serveur GLPI sont collectées par Zabbix.

Les données de supervision sont visibles directement dans l'interface graphique.

![Remontée des métriques du serveur GLPI](Images/extrait_metriques_server_glpi_sur_server_zabbix.png)

Cette première intégration manuelle valide le fonctionnement de la supervision d'un serveur Linux.

Elle permet ensuite de passer à l'étape suivante du projet : l'automatisation du déploiement de Zabbix Agent 2 sur les serveurs Windows avec Ansible.


# 6. Déploiement automatisé de Zabbix Agent 2 avec Ansible

Après avoir validé manuellement la supervision du serveur Linux GLPI, l'étape suivante consiste à automatiser le déploiement de Zabbix Agent 2 sur les serveurs Windows avec Ansible.

Le serveur PKI est utilisé comme première machine de validation de cette automatisation.

L'objectif est de vérifier progressivement :

* la communication entre le contrôleur Ansible et le serveur Windows ;
* le déploiement automatisé de l'agent ;
* la configuration du service ;
* l'ouverture du port TCP 10050 ;
* la communication entre Zabbix et l'agent ;
* puis, dans un second temps, la création automatique de l'hôte dans Zabbix via l'API.

La démarche suivie est donc :

```text
Contrôleur Ansible
        ↓
Test réseau et WinRM
        ↓
Déploiement de Zabbix Agent 2
        ↓
Validation du service Windows
        ↓
Ouverture du port TCP 10050
        ↓
Test depuis le serveur Zabbix
        ↓
Création manuelle initiale de l'hôte PKI
        ↓
Validation de la supervision
        ↓
Création du token API Zabbix
        ↓
Test Ansible → API Zabbix
        ↓
Automatisation de la création des hôtes
```

---

## 6.1 Validation de la communication avec le serveur PKI

Avant de déployer l'agent Zabbix, la communication entre le contrôleur Ansible et le serveur PKI est vérifiée.

Le contrôleur Ansible est situé sur :

```text
ControllerNodeAnsible
192.168.1.246
```

Le serveur PKI est situé sur :

```text
WS2022-CA
192.168.1.236
```

La première étape consiste à vérifier la connectivité réseau entre les deux machines.

Depuis le contrôleur Ansible, un test `ping` est effectué vers le serveur PKI :

```bash
ping -c 4 192.168.1.236
```

Le résultat confirme que la communication IP est fonctionnelle.

La communication utilisée par Ansible repose ensuite sur :

```text
WinRM
TCP 5985
Transport NTLM
```

L'accessibilité du service WinRM est vérifiée avec :

```bash
nc -zv 192.168.1.236 5985
```

Le port doit apparaître comme accessible.

La connexion Ansible est ensuite testée avec le module :

```bash
ansible pki \
-i inventory/zabbix_agent.yml \
-m ansible.windows.win_ping \
--ask-vault-pass
```

Le résultat attendu est :

```text
pki | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

Ce résultat valide simultanément :

* la connectivité réseau ;
* l'accès au service WinRM ;
* l'authentification du compte `CELDUC\ansible` ;
* l'utilisation du transport NTLM ;
* la capacité d'Ansible à exécuter une tâche distante sur le serveur Windows.

Le serveur PKI est donc prêt à recevoir le déploiement automatisé de Zabbix Agent 2.

---

## 6.2 Premier déploiement automatisé sur le serveur PKI

Une fois la communication validée, le playbook de déploiement est exécuté sur le serveur PKI.

Le déploiement est réalisé avec :

```bash
ansible-playbook \
-i inventory/zabbix_agent.yml \
playbooks/install_zabbix_agent.yml \
--limit pki \
--ask-vault-pass
```

Le playbook réalise automatiquement les opérations nécessaires à l'installation de l'agent Zabbix 2.

Les principales étapes sont :

1. vérifier si l'agent est déjà installé ;
2. créer un répertoire temporaire ;
3. copier le fichier MSI sur le serveur Windows ;
4. installer Zabbix Agent 2 ;
5. configurer l'agent ;
6. démarrer le service ;
7. configurer le démarrage automatique ;
8. ouvrir le port TCP 10050 ;
9. supprimer le fichier MSI temporaire.

Le déploiement est réalisé depuis le contrôleur Ansible sans intervention manuelle sur le serveur PKI.

![Déploiement automatisé de Zabbix Agent 2 sur le serveur PKI](Images/Verification_apres_deploiement_agent_zabbix_installe_configure_running_server_PKI.png)

---

## 6.3 Vérification du service Zabbix Agent 2

Après le déploiement, l'état du service est vérifié sur le serveur PKI.

La commande utilisée est :

```powershell
Get-Service -Name "Zabbix Agent 2"
```

Le service doit apparaître dans l'état :

```text
Status   : Running
```

Le démarrage automatique du service est également vérifié.

La configuration attendue est :

```text
Status    : Running
StartType : Automatic
```

Cette vérification confirme que l'installation de l'agent a été correctement réalisée par Ansible.

---

## 6.4 Vérification de l'écoute sur le port TCP 10050

Zabbix Agent 2 utilise le port :

```text
TCP 10050
```

La présence du service en écoute est vérifiée sur le serveur PKI.

Cette étape permet de confirmer que l'agent est prêt à recevoir les requêtes du serveur Zabbix.

La communication attendue est :

```text
Serveur Zabbix
192.168.1.230
        │
        │ TCP 10050
        ▼
Zabbix Agent 2
PKI
192.168.1.236
```

---

## 6.5 Configuration du pare-feu Windows

Pour permettre au serveur Zabbix d'interroger l'agent, le port TCP 10050 doit être autorisé dans le pare-feu Windows.

La règle est créée avec :

```powershell
New-NetFirewallRule `
-DisplayName "Zabbix Agent 2 - TCP 10050" `
-Direction Inbound `
-Protocol TCP `
-LocalPort 10050 `
-Action Allow `
-Enabled True `
-Profile Any
```

La présence de la règle est ensuite vérifiée avec :

```powershell
Get-NetFirewallRule `
-DisplayName "Zabbix Agent 2 - TCP 10050"
```

La règle doit être active et autoriser les connexions entrantes sur le port TCP 10050.

Lors des tests suivants, cette même configuration a également été appliquée lors du déploiement automatisé sur d'autres serveurs, notamment `srv_veeam`.

![Création de la règle de pare-feu pour srv\_veeam](Images/creation_regle_parefeu_srv_veeam.png)

---

## 6.6 Validation de la communication réseau depuis le serveur Zabbix

Une fois l'agent installé et le pare-feu configuré, l'accessibilité du port TCP 10050 est testée depuis le serveur Zabbix.

Pour le serveur PKI :

```bash
nc -zv 192.168.1.236 10050
```

Le résultat attendu est :

```text
open
```

Cette étape confirme que le serveur Zabbix peut atteindre l'agent installé sur le serveur Windows.

---

## 6.7 Installation et utilisation de zabbix_get

Pour effectuer une validation fonctionnelle de l'agent, l'outil `zabbix_get` est installé sur le serveur Zabbix.

Cet outil permet d'interroger directement un agent Zabbix et de vérifier les réponses retournées.

La communication est alors testée avec la clé :

```text
agent.ping
```

La commande utilisée est :

```bash
zabbix_get -s 192.168.1.236 -k agent.ping
```

Le résultat attendu est :

```text
1
```

La valeur `1` confirme que l'agent répond correctement aux requêtes du serveur Zabbix.

La version de l'agent est également vérifiée :

```bash
zabbix_get -s 192.168.1.236 -k agent.version
```

Le résultat obtenu est :

```text
7.4.12
```

Cette validation permet de confirmer simultanément :

* l'accessibilité réseau ;
* l'ouverture du port TCP 10050 ;
* le fonctionnement du service Zabbix Agent 2 ;
* la capacité de l'agent à répondre aux requêtes ;
* la version de l'agent déployée.

![Installation de zabbix\_get et validation de la communication avec l'agent](Images/Installation_zabbix_get_&_verification_reseau_resultat_1.png)

---

## 6.8 Première intégration de PKI dans Zabbix

Après avoir validé le fonctionnement de l'agent, le serveur PKI est ajouté dans l'interface Zabbix.

Cette première intégration est réalisée manuellement afin de valider le fonctionnement complet de la supervision avant d'automatiser la création des hôtes.

L'hôte est configuré avec :

```text
Nom de l'hôte : pki
Adresse IP    : 192.168.1.236
Port          : 10050
```

Le modèle utilisé est :

```text
Windows by Zabbix agent
```

![Création manuelle du serveur PKI dans Zabbix](Images/Creation_Manuellement_server_pki_gui_server_zabbix.png)

Cette étape permet de séparer les deux problématiques :

```text
Déploiement de l'agent
        ↓
Validation de l'agent
        ↓
Création de l'hôte dans Zabbix
        ↓
Validation de la supervision
```

Le déploiement de l'agent étant déjà automatisé avec Ansible, la création de l'hôte dans Zabbix constitue alors la prochaine étape à automatiser.

---

## 6.9 Validation de la supervision de PKI dans l'interface Zabbix

Après la création de l'hôte, la disponibilité de l'agent est vérifiée dans l'interface Zabbix.

L'indicateur `ZBX` apparaît en vert.

Cette validation confirme que :

* l'agent est installé ;
* le service est démarré ;
* le port TCP 10050 est accessible ;
* le serveur Zabbix peut communiquer avec l'agent ;
* le nom d'hôte est correctement configuré ;
* le template Windows est correctement associé.

![Validation de la disponibilité du serveur PKI dans Zabbix](Images/Test_Validation_remontee_server_dans_zabbix_gui.png)

Le premier déploiement automatisé de Zabbix Agent 2 sur un serveur Windows est donc validé.

---

## 6.10 Création du token API Zabbix

Afin d'automatiser également la création des hôtes dans Zabbix, l'API Zabbix est utilisée.

Un token API est créé dans l'interface Zabbix.

Ce token permet à Ansible de communiquer avec le serveur Zabbix et de créer ou mettre à jour automatiquement les hôtes.

![Création du token API Zabbix](Images/creation_token_API_server_zabbix.png)

Le token est ensuite utilisé par Ansible pour les opérations réalisées via l'API.

Pour des raisons de sécurité, le token n'est pas stocké directement en clair dans le playbook.

Il est stocké dans Ansible Vault avec les autres informations sensibles :

```text
zabbix_api_token
```

---

## 6.11 Test de communication entre Ansible et l'API Zabbix

Avant d'ajouter la création automatique des hôtes au playbook principal, un test spécifique est réalisé.

L'objectif est de vérifier séparément la communication entre :

```text
Contrôleur Ansible
        │
        │ API Zabbix
        ▼
Serveur Zabbix
192.168.1.230
```

Un playbook de test est utilisé afin de valider :

* l'accès au serveur Zabbix ;
* l'utilisation du token API ;
* l'authentification auprès de l'API ;
* la communication entre Ansible et Zabbix.

Le résultat du test est validé avec succès.

![Test de communication entre Ansible et l'API Zabbix](Images/PLayboo_Test_communication_server_ansible_api_zabbix_OK.png)

Cette validation permet d'éviter de modifier directement le playbook de déploiement avant d'avoir confirmé que la communication avec l'API fonctionne correctement.

---

## 6.12 Automatisation de la création de l'hôte dans Zabbix

Une fois la communication avec l'API validée, le playbook est amélioré.

Une nouvelle tâche est ajoutée afin de créer ou mettre à jour automatiquement l'hôte dans Zabbix.

Le module utilisé est :

```text
community.zabbix.zabbix_host
```

Cette tâche permet notamment de configurer automatiquement :

* le nom de l'hôte ;
* le groupe Zabbix ;
* le template ;
* l'interface agent ;
* l'adresse IP ;
* le port TCP 10050.

La chaîne de déploiement devient alors :

```text
Ansible
    ↓
WinRM
    ↓
Installation de Zabbix Agent 2
    ↓
Configuration du service
    ↓
Pare-feu TCP 10050
    ↓
API Zabbix
    ↓
Création automatique de l'hôte
```

![Ajout de la tâche de création automatique de l'hôte](Images/Playbook_avec_New_Tache.png)

Le playbook permet désormais d'automatiser à la fois le déploiement de l'agent et l'intégration du serveur dans Zabbix.

---

## 6.13 Première création automatisée d'un hôte dans Zabbix

Le playbook est ensuite exécuté avec la nouvelle tâche d'intégration API.

L'hôte est créé automatiquement dans Zabbix depuis le contrôleur Ansible.

Cette opération permet de supprimer l'étape de création manuelle de l'hôte.

La nouvelle chaîne est donc :

```text
Serveur Windows
        ↓
Ansible
        ↓
Installation de l'agent
        ↓
Configuration Windows
        ↓
Pare-feu
        ↓
API Zabbix
        ↓
Création automatique de l'hôte
        ↓
Supervision
```

![Création automatique d'un hôte depuis Ansible dans Zabbix](Images/creation_automatisee_hote_depuis_ansible_sur_zabbix_server.png)

La création automatique de l'hôte est ainsi validée.

---

## 6.14 Déploiement automatisé sur plusieurs serveurs

Après validation du fonctionnement sur le serveur PKI, le déploiement est étendu à plusieurs serveurs Windows.

Le playbook permet de déployer automatiquement Zabbix Agent 2 et de créer les hôtes correspondants dans Zabbix.

Le lancement du déploiement est réalisé depuis le contrôleur Ansible.

Plusieurs serveurs sont déployés avec succès.

![Déploiement automatisé sur plusieurs serveurs Windows](Images/lancement_playbook_5_server_OK.png)

Les machines intégrées comprennent notamment :

```text
PKI
SRV-VEEAM
CAO-RELAIS
CAO-TRANSFO
DATA1-2014
SAGE
```

Chaque serveur est automatiquement :

* préparé ;
* équipé de Zabbix Agent 2 ;
* configuré ;
* associé à une règle de pare-feu ;
* intégré dans Zabbix via l'API.

---

## 6.15 Vérification après déploiement

Après le déploiement, les serveurs sont vérifiés directement sur leur système d'exploitation.

L'état du service Zabbix Agent 2 doit être :

```text
Running
```

Le port TCP 10050 doit également être accessible.

Des validations complémentaires sont réalisées depuis le serveur Zabbix avec :

```bash
zabbix_get -s <IP> -k agent.ping
```

Le résultat attendu est :

```text
1
```

Ces tests permettent de vérifier que les agents déployés automatiquement fonctionnent correctement.

---

## 6.16 Validation finale dans l'interface Zabbix

La dernière étape consiste à vérifier la disponibilité des serveurs dans l'interface Zabbix.

Les hôtes apparaissent comme disponibles avec l'indicateur `ZBX` en vert.

Cette validation confirme que la chaîne complète fonctionne :

```text
Active Directory / GPO
        ↓
WinRM
        ↓
Ansible
        ↓
Installation de Zabbix Agent 2
        ↓
Configuration Windows
        ↓
Pare-feu TCP 10050
        ↓
API Zabbix
        ↓
Création automatique de l'hôte
        ↓
Supervision opérationnelle
```

L'automatisation du déploiement et de l'intégration des serveurs Windows dans Zabbix est désormais fonctionnelle.

La procédure initialement réalisée sur un seul serveur de test peut donc être reproduite sur plusieurs serveurs de l'infrastructure.

La prochaine étape consiste à valider le déploiement complet sur un premier serveur, puis à l'étendre progressivement aux autres serveurs de l'infrastructure.
