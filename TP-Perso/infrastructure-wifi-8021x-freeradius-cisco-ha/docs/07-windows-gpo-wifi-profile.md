# Déploiement du profil WiFi Windows par GPO

## Objectif

Cette procédure décrit le déploiement centralisé d’un profil WiFi
d’entreprise sur les postes Windows joints au domaine Active Directory.

Le profil utilise :

```text
SSID : CORP-SECURE
Sécurité : WPA2-Enterprise
Chiffrement : AES-CCMP
Authentification : PEAP
Méthode interne : EAP-MSCHAPv2
Annuaire : Active Directory
Serveurs RADIUS : radius01.example.local et radius02.example.local
CA interne : CORP-ROOT-CA
```

Le déploiement par GPO permet d’éviter une configuration manuelle poste
par poste.

---

## 1. Objectifs de la GPO WiFi

La GPO doit permettre aux postes Windows de :

```text
Faire confiance à la CA interne.
Valider le certificat présenté par FreeRADIUS.
Détecter automatiquement le SSID CORP-SECURE.
Utiliser WPA2-Enterprise.
Utiliser PEAP.
Utiliser EAP-MSCHAPv2.
S’authentifier avec un compte Active Directory valide.
Se connecter automatiquement lorsque le réseau est à portée.
```

Architecture :

```text
GPO Certificat CA
→ installe CORP-ROOT-CA sur les postes Windows

GPO WiFi
→ déploie le profil CORP-SECURE

Poste Windows
→ valide le certificat RADIUS
→ établit PEAP
→ s’authentifie avec Active Directory
```

---

## 2. Prérequis

Avant de créer ou de lier la GPO WiFi, vérifier :

```text
La CA interne est disponible.
Les certificats RADIUS sont valides.
Les certificats RADIUS contiennent un FQDN cohérent.
Le DNS résout radius01.example.local.
Le DNS résout radius02.example.local.
Le SSID CORP-SECURE est actif sur le WLC.
Les deux serveurs RADIUS sont actifs.
Le poste pilote est joint au domaine.
Le poste pilote peut recevoir des GPO.
Une OU de test existe.
```

Exemple de poste pilote :

```text
WIN11-TEST-01
```

Ne pas lier immédiatement la GPO à tous les ordinateurs de production.

---

## 3. Déployer la CA interne par GPO

### 3.1 Objectif

Avant de déployer le profil WiFi, les postes Windows doivent faire
confiance à la CA qui a signé les certificats EAP de FreeRADIUS.

Exemple de CA :

```text
CORP-ROOT-CA
```

### 3.2 Ouvrir la gestion des GPO

Sur un contrôleur de domaine ou poste d’administration :

```text
Win + R
→ gpmc.msc
```

Puis naviguer :

```text
Forêt : example.local
→ Domaines
→ example.local
→ Objets de stratégie de groupe
```

Créer une nouvelle GPO, ou utiliser une GPO existante de déploiement
des certificats.

Exemple de nom :

```text
GPO - Certificat CA interne
```

### 3.3 Modifier la GPO

Clic droit sur la GPO :

```text
Modifier
```

Naviguer :

```text
Configuration ordinateur
→ Stratégies
→ Paramètres Windows
→ Paramètres de sécurité
→ Stratégies de clé publique
→ Autorités de certification racines de confiance
```

Clic droit :

```text
Importer
```

Sélectionner le certificat public de la CA interne.

Exemple :

```text
CORP-ROOT-CA.crt
```

### 3.4 Vérifier le certificat sur le poste pilote

Sur le poste Windows pilote :

```text
Win + R
→ certlm.msc
```

Naviguer :

```text
Certificats - Ordinateur local
→ Autorités de certification racines de confiance
→ Certificats
```

Le certificat de la CA interne doit apparaître.

Vérification PowerShell possible :

```powershell
Get-ChildItem Cert:\LocalMachine\Root |
Where-Object { $_.Subject -match "CORP-ROOT-CA" } |
Select-Object Subject, Issuer, NotAfter, Thumbprint
```

---

## 4. Créer une GPO WiFi de test

Dans `gpmc.msc` :

```text
Forêt : example.local
→ Domaines
→ example.local
→ Objets de stratégie de groupe
→ clic droit
→ Nouveau
```

Nom recommandé :

```text
GPO - WiFi - CORP-SECURE - UserAuth - TEST
```

Description :

```text
Déploiement pilote du profil WiFi WPA2-Enterprise CORP-SECURE
avec authentification utilisateur Active Directory.
```

Cette GPO doit être utilisée d’abord sur une OU de test contenant un
seul ordinateur pilote.

