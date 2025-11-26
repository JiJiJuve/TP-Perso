# **Installation et configuration de Proxmox VE et pfSense dans un environnement virtualisé**

---

## Sommaire
- [Contexte](#contexte)
- [Objectifs](#objectifs)
- [Matériel et logiciels](#matériel-et-logiciels)
- [Étapes réalisées](#etapes-réalisées)
- [Gestion des utilisateurs](#gestion-des-utilisateurs--création-dun-compte-non-root-dans-proxmox-ve)
- [Ajout et Vérification de l ISO Pfsense](#ajout-et-verification-de-l-iso-pfsense)
- [Création vm pfsense](#création-de-la-vm-pfsense)
- [Conclusion](#conclusion)

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
     
   - Pour les utilisateurs sans abonnement, il faut configurer le dépôt **no-subscription** pour continuer à recevoir les mises à jour du système et des paquets.

    <img width="1920" height="1032" alt="pas_subscription_No-sub=obtenir_MaJ" src="https://github.com/user-attachments/assets/1d0cdbd9-dd38-41e8-b948-94319e49f14c" />

     
   - Ce dépôt offre un accès rapide aux mises à jour suffisant pour un usage personnel ou lab.

   ![No-Subscription permet d'avoir les MàJ](./images/pas_subscription_MaJ_OK2.png)
   
10. Mise à jour des caches des paquets

   <img width="1920" height="1032" alt="MaJ_cache_paquetproxmox" src="https://github.com/user-attachments/assets/7c108977-1b3a-407b-ba22-6c7d3e658046" />


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

## Ajout et Vérification de l ISO Pfsense

1 - Vérification de l'Intégrité de l'ISO Pfsense

<img width="920" height="378" alt="hash_iso_pfsense_site_officiel" src="https://github.com/user-attachments/assets/2e505434-6b21-45db-ab99-e5241d55e0d5" />

<img width="1109" height="608" alt="hash_iso_pfsense" src="https://github.com/user-attachments/assets/c33407f4-15cf-4a76-b517-ae2ec0608cd6" />



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

<img width="1675" height="268" alt="rajout_interface_reseau_lan2" src="https://github.com/user-attachments/assets/91dec50f-b0ef-456e-9182-02cac8a07ecf" />


<img width="1021" height="388" alt="rajout_interface_reseau_lan" src="https://github.com/user-attachments/assets/4a2ac0f0-ea80-4b50-8986-d05cbbecfb90" />


---

## Création VM Pfsense depuis ISO

<img width="1157" height="639" alt="lancement_creation_depuis_iso_vm_pfsense" src="https://github.com/user-attachments/assets/d0811126-5f3c-41fb-bb22-bfbc560110e9" />

## Configuration interface réseau WAN + LAN

<img width="828" height="528" alt="config_interfaces_reseau" src="https://github.com/user-attachments/assets/40b1f10a-758e-48c2-b765-aeec896f1682" />

<img width="1749" height="426" alt="config_interfaces_reseau2" src="https://github.com/user-attachments/assets/703eefb1-4e24-4556-a809-49a8f806b84b" />


---

## Accés à l'interface Web de PFsense depuis une VM LAN

- #### Connexion par défaut avec "admin" et "pfsense"


<img width="800" height="600" alt="connexion_interface_web_pfsense" src="https://github.com/user-attachments/assets/b91ad585-9552-4a01-a23d-78c15a6711d7" />


- #### Configuration de base sur PFsense

<img width="1920" height="955" alt="gui_pfsense" src="https://github.com/user-attachments/assets/997980c8-ec65-436f-9ad7-c6ec778b6c58" />

  
- #### Fonctionnement DHCP avec attribution IP (192.168.2.100) à ma VM client dans LAN


<img width="1114" height="613" alt="ip_vm_client_dhcp" src="https://github.com/user-attachments/assets/ada7e6e1-c0d6-451a-97a8-eeb390072e4b" />

- #### Dashbord Pfsense



<img width="1152" height="864" alt="dhasbord_pfsense" src="https://github.com/user-attachments/assets/b2e2fb0d-6d57-4f8a-b43a-9de9be733ea9" />


---

## Conclusion

**Le TP est validé : l’environnement réseau fonctionne correctement et l’accès au dashboard de pfSense confirme la bonne configuration des interfaces WAN et LAN ainsi que la connectivité des clients.
La prochaine étape consistera à approfondir la gestion des certificats d’autorités et à mettre en place des règles de firewall sur pfSense.**
