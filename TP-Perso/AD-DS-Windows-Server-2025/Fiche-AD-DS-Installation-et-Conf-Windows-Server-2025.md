# Active Directory – Installation sur Windows Server 2025

## 1. Rappels sur Active Directory

Active Directory (AD) est le service d’annuaire de Microsoft utilisé pour centraliser la gestion des utilisateurs, des ordinateurs et des ressources du réseau.

**Rôles principaux :**
- Gestion des **utilisateurs** et **groupes** (authentification, autorisations).  
- Contrôle d’accès aux **fichiers**, **imprimantes**, **applications**.  
- Déploiement de **GPO** (stratégies de sécurité / configuration).  
- Administration centralisée du réseau.  
- Organisation logique des ressources dans un **domaine**.

**Termes clés :** 
- **Contrôleur de domaine (DC)** : serveur qui stocke la base AD DS et gère l’authentification.  
- **Domaine** : périmètre logique partageant la même base AD.  
- **Forêt** : ensemble de domaines partageant schéma + configuration.  
- **OU (Unité d’Organisation)** : conteneur logique pour organiser objets et appliquer GPO.  
- **LDAP** : protocole utilisé pour interroger/modifier les données de l’annuaire.

***

## 2. Pré‑requis avant l’installation

**Technique :**
- Windows Server récent (≥ 2016, ici 2025).  
- Nom de machine propre et unique (ex. `DC01`).  
- **Adresse IP statique** (pas de DC en DHCP).  
- DNS configuré (le DC pointera sur lui‑même ou un autre DC après install).  
- Compte **admin local** avec mot de passe.  
- Heure système correcte (Kerberos).  
- Nom de domaine au format DNS : ex. `colin.lan`.

***

## 3. Préparation du serveur

### 3.1 Renommer le serveur

1. Ouvrir **Gestionnaire de serveur** → onglet **Serveur local**.  
2. Cliquer sur le nom de l’ordinateur → **Modifier**.  
3. Saisir un nom explicite (ex. `DC01`) → redémarrer le serveur. 

### 3.2 Configurer l’IP statique

1. Depuis **Gestionnaire de serveur**, cliquer sur la carte réseau.  
2. Ouvrir les propriétés IPv4.  
3. Renseigner :  
   - IP fixe  
   - Masque  
   - Passerelle  
   - DNS (lui‑même ou futur DC/DNS). 

***

## 4. Installation des rôles AD DS et DNS

1. **Gestionnaire de serveur** → menu **Gérer** → **Ajouter des rôles et fonctionnalités**.  
2. Type d’installation :  
   - **Installation basée sur un rôle ou une fonctionnalité**.  
3. Sélectionner le serveur local.  
4. Cocher les rôles :
   - **Services de domaine Active Directory (AD DS)**  
   - **Serveur DNS** (si aucun autre DNS sur le réseau)  
5. Passer les écrans de confirmation → cliquer sur **Installer**.  
6. Redémarrer le serveur après installation.

***

## 5. Promotion en contrôleur de domaine

1. Dans le **Gestionnaire de serveur**, cliquer sur la notification → **Promouvoir ce serveur en contrôleur de domaine**.
2. Choisir :  
   - **Ajouter une nouvelle forêt** si c’est le premier DC.  
   - Saisir le **nom de domaine** (ex. `colin.lan`).  
3. Définir le **mot de passe DSRM** (Directory Services Restore Mode) et le conserver. 
4. Laisser les options avancées par défaut (DNS, NetBIOS…) sauf besoin spécifique.
5. Lancer la vérification des prérequis → **Installer**.  
6. Le serveur redémarre automatiquement → il devient **DC + DNS** pour la nouvelle forêt. 

***

## 6. Outils d’administration AD

Après promotion, dans **Gestionnaire de serveur → Outils**, tu as notamment : 
- **DNS**  
  - Gestion des zones et enregistrements DNS (A, CNAME, SRV, etc.).  
- **Domaines et approbations Active Directory**  
  - Gestion des relations d’approbation entre domaines / forêts.  
- **Utilisateurs et ordinateurs Active Directory**  
  - Création et gestion des utilisateurs, groupes, ordinateurs, OU.  
- **Module Active Directory pour Windows PowerShell**  
  - Administration AD en PowerShell (scripts, automatisation).