---

## 5. Ouvrir la stratégie WiFi

Clic droit sur la GPO créée :

```text
Modifier
```

Naviguer :

```text
Configuration ordinateur
→ Stratégies
→ Paramètres Windows
→ Paramètres de sécurité
→ Stratégies de réseau sans fil IEEE 802.11
```

Clic droit :

```text
Nouvelle stratégie de réseau sans fil pour Windows Vista
et versions ultérieures
```

Renseigner :

```text
Nom :
WiFi - CORP-SECURE

Description :
Déploiement du profil WiFi 802.1X CORP-SECURE par GPO
```

Activer l’option :

```text
Utiliser le service de configuration automatique
de réseau WLAN Windows pour les clients
```

---

## 6. Créer le profil WiFi

Dans la stratégie WiFi créée :

```text
Ajouter
→ Créer un nouveau profil réseau sans fil
```

Renseigner les paramètres de connexion.

| Paramètre | Valeur |
|---|---|
| Nom du profil | `CORP-SECURE` |
| Nom du réseau / SSID | `CORP-SECURE` |
| Type de réseau | Basé sur un point d’accès / Infrastructure |
| Connexion automatique | Activée |
| Connexion à un réseau non diffusé | Désactivée |
| Réseau favori prioritaire | Désactivé |

Le réseau est de type :

```text
Infrastructure
```

Ne pas sélectionner :

```text
Ad hoc
```

La connexion à un réseau non diffusé n’est pas nécessaire si le SSID est
diffusé par le WLC.

---

## 7. Configurer la sécurité WPA2-Enterprise

Dans le profil WiFi :

```text
Onglet Sécurité
```

Configurer :

| Paramètre | Valeur |
|---|---|
| Type de sécurité | WPA2-Enterprise |
| Type de chiffrement | AES-CCMP |
| Méthode d’authentification réseau | Microsoft : Protected EAP (PEAP) |

Ne pas sélectionner :

```text
WPA2-Personal
WEP
TKIP
EAP-MD5
```

PEAP doit être visible sous la forme :

```text
Microsoft : Protected EAP (PEAP)
```

Cliquer ensuite sur :

```text
Propriétés
```

---

## 8. Configurer PEAP

Dans les propriétés PEAP, activer :

```text
Vérifier l’identité du serveur en validant le certificat
```

Cette option est obligatoire pour empêcher les clients de se connecter à
un faux serveur RADIUS.

Activer :

```text
Se connecter à ces serveurs
```

Renseigner les serveurs RADIUS autorisés :

```text
radius01.example.local;radius02.example.local
```

Les noms sont séparés par un point-virgule.

Sélectionner la CA racine approuvée :

```text
CORP-ROOT-CA
```

Dans la méthode d’authentification, sélectionner :

```text
Mot de passe sécurisé (EAP-MSCHAP v2)
```

Activer si disponible :

```text
Activer la reconnexion rapide
```

Résumé attendu :

```text
Validation du certificat serveur : activée
Serveurs RADIUS autorisés : radius01.example.local;radius02.example.local
CA racine : CORP-ROOT-CA
Méthode interne : EAP-MSCHAPv2
Reconnexion rapide : activée
```

---

## 9. Configurer EAP-MSCHAPv2

Dans les propriétés de :

```text
Mot de passe sécurisé (EAP-MSCHAP v2)
```

Ne pas cocher automatiquement :

```text
Utiliser automatiquement mon nom d’ouverture de session Windows,
mon mot de passe et mon domaine éventuel
```

Dans cette procédure, la case reste décochée.

Comportement attendu :

```text
Première connexion WiFi
→ Windows peut demander les identifiants Active Directory.

Connexions suivantes du même utilisateur
→ Windows peut réutiliser les informations mémorisées.

Changement d’utilisateur Windows
→ une nouvelle authentification peut être demandée.

Suppression du profil ou des informations mémorisées
→ une nouvelle authentification peut être demandée.
```

---

## 10. Choisir le mode d’authentification

Dans les paramètres avancés du profil WiFi, choisir :

```text
Authentification de l’utilisateur
```

Ne pas sélectionner pour ce profil utilisateur :

```text
Authentification de l’utilisateur ou de l’ordinateur
```

Objectif :

```text
Le journal FreeRADIUS doit afficher l’identité utilisateur.

Exemple souhaité :
user.test

Au lieu d’une identité machine :
host/win11-test-01.example.local
```

Définir le nombre maximal d’échecs à :

```text
3
```

Activer la mise en cache des informations destinées aux connexions futures
si l’option est disponible.

---

## 11. Lier la GPO à une OU pilote

