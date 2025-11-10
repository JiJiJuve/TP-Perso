# Installation et Configuration d'un serveur Proxmox VE

---

## Contexte

Ce TP apour objectif d'installer et configurer Proxmox VE dans une machine virtuelle VirtualBox, afin de mettre en place un hyperviseur pour gérer des VM.

---

## Objectifs

- Installer Proxmox VE dans Virtualbox
- Configurer les paramètres réseau et stockage
- Se connecter à l'interface web de gestion
- Créer et gérer des machines virtuelles

## Matériel et Logiciels

- PC hôte avec VirtualBox
- ISO Proxmox VE (version proxmox-ve_9.0-1)
- OS hôte Windows 11 Pro

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

   ![Mise à jours des paquets Proxmox](./images/MAJ_Proxmox.png)

Cela garantit que le système est à jour avec les dernières corrections et améliorations.

---

Cette démarche est classique pour ceux qui utilisent Proxmox sans licence professionnelle et veulent garder leur installation à jour en toute légalité.
