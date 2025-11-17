## **Installation et configuration de Proxmox VE et pfSense dans un environnement virtualisé**

---

## Contexte

Ce TP a pour objectif d’installer et configurer Proxmox VE dans une machine virtuelle VirtualBox, puis de déployer une VM pfSense afin de mettre en place un hyperviseur capable de gérer des machines virtuelles, de simuler un environnement réseau sécurisé, et d’expérimenter différentes fonctionnalités de firewall, routage et services réseau.

# Introduction

- Proxmox Virtual Environment (Proxmox VE) est une plateforme open source de virtualisation qui permet de créer et gérer des machines virtuelles et des conteneurs sur un seul serveur. Elle offre une interface web puissante pour administrer facilement les systèmes virtualisés, optimiser les ressources matérielles, et gérer le stockage et la mise en réseau. Proxmox est souvent utilisé en entreprise pour consolider des serveurs, simplifier la gestion informatique et garantir une haute disponibilité des services.

- pfsense est une distribution open source basée sur FreeBSD permettant de déployer un pare-feu (firewall), de contrôler le routage, de gérer le NAT, et d’offrir de nombreux services réseau avancés (DHCP, VPN, etc.).
  Intégré comme machine virtuelle dans Proxmox, pfSense permet de simuler des architectures réseau sécurisées et d’apprendre la gestion des flux réseau et des règles de sécurité en environnement virtualisé.

---

## Objectifs

- Installer Proxmox VE dans Virtualbox
- Configurer les paramètres réseau et stockage
- Se connecter à l'interface web de gestion
- Créer et gérer des machines virtuelles
- Déployer une machine virtuelle pfsense via proxmox
- Configurer pfSense pour simuler un environnement réseau sécurisé (interfaces, DHCP, NAT, firewall)
- Vérifier la connectivité et les services réseau à partir d’une VM cliente

## Matériel et Logiciels

- PC hôte avec VirtualBox
- ISO Proxmox VE (version proxmox-ve_9.0-1)
- ISO pfSense (ex : pfSense-ce-2.7.2-RELEASE-amd64)
- OS hôte Windows 11 Pro
- VM cliente (Debian) pour tester le réseau

## Etapes réalisées