Créer ou identifier une OU de test.

Exemple :

```text
example.local
→ Workstations
→ WiFi-Test
```

Déplacer uniquement le poste pilote dans cette OU :

```text
WIN11-TEST-01
```

Dans `gpmc.msc` :

```text
Clic droit sur l’OU WiFi-Test
→ Lier un objet de stratégie de groupe existant
→ sélectionner :
GPO - WiFi - CORP-SECURE - UserAuth - TEST
```

Ne pas lier la GPO à la racine du domaine tant que le test pilote n’est
pas validé.

---

## 12. Appliquer la GPO sur le poste pilote

Sur `WIN11-TEST-01`, ouvrir un terminal administrateur.

Forcer l’application des GPO :

```cmd
gpupdate /force
```

Redémarrer le poste :

```cmd
shutdown /r /t 0
```

Après redémarrage, vérifier les GPO appliquées :

```cmd
gpresult /r
```

Ou générer un rapport détaillé :

```cmd
gpresult /h C:\Temp\gpresult-wifi.html
```

Vérifier la présence du profil WiFi :

```cmd
netsh wlan show profiles
```

Résultat attendu :

```text
CORP-SECURE
```

---

## 13. Vérifier la configuration WiFi Windows

Afficher les paramètres du profil :

```cmd
netsh wlan show profile name="CORP-SECURE"
```

Vérifier notamment :

```text
SSID : CORP-SECURE
Authentification : WPA2-Enterprise
Chiffrement : AES-CCMP
Méthode EAP : PEAP
Méthode interne : EAP-MSCHAPv2
```

Vérifier l’état WiFi :

```cmd
netsh wlan show interfaces
```

Le profil doit apparaître lorsque le poste est connecté.

---

## 14. Tester l’authentification utilisateur

Sur le poste pilote :

```text
1. Vérifier que le SSID CORP-SECURE est visible.
2. Se connecter au SSID.
3. Saisir les identifiants Active Directory si Windows les demande.
4. Attendre l’établissement de la connexion.
5. Vérifier l’adresse IP reçue.
6. Vérifier la passerelle.
7. Vérifier DNS.
8. Vérifier l’accès aux ressources autorisées.
```

Côté FreeRADIUS :

```bash
journalctl -fu freeradius
```

Ou, pendant une fenêtre de test :

```bash
systemctl stop freeradius
freeradius -X
```

Rechercher :

```text
User-Name = "user.test"
PEAP Session established
MS-CHAP authentication succeeded
EAP: Sending EAP Success
Sent Access-Accept
```

Après le test debug :

```text
Ctrl + C
```

Puis :

```bash
systemctl start freeradius
systemctl is-active freeradius
```

Résultat attendu :

```text
active
```

---

## 15. Dépannage GPO et WiFi

| Symptôme | Vérification |
|---|---|
| La GPO n’est pas appliquée | `gpresult /r`, OU, lien GPO, filtrage sécurité |
| Profil WiFi absent | `netsh wlan show profiles`, stratégie 802.11 |
| CA absente | `certlm.msc`, GPO certificat, `gpupdate /force` |
| Erreur certificat PEAP | CA, CN/SAN, serveurs RADIUS approuvés |
| Demande d’identifiants répétée | Cache, utilisateur Windows, paramètres EAP-MSCHAPv2 |
| Authentification machine au lieu d’utilisateur | Mode d’authentification du profil GPO |
| Access-Reject FreeRADIUS | Winbind, ntlm_auth, utilisateur AD, groupe, mot de passe |
| Access-Accept sans accès réseau | DHCP, VLAN, passerelle, DNS, firewall |
| Le SSID n’est pas visible | WLC, AP, diffusion SSID, WLAN activé |

---

## 16. Déploiement progressif

Après validation sur le poste pilote :

```text
1. Ajouter un deuxième poste de test.
2. Vérifier l’application de la GPO.
3. Vérifier les logs FreeRADIUS.
4. Vérifier l’accès réseau.
5. Étendre la GPO à une OU pilote plus large.
6. Surveiller les Access-Reject.
7. Documenter les problèmes éventuels.
8. Étendre progressivement à la production.
```

Ne pas déployer immédiatement à tous les ordinateurs du domaine.

---

## Étape suivante

Poursuivre avec :

```text
docs/08-high-availability-failover.md
```

Cette prochaine fiche couvre :

```text
Déclaration de deux serveurs FreeRADIUS.
Fonctionnement primaire / secondaire.
Maintenance sans coupure.
Tests de bascule dans les deux sens.
Validation de la haute disponibilité RADIUS.
```
