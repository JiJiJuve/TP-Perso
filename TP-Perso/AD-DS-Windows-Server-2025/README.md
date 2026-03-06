# Installation d’Active Directory (AD DS) sur Windows Server 2025

Ce guide décrit l’installation d’un contrôleur de domaine Active Directory (AD DS) et du rôle DNS sur Windows Server 2025, ainsi que la mise en place de partages de fichiers sécurisés basés sur des groupes.  
Il est pensé pour un **lab pédagogique** reproduisant une petite infrastructure d’entreprise.

> 📄 Fiche synthèse : [AD DS – Installation et configuration](Fiche-AD-DS-Installation-et-Conf-Windows-Server-2025.md)
---

## Sommaire

- [1. Prérequis du lab](#1-prérequis-du-lab)
- [2. Rappels sur Active Directory](#2-rappels-sur-active-directory)
- [3. Pré‑requis techniques sur le serveur](#3-pré‑requis-techniques-sur-le-serveur)
- [4. Préparation du serveur](#4-préparation-du-serveur)
- [5. Installation des rôles AD DS et DNS](#5-installation-des-rôles-ad-ds-et-dns)
- [6. Promotion en contrôleur de domaine](#6-promotion-en-contrôleur-de-domaine)
- [7. Outils d’administration AD](#7-outils-dadministration-ad)
- [8. Création d’une structure d’OU](#8-création-dune-structure-dou)
- [9. Création d’utilisateurs](#9-création-dutilisateurs)
- [10. Préparer les partages de fichiers](#10-préparer-les-partages-de-fichiers-it--rh--direction)
- [11. Créer les groupes AD par service](#11-créer-les-groupes-ad-par-service)
- [12. Configurer les droits NTFS](#12-configurer-les-droits-ntfs-sur-les-dossiers)
- [13. Créer les partages réseau](#13-créer-les-partages-réseau)
- [14. Tester les droits depuis un poste client](#14-tester-les-droits-depuis-un-poste-client)
- [15. Pour aller plus loin](#15-pour-aller-plus-loin)

---

## 1. Prérequis du lab

- 1 VM **Windows Server 2025** (ex. 2 vCPU, 4 Go de RAM, 60 Go de disque).
- 1 VM **client Windows** (10/11) pour les tests d’accès.
- Réseau fonctionnel entre les VMs (même LAN / même réseau virtuel).
- Accès administrateur local sur le serveur.
- ISO Windows Server 2025 déjà installé et activé en version Évaluation ou Standard.

---

## 2. Rappels sur Active Directory

Active Directory (AD) est le service d’annuaire de Microsoft utilisé pour centraliser la gestion des utilisateurs, des ordinateurs et des ressources du réseau.

**Rôles principaux :**

- Gestion des utilisateurs et groupes (authentification, autorisations).
- Contrôle d’accès aux fichiers, imprimantes, applications.
- Déploiement de GPO (stratégies de sécurité / configuration).
- Administration centralisée du réseau.
- Organisation logique des ressources dans un domaine.

**Termes clés :**

- **Contrôleur de domaine (DC)** : serveur qui stocke la base AD DS et gère l’authentification.
- **Domaine** : périmètre logique partageant la même base AD.
- **Forêt** : ensemble de domaines partageant schéma + configuration.
- **OU (Unité d’Organisation)** : conteneur logique pour organiser objets et appliquer GPO.
- **LDAP** : protocole utilisé pour interroger/modifier les données de l’annuaire.

---

## 3. Pré‑requis techniques sur le serveur

- Windows Server récent (≥ 2016, ici **2025**).
- Nom de machine propre et unique (ex. `DC01`).
- Adresse IP **statique** (pas de DC en DHCP).
- DNS configuré (le DC pointera sur lui‑même ou un autre DC après install).
- Compte admin local avec mot de passe.
- Heure système correcte (Kerberos).
- Nom de domaine au format DNS : ex. `lab.local` ou `colin.lan`.

---

## 4. Préparation du serveur

![Tableau de bord Windows Server](images/tableau_bord.png)

### 4.1 Renommer le serveur

1. Ouvrir **Gestionnaire de serveur** → onglet **Serveur local**.  
2. Cliquer sur le nom de l’ordinateur → **Modifier**.  
3. Saisir un nom explicite (ex. `DC01`) → redémarrer le serveur.

![Définir le nom du serveur](images/definir_nom_server.png)

### 4.2 Configurer l’IP statique

1. Depuis le Gestionnaire de serveur, cliquer sur la carte réseau.  
2. Ouvrir les propriétés **IPv4**.  
3. Renseigner :
   - IP fixe  
   - Masque  
   - Passerelle  
   - DNS (lui‑même ou futur DC/DNS).

![Définir une IP fixe](images/definir_IP_fixe_server.png)

---

## 5. Installation des rôles AD DS et DNS

1. **Gestionnaire de serveur** → menu **Gérer** → **Ajouter des rôles et fonctionnalités**.  
2. Type d’installation :  
   - *Installation basée sur un rôle ou une fonctionnalité*.  
3. Sélectionner le **serveur local**.  
4. Cocher les rôles :
   - **Services de domaine Active Directory (AD DS)**  
   - **Serveur DNS** (si aucun autre DNS sur le réseau)  
5. Passer les écrans de confirmation → cliquer sur **Installer**.  
6. Redémarrer le serveur après installation.

![Sélection des rôles AD DS et DNS](images/installation_services_AD_DNS.png)

![Résumé installation des rôles](images/installation_services_AD_DNS2.png)

![Installation des rôles en cours](images/install_role_OK.png)

![Installation terminée](images/install_OK.png)

---

## 6. Promotion en contrôleur de domaine

1. Dans le Gestionnaire de serveur, cliquer sur la notification :  
   - **Promouvoir ce serveur en contrôleur de domaine**.  
2. Choisir :
   - **Ajouter une nouvelle forêt** si c’est le premier DC.  
   - Saisir le nom de domaine (ex. `lab.local` / `colin.lan`).  
3. Définir le mot de passe **DSRM** (Directory Services Restore Mode) et le conserver.  
4. Laisser les options avancées par défaut (DNS, NetBIOS…) sauf besoin spécifique.  
5. Lancer la vérification des prérequis → **Installer**.  
6. Le serveur redémarre automatiquement → il devient **DC + DNS** pour la nouvelle forêt.

![Créer une nouvelle forêt](images/creation_new_foret.png)

![Configuration du domaine](images/creation_foret_config_domaine.png)

![Options supplémentaires de la forêt](images/creation_new_foret2.png)

![Vérification des prérequis](images/creation_new_foret3.png)

![Résumé avant promotion](images/creation_new_foret4.png)

---

## 7. Outils d’administration AD

Après promotion, dans **Gestionnaire de serveur** → **Outils**, on trouve notamment :

- **DNS**  
  Gestion des zones et enregistrements DNS (A, CNAME, SRV, etc.).  

- **Domaines et approbations Active Directory**  
  Gestion des relations d’approbation entre domaines / forêts.  

- **Utilisateurs et ordinateurs Active Directory**  
  Création et gestion des utilisateurs, groupes, ordinateurs, OU.  

- **Module Active Directory pour Windows PowerShell**  
  Administration AD en PowerShell (scripts, automatisation).

---

## 8. Création d’une structure d’OU

J’ai créé une structure d’unités d’organisation (OU) pour organiser les objets Active Directory par service (IT, RH, Direction).  
Cette structure servira ensuite à appliquer des GPO ciblées et à mieux gérer les droits.

![Création d'une OU](images/creation_OU(unite_organisation).png)

![OU créée dans la console](images/creation_OU(unite_organisation)2.png)

---

## 9. Création d’utilisateurs

Pour peupler l’annuaire, je crée des comptes utilisateurs qui seront ensuite ajoutés dans les groupes par service.

![Création d'un nouvel utilisateur](images/creation_new_user.png)

![Assistant nouvel utilisateur](images/creation_new_user2.png)

![Définition du mot de passe](images/creation_new_user3.png)

![Utilisateur créé](images/creation_new_user4.png)

---

## 10. Préparer les partages de fichiers (IT / RH / Direction)

### 10.1 Arborescence des dossiers sur le serveur

Sur le serveur de fichiers (ou ton DC pour le lab) :

- Créer un dossier racine pour les données, par exemple :  
  - `C:\Partages` (en prod : de préférence sur un autre disque, ex. `D:\Partages`).  
- Créer un sous‑dossier par service :  
  - `C:\Partages\IT`  
  - `C:\Partages\RH`  
  - `C:\Partages\DIRECTION`

![Création des dossiers de partage](images/Creation_dossier_partages.png)

---

## 11. Créer les groupes AD par service

Dans **Utilisateurs et ordinateurs Active Directory** :

1. Créer des **groupes de sécurité globaux** :
   - `GG-IT`  
   - `GG-RH`  
   - `GG-DIRECTION`  

   Paramètres :
   - Type : **Sécurité**  
   - Portée : **Globale**

2. Ajouter les membres :
   - Ouvrir le groupe (ex. `GG-IT`).  
   - Onglet **Membres** → **Ajouter…**.  
   - Ajouter les utilisateurs du service (ex. `user.it1`, `user.it2`).  

Ces groupes serviront à donner les droits sur les dossiers (NTFS) et éventuellement à filtrer des GPO.

![Création d'un groupe](images/Creation_Groupe.png)

![Détails du groupe](images/Creation_Groupe2.png)

![Ajout de membres dans le groupe](images/ajout_membre_groupe.png)

![Ajout d'autres membres](images/ajout_membre_groupe2.png)

![Vue finale des membres](images/ajout_membre_groupe3.png)

---

## 12. Configurer les droits NTFS sur les dossiers

### 12.1 Désactiver l’héritage

Pour chaque dossier de service, par exemple `C:\Partages\IT` :

1. Clic droit → **Propriétés** → onglet **Sécurité**.  
2. Bouton **Avancé**.  
3. Cliquer sur **Désactiver l’héritage**.  
4. Choisir : **Convertir les autorisations héritées en autorisations explicites**.

Ensuite, dans la liste :

- Garder :
  - `SYSTEM` (Contrôle total)  
  - `Administrateurs` (Contrôle total)  
  - `Créateur propriétaire`  
- Supprimer si présent :
  - `Utilisateurs` / `Users`  
  - Comptes utilisateurs individuels (ex. `jiji`), pour ne garder que des groupes dans les ACL.

![Nettoyage des ACL (users inutiles)](images/enlever_user_inutiles.png)

### 12.2 Ajouter les groupes AD

Toujours sur `C:\Partages\IT` :

1. Onglet **Sécurité** → **Modifier** → **Ajouter**.  
2. Ajouter le groupe `GG-IT`.  
3. Lui donner le droit **Modification** (lecture/écriture/suppression).

![Ajout du groupe dans les droits NTFS](images/ajout_groupe_droit_ntfs_dossier_partages.png)

![Droits NTFS appliqués](images/ajout_groupe_droit_ntfs_dossier_partages2.png)

Répéter pour les autres dossiers :

- `C:\Partages\RH` → groupe `GG-RH` → **Modification**.  
- `C:\Partages\DIRECTION` → groupe `GG-DIRECTION` → **Modification** (ou plus restrictif selon le besoin).

**Principe :**

- Les utilisateurs n’apparaissent **jamais** directement dans les droits NTFS.  
- On donne les droits aux **groupes AD**, puis on gère les users dans les groupes.

---

## 13. Créer les partages réseau

Sur le serveur, par exemple pour `C:\Partages\IT` :

1. Clic droit sur `C:\Partages\IT` → **Propriétés** → onglet **Partage**.  
2. Bouton **Partage avancé**.  
3. Cocher **Partager ce dossier**.  
4. Nom du partage :
   - `IT` (ou `IT$` pour un partage caché).  
5. Bouton **Autorisations** (autorisations de partage) :
   - En lab, on peut laisser `Tout le monde : Contrôle total` et se reposer sur NTFS pour la sécurité fine.

Répéter :

- `C:\Partages\RH` → partage `RH` / `RH$`.  
- `C:\Partages\DIRECTION` → partage `DIRECTION` / `DIRECTION$`.

**Rappel :**

- **NTFS** (onglet Sécurité) = vraie limite de sécurité.  
- **Partage** (onglet Partage) = porte d’entrée réseau, souvent plus large, filtrage fin en NTFS.

---

## 14. Tester les droits depuis un poste client

Depuis un PC joint au domaine :

### 14.1 Test d’accès pour un user autorisé

1. Se connecter avec un user membre de `GG-IT` (ex. `user.it1`).  
2. Ouvrir l’explorateur → dans la barre d’adresse :  
   - `\\NOM_DU_SERVEUR\IT`  
3. Vérifier :
   - Le dossier s’ouvre.  
   - On peut créer un fichier (Nouveau → Document texte).  
   - On peut modifier et supprimer ce fichier.

### 14.2 Test de blocage pour un user non autorisé

1. Se connecter avec un user qui **n’est pas** dans `GG-IT` (par ex. user RH).  
2. Essayer `\\NOM_DU_SERVEUR\IT`.  
3. Résultat attendu :
   - Accès refusé ou impossibilité d’écrire/modifier.

Ce double test valide que la gestion par **groupes AD + NTFS** fonctionne comme prévu.

---

## 15. Pour aller plus loin

- Mettre en place des GPO (sécurité, configuration des postes, scripts de connexion).  
- Ajouter un deuxième DC pour la redondance du service AD DS.
