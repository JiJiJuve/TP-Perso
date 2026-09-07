# Laboratoire – Sauvegarde et restauration d’un contrôleur de domaine Active Directory

## Sommaire

- [Présentation](#présentation)
- [Architecture du laboratoire](#architecture-du-laboratoire)
- [Installation et promotion du contrôleur de domaine](#installation-et-promotion-du-contrôleur-de-domaine)
- [Installation de Windows Server Backup](#installation-de-windows-server-backup)
- [Peuplement de l’annuaire Active Directory](#peuplement-de-lannuaire-active-directory)
- [Vérifications avant sauvegarde](#vérifications-avant-sauvegarde)
- [Configuration et test du partage NAS](#configuration-et-test-du-partage-nas)
- [Sauvegarde du System State](#sauvegarde-du-system-state)
- [Simulation de l’incident](#simulation-de-lincident)
- [Passage en mode DSRM](#passage-en-mode-dsrm)
- [Restauration du System State](#restauration-du-system-state)
- [Vérifications après restauration](#vérifications-après-restauration)
- [Résultat du laboratoire](#résultat-du-laboratoire)
- [Avertissements](#avertissements)

---

## Présentation

Ce laboratoire a pour objectif de mettre en place un environnement de test isolé permettant de :

- Déployer un contrôleur de domaine Windows Server
- Créer une forêt Active Directory de test
- Sauvegarder l’état système (System State) sur un NAS
- Simuler un incident (suppression d’OU et d’utilisateurs)
- Restaurer le contrôleur de domaine en mode DSRM
- Vérifier le retour des objets Active Directory supprimés

L’environnement utilisé est strictement isolé du réseau de production.

---

## Architecture du laboratoire

- **Nom du serveur** : `DC-TEST`
- **Système** : Windows Server 2019 Evaluation x64
- **Domaine** : `lab.test`
- **Adresse IP du DC** : `192.168.1.231/24`
- **Adresse IP du NAS** : `192.168.1.2/24`
- **Partage NAS** : `\\192.168.1.2\SauvegardeAD`
- **Dossier de sauvegarde** : `\\192.168.1.2\SauvegardeAD\SauvegardeAD-TEST`

![Configuration de la VM de test pour la restauration AD](Images/Config_VM_Test_Restauration_AD.png)

---

## Installation et promotion du contrôleur de domaine

Après l’installation de Windows Server 2019 :

- Renommage du serveur en `DC-TEST`
- Configuration d’une adresse IP fixe
- Installation des rôles **AD DS** et **DNS**
- Promotion du serveur en contrôleur de domaine
- Création de la forêt `lab.test`

![Promotion du contrôleur de domaine lab.test](Images/Promotion_DC_Lab_test.png)

![Configuration de base AD](Images/Check_conf_base_AD.png)

### Commandes clés et explications

Aucune commande spécifique n’est requise dans cette section au-delà de l’assistant graphique, mais les vérifications suivantes sont faites plus loin :

- `Get-ADDomain` : affiche les informations du domaine (nom DNS, DN, etc.)
- `Get-ADForest` : affiche les informations de la forêt Active Directory

---

## Installation de Windows Server Backup

Le rôle **Windows Server Backup** est installé afin de réaliser la sauvegarde de l’état système.

![Installation et vérification du rôle Windows Server Backup](Images/Installation_&_Check_role_Windows_Server_Backup.png)

### Commandes clés et explications

```powershell
Install-WindowsFeature Windows-Server-Backup
```
- Installe le rôle Windows Server Backup sur le serveur.

```powershell
Get-WindowsFeature Windows-Server-Backup
```
- Vérifie que le rôle Windows Server Backup est bien installé (doit afficher `[X]`).

```powershell
Get-Command wbadmin.exe
```
- Vérifie que l’outil en ligne de commande `wbadmin` (Windows Backup Admin) est disponible.

---

## Peuplement de l’annuaire Active Directory

L’annuaire est peuplé avec :

- Des unités d’organisation (OU)
- Des groupes de sécurité
- Des utilisateurs de test
- Une GPO de test

Les objets créés utilisent le préfixe `LAB-` pour les distinguer facilement.

Le peuplement a été réalisé à l’aide d’un script PowerShell dédié, qui crée notamment :

- Les OU : `LAB-Utilisateurs`, `LAB-Administratifs`, `LAB-Techniques`, `LAB-Groupes`, `LAB-Ordinateurs`
- Les groupes : `LAB-Admins`, `LAB-Users`, `LAB-IT`, `LAB-Test-GPO`
- Cinq utilisateurs de laboratoire
- La GPO `LAB - GPO Test` liée à l’OU `LAB-Utilisateurs`

👉 Script utilisé : [Scripts/Peuplement-AD.ps1](Images/Script_Powershell_Peuplement_ActiveDirectory.ps1)

![Vérification des comptes, groupes, GPO et OU](Images/Check_Comptes_Groupe_GPO_OU_AD.PNG)

![Vérification OK du peuplement AD (OU, groupes, utilisateurs, GPO)](Images/Check_OK_peuplement_AD.PNG)

---

## Vérifications avant sauvegarde

Avant de lancer la sauvegarde, les contrôles suivants sont effectués :

- État des services : `NTDS`, `DNS`, `Netlogon`
- Diagnostic Active Directory avec `dcdiag`
- Vérification des partages `SYSVOL` et `NETLOGON`

![Vérification des 3 services et dcdiag avant sauvegarde](Images/Extrait_test_avant_sauvegarde_3services_dcdiage_OK.PNG)

![Test et accès au partage NAS](Images/Test_partage_&_acces_NAS_OK.PNG)

### Commandes clés et explications

```powershell
Get-Service NTDS, DNS, Netlogon
```
- Affiche l’état des services critiques du contrôleur de domaine :
  - `NTDS` : service Active Directory
  - `DNS` : service DNS intégré à AD
  - `Netlogon` : service d’authentification et de réplication  
  Tous doivent être `Running`.

```powershell
dcdiag
```
- Lance un diagnostic complet du contrôleur de domaine (tests de santé AD, DNS, réplication, etc.).

```powershell
net share
```
- Liste les partages réseau du serveur.  
  Doit afficher notamment `SYSVOL` et `NETLOGON`, indispensables pour AD.

---

## Configuration et test du partage NAS

Le NAS est configuré avec :

- Adresse IP : `192.168.1.2`
- Partage : `\\192.168.1.2\SauvegardeAD`
- Compte : `admin`

Les tests de connectivité et d’accès sont réalisés depuis le contrôleur de domaine.

![Authentification auprès du partage NAS, vérification de l’accès et création du dossier](Images/Authentification_aupres_partage_NAS_verif_Acces_Creation_Dossier.PNG)

### Commandes clés et explications

```powershell
Test-NetConnection 192.168.1.2 -Port 445
```
- Teste la connectivité réseau vers le NAS sur le port SMB (445).  
  `TcpTestSucceeded : True` = le NAS est reachable.

```powershell
net use \\192.168.1.2\SauvegardeAD /user:admin *
```
- Ouvre une session SMB authentifiée vers le partage NAS avec le compte `admin`.  
  Le mot de passe est demandé de façon interactive.

```powershell
Test-Path "\\192.168.1.2\SauvegardeAD"
```
- Vérifie que le partage est accessible depuis PowerShell (retourne `True` ou `False`).

```powershell
New-Item -Path "\\192.168.1.2\SauvegardeAD\SauvegardeAD-TEST" -ItemType Directory
```
- Crée le dossier de destination pour les sauvegardes sur le NAS.

```powershell
Test-Path "\\192.168.1.2\SauvegardeAD\SauvegardeAD-TEST"
```
- Vérifie que le dossier de sauvegarde a bien été créé.

---

## Sauvegarde du System State

La sauvegarde de l’état système est lancée avec `wbadmin` :

```powershell
wbadmin start systemstatebackup -backuptarget:\\192.168.1.2\SauvegardeAD\SauvegardeAD-TEST -quiet
```

![Vérification avant lancement de la sauvegarde](Images/Check_backup_avant_lancement.PNG)

![Lancement de la sauvegarde System State](Images/extrait_lancement_sauvegarde.PNG)

La présence de la sauvegarde est vérifiée :

- En ligne de commande avec `wbadmin get versions`
- Via l’interface du NAS

![Présence de la sauvegarde AD en CLI (1)](Images/Extrait_Presence_Backup_AD_CLI.PNG)

![Présence de la sauvegarde AD en CLI (2)](Images/Extrait_Presence_Backup_AD_CLI_2.PNG)

![Présence de la sauvegarde sur le NAS (GUI)](Images/Extrait_Presence_Backup_NAS_GUI.png)

### Commandes clés et explications

```powershell
wbadmin start systemstatebackup -backuptarget:\\192.168.1.2\SauvegardeAD\SauvegardeAD-TEST -quiet
```
- Lance une sauvegarde de l’**état système** (System State) du contrôleur de domaine.  
  Cela inclut :
  - La base AD (`NTDS.dit`)
  - Le registre
  - SYSVOL
  - Les composants AD associés  
  `-quiet` = pas de confirmation interactive.

```powershell
wbadmin get status
```
- Affiche l’état d’avancement de la sauvegarde en cours.

```powershell
wbadmin get versions -backuptarget:\\192.168.1.2\SauvegardeAD\SauvegardeAD-TEST
```
- Liste les versions de sauvegarde disponibles sur le NAS.  
  Chaque version a un identifiant du type `09/03/2026-11:28` utilisé pour la restauration.

---

## Simulation de l’incident

Après validation de la sauvegarde, une OU contenant des utilisateurs est supprimée volontairement afin de simuler un incident Active Directory.

![Test de suppression d’une OU avant restauration](Images/Test_Suppression_OU_avant_Restauration.PNG)

---

## Passage en mode DSRM

Pour restaurer l’état système, le contrôleur de domaine est redémarré en mode **Directory Services Restore Mode (DSRM)** :

```powershell
bcdedit /set safeboot dsrepair
shutdown /r /t 0
```

![Check et passage en mode DSRM avant restauration](Images/Check_&_passage_mode_DSRM_avant_Restauration.PNG)

![Mode DSRM après redémarrage – OK](Images/Check_mode_DSRM_apres_Reddemarrage_OK.PNG)

En DSRM :

- Le service `NTDS` est arrêté
- Les commandes Active Directory ne fonctionnent pas
- La connexion se fait avec le compte `.\Administrateur` et le mot de passe DSRM

### Commandes clés et explications

```powershell
bcdedit /set safeboot dsrepair
```
- Configure le prochain démarrage en mode **DSRM** (réparation des services d’annuaire).

```powershell
shutdown /r /t 0
```
- Redémarre immédiatement le serveur (`/r`) sans délai (`/t 0`).

---

## Restauration du System State

La restauration est lancée avec la version de sauvegarde précédemment identifiée :

```powershell
wbadmin start systemstaterecovery -version:09/03/2026-11:28 -backuptarget:\\192.168.1.2\SauvegardeAD\SauvegardeAD-TEST -quiet
```

![Lancement de la restauration du DC](Images/Lancement_Restauration_DC.PNG)

Après la restauration, le serveur est redémarré, puis DSRM est désactivé :

```powershell
bcdedit /deletevalue safeboot
shutdown /r /t 0
```

![Sortie du mode DSRM](Images/sortie_mode_dsrm.PNG)

### Commandes clés et explications

```powershell
wbadmin start systemstaterecovery -version:09/03/2026-11:28 -backuptarget:\\192.168.1.2\SauvegardeAD\SauvegardeAD-TEST -quiet
```
- Restaure l’**état système** à partir de la version indiquée (`-version:…`).  
  Cela remet :
  - La base AD telle qu’à la sauvegarde
  - Le registre
  - SYSVOL
  - Les autres composants système sauvegardés  
  Doit être exécuté en **DSRM**.

```powershell
bcdedit /deletevalue safeboot
```
- Supprime l’option `safeboot dsrepair` pour que le prochain démarrage soit normal (plus en DSRM).

```powershell
shutdown /r /t 0
```
- Redémarre le serveur pour appliquer le changement et revenir en mode normal.

---

## Vérifications après restauration

Après redémarrage en mode normal, les contrôles suivants sont effectués :

- Services `NTDS`, `DNS`, `Netlogon` : état `Running`
- Partages `SYSVOL` et `NETLOGON` : présents
- Domaine `lab.test` : fonctionnel
- OU, groupes, utilisateurs supprimés : de nouveau présents
- GPO `LAB - GPO Test` : présente et liée

![Vérification après restauration – 1](Images/Check_apres_restauration_1.PNG)

![Vérification après restauration – 2](Images/Check_apres_restauration_2.PNG)

![Vérification après restauration – 3](Images/Check_apres_restauration_3.PNG)

![Vérification après restauration – 4](Images/Check_apres_restauration_4.PNG)

![Restauration OK – OU et comptes utilisateurs revenus](Images/Restauration_OK_OU_&_Comptes_user_revenus.png)

![Validation finale de la restauration](Images/Validation_Restau_OK.PNG)

### Commandes clés et explications

```powershell
bcdedit
```
- Affiche la configuration de démarrage.  
  Ne doit plus contenir `safeboot dsrepair` après la sortie de DSRM.

```powershell
Get-Service NTDS, DNS, Netlogon
```
- Vérifie que les services critiques du contrôleur de domaine sont bien démarrés (`Running`).

```powershell
net share
```
- Vérifie que les partages `SYSVOL` et `NETLOGON` sont de nouveau présents.

```powershell
Get-ADDomain
```
- Vérifie que le domaine `lab.test` est bien en place et fonctionnel.

```powershell
Get-ADForest
```
- Vérifie l’état de la forêt Active Directory.

```powershell
dcdiag
```
- Relance un diagnostic complet du contrôleur de domaine après restauration.

```powershell
dcdiag /test:dns
```
- Test spécifiquement la partie DNS liée à Active Directory.

```powershell
Get-ADOrganizationalUnit -Filter "Name -like 'LAB-*'"
```
- Liste les OU de laboratoire pour vérifier que l’OU supprimée est revenue.

```powershell
Get-ADUser -Filter *
```
- Liste les utilisateurs ; ceux de l’OU supprimée doivent être de retour.

```powershell
Get-ADGroup -Filter "Name -like 'LAB-*'"
```
- Vérifie que les groupes de laboratoire sont présents.

```powershell
Get-GPO -All
```
- Liste toutes les GPO ; `LAB - GPO Test` doit être présente.

---

## Résultat du laboratoire

**Résultat : SUCCÈS**

Le scénario complet a été validé :

- Création et promotion du contrôleur de domaine
- Installation de Windows Server Backup
- Peuplement de l’annuaire avec OU, groupes, utilisateurs et GPO
- Sauvegarde du System State sur le NAS
- Simulation d’un incident (suppression d’OU)
- Restauration en mode DSRM
- Retour des objets Active Directory supprimés
- Vérifications post‑restauration positives

---

## Avertissements

Ce projet concerne un environnement de laboratoire isolé.

Ne pas appliquer directement une restauration System State sur un contrôleur de domaine de production sans :

- Procédure validée
- Analyse d’impact
- Stratégie de restauration Active Directory adaptée
- Sauvegardes vérifiées et testées

Les identifiants NAS et DSRM ne doivent jamais être enregistrés dans les scripts ou poussés dans le dépôt Git.