***

## 8. Préparer les partages de fichiers (IT / RH / Direction)

### 8.1 Arborescence des dossiers sur le serveur

Sur le serveur de fichiers (ou ton DC pour le lab) :

- Créer un dossier racine pour les données, par exemple :  
  - `C:\Partages` (en prod : de préférence sur un autre disque, ex. `D:\Partages`).
- Créer un sous‑dossier par service :  
  - `C:\Partages\IT`  
  - `C:\Partages\RH`  
  - `C:\Partages\DIRECTION`  

***

## 9. Créer les groupes AD par service

Dans **Utilisateurs et ordinateurs Active Directory** :

- Créer des **groupes de sécurité globaux** :
  - `GG-IT`  
  - `GG-RH`  
  - `GG-DIRECTION`  

Paramètres :  
- Type : **Sécurité**  
- Portée : **Globale**  

Ajouter les membres :  
1. Ouvrir le groupe (ex. `GG-IT`).  
2. Onglet **Membres** → **Ajouter…**.  
3. Ajouter les utilisateurs du service (ex. `user.it1`, `user.it2`). 
Ces groupes serviront à donner les droits sur les dossiers (NTFS) et éventuellement à filtrer des GPO.

***

## 10. Configurer les droits NTFS sur les dossiers

Sur le serveur, dans l’Explorateur :

### 10.1 Désactiver l’héritage (pour contrôler les ACL)

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
  - Comptes utilisateurs individuels (ex. `jiji`), pour ne garder que des **groupes** dans les ACL. 

### 10.2 Ajouter les groupes AD

Toujours sur `C:\Partages\IT` :  
1. Onglet **Sécurité** → **Modifier** → **Ajouter**.  
2. Ajouter le groupe `GG-IT`.  
3. Lui donner le droit **Modification** (ce qui inclut lecture/écriture/suppression).

Répéter pour les autres dossiers :  
- `C:\Partages\RH` → groupe `GG-RH` → **Modification**.  
- `C:\Partages\DIRECTION` → groupe `GG-DIRECTION` → **Modification** (ou plus restrictif selon le besoin).  

**Principe :**  
- Les utilisateurs n’apparaissent **jamais** directement dans les droits NTFS.  
- On donne les droits aux **groupes AD**, puis on gère les users dans les groupes. 

***

## 11. Créer les partages réseau

Toujours sur le serveur, par exemple pour `C:\Partages\IT` :

1. Clic droit sur `C:\Partages\IT` → **Propriétés** → onglet **Partage**.  
2. Bouton **Partage avancé**.  
3. Cocher **Partager ce dossier**.  
4. Nom du partage :  
   - `IT` (ou `IT$` pour un partage caché).
5. Bouton **Autorisations** (autorisations de **partage**) :  
   - En lab, tu peux laisser `Tout le monde : Contrôle total` et **te reposer sur NTFS** pour la sécurité fine. 

Répéter :  
- `C:\Partages\RH` → partage `RH` / `RH$`.  
- `C:\Partages\DIRECTION` → partage `DIRECTION` / `DIRECTION$`.  

**Rappel :**  
- **NTFS** (onglet Sécurité) = vraie limite de sécurité.  
- **Partage** (onglet Partage) = porte d’entrée réseau, souvent plus large, filtrage fin en NTFS.
  
***

## 12. Tester les droits depuis un poste client

Depuis un PC **joint au domaine** :

### 12.1 Test d’accès pour un user autorisé

1. Se connecter avec un user membre de `GG-IT` (ex. `user.it1`). 
2. Ouvrir l’explorateur → dans la barre d’adresse :  
   - `\\NOM_DU_SERVEUR\IT`  
3. Vérifier :  
   - Le dossier s’ouvre.  
   - On peut créer un fichier (Nouveau → Document texte).  
   - On peut modifier et supprimer ce fichier.
     
### 12.2 Test de blocage pour un user non autorisé

1. Se connecter avec un user qui n’est **pas** dans `GG-IT` (par ex. user RH).  
2. Essayer `\\NOM_DU_SERVEUR\IT`.  
3. Résultat attendu :  
   - Accès refusé ou impossibilité d’écrire/modifier.

Ce double test valide que ta **gestion par groupes AD + NTFS** fonctionne comme prévu.

***