1. Téléchargement de l’image ISO officielle de Proxmox VE depuis le site officiel, suivi de la vérification de l’intégrité du fichier via le contrôle du hash SHA256 pour garantir la validité de l’ISO.

   ![Téléchargement de l'ISO Proxmox](./images/Download_ISO_Proxmox.png)

   ![Vérification du Hash ISO](./images/verif_Hash.png)
2. Création de la machine virtuelle Proxmox dans VirtualBox

   ![Création VM Proxmox dans VirtualBox](./images/creation_VM_Proxmox.png)
3. Installation de Proxmox VE à partir de l'ISO

   ![Installation Proxmox depuis ISO](./images/Install1.png)

   ![Suite Installation Proxmox depuis ISO](./images/Install2.png)
4. Retrait de l'ISO pour éviter la boucle d'installation
5. Configuration réseau en mode Bridge
6. Connexion à l'interface web via https://IP_VM:8006 + Premier login root

   ![Interface Web Proxmox](./images/connexion_interface_proxmox.png)
7. Interface de Gestion Web Proxmox

   ![Interface Gestion Web Proxmox](./images/interface_proxmox.png)
8. Configuration du compte en mode **no-subscription**

   - Proxmox VE propose par défaut un dépôt "Enterprise" réservé aux abonnés payants.

     ![Depôt Entreprise Proxmox](./images/pas_subscription.png)
   - Pour les utilisateurs sans abonnement, il faut configurer le dépôt**no-subscription** pour continuer à recevoir les mises à jour du système et des paquets.

     ![Configuration ](./images/pas_subscription_No-sub=obtenir_MAJ.png)
   - Ce dépôt offre un accès rapide aux mises à jour suffisant pour un usage personnel ou lab.

   ![No-Subscription permet d'avoir les MàJ](./images/pas_subscription_MaJ_OK2.png)
9. Mise à jour des caches des paquets

   ![mise à jour](./images\MaJ_cache_paquetproxmox.png)

   ![Mise à jours des paquets Proxmox](./images/MAJ_Proxmox.png)

Cela garantit que le système est à jour avec les dernières corrections et améliorations.

---

Cette démarche est classique pour ceux qui utilisent Proxmox sans licence professionnelle et veulent garder leur installation à jour en toute légalité.

## Gestion des utilisateurs : création d’un compte non-root dans Proxmox VE

Dans une logique de bonnes pratiques de sécurité, toutes les opérations courantes relatives à la gestion des machines virtuelles, des stockages ou des ISO sont effectuées depuis un compte utilisateur **Proxmox VE** et non depuis le compte root.

![Création User](./images/creation_user_proxmoxVE.png)

![suite création user](./images/creation_user_proxmoxVE2.png)

![Role new user](./images/creation_user_role_proxmoxVE2.png)

Cette démarche s’inscrit dans un souci de séparation des privilèges et d’amélioration de la sécurité de l’infrastructure Proxmox.

---

## Ajout et Vérification de l'ISO Pfsense

1 - Vérification de l'Intégrité de l'ISO Pfsense

![Hash ISO Pfsense](./images\hash_iso_pfsense_site_officiel.png)

![Vérification Hash Iso Pfsense](./images\hash_iso_pfsense.png)

Pour garantir l’intégrité et l’authenticité de l’image ISO utilisée, j’ai récupéré son SHA256 sur le site officiel Netgate, puis vérifier et comparer dans PowerShell.

2 - Ajout de l'ISO Pfsense dans Proxmox

![Dowload ISO dans Proxmox](./images/install_ISO_Proxmox.png)

---

## Création de la VM Pfsense

![Création VM PFsense](./images/creation_vm_pfsense.png)

![Suite création VM Pfsense](./images//vm_pfsense_créee.png)

#### Création et ajout de l'interface réseau LAN sous Proxmox

Mise en place d’un bridge virtuel (vmbr1) dans Proxmox, associé à l’interface réseau (enp0s8), pour le réseau interne (LAN).
La VM pfSense a été configurée avec son interface LAN raccordée à ce bridge, permettant la connectivité avec les clients du réseau interne (ex : VM Debian en ‘Internal Network’).

![Création Interface Réseau LAN](./images\rajout_interface_reseau_lan2.png)

![Création Interface Reseau LAN](./images\rajout_interface_reseau_lan.png)

---

## Création VM Pfsense depuis ISO

![Création vm pfsense depuis l'ISO](./images\lancement_creation_depuis_iso_vm_pfsense.png)

## Configuration interface réseau WAN + LAN

![configuration interafces reseau WAN etLAN](./images\config_interfaces_reseau.png)

![Validation Configuration Interfaces Réseaux](./images\config_interfaces_reseau2.png)

---

## Accés à l'interface Web de PFsense depuis une VM LAN

- #### Connexion par défaut avec "admin" et "pfsense"


![Connexion interface web pfsense](./images\connexion_interface_web_pfsense.png)

- #### Configuration de base sur PFsense

  ![configuration de base pfsense](./images\gui_pfsense.png)
- #### Fonctionnement DHCP avec attribution IP (192.168.2.100) à ma VM client dans LAN


![ip depuis DHCP vm client](./images\ip_vm_client_dhcp.png)

- #### Dashbord Pfsense



![tableau de bord de PFsense](./images\dhasbord_pfsense.png)

---

**Le TP est validé : l’environnement réseau fonctionne correctement et l’accès au dashboard de pfSense confirme la bonne configuration des interfaces WAN et LAN ainsi que la connectivité des clients.
La prochaine étape consistera à approfondir la gestion des certificats d’autorités et à mettre en place des règles de firewall sur pfSense.**
