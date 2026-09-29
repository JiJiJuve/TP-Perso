# Concepts et protocoles utilisés

## Objectif

Ce document présente simplement les principaux protocoles, composants et
termes techniques utilisés dans l’infrastructure WiFi d’entreprise.

Il permet de comprendre la logique globale avant de suivre les documents
de déploiement, d’authentification, de haute disponibilité ou
d’Accounting.

---

## 1. WiFi Enterprise

Un réseau WiFi peut utiliser deux modèles de sécurité principaux.

### WiFi avec mot de passe partagé

Le modèle classique est généralement appelé :

```text
WPA2-Personal
ou
WPA3-Personal
```

Tous les utilisateurs possèdent la même clé WiFi.

Inconvénients :

```text
Une même clé est utilisée par plusieurs personnes.
Il est difficile d’identifier un utilisateur précis.
Lorsqu’un collaborateur quitte l’entreprise,
il faut généralement changer le mot de passe WiFi.
Le nouveau mot de passe doit être rediffusé sur les appareils.
```

### WiFi Enterprise

Le modèle professionnel utilisé dans ce projet est :

```text
WPA2-Enterprise
avec IEEE 802.1X
```

Chaque utilisateur utilise son propre compte Active Directory.

Avantages :

```text
Authentification individuelle.
Révocation simple d’un utilisateur.
Meilleure traçabilité.
Contrôle centralisé des accès.
Possibilité d’utiliser des groupes AD.
Possibilité de créer des politiques VLAN ou ACL.
Pas de mot de passe WiFi commun à diffuser.
```

---

## 2. IEEE 802.1X

IEEE 802.1X est un mécanisme de contrôle d’accès au réseau.

Un client ne reçoit pas un accès complet au réseau tant qu’il n’est pas
authentifié.

Trois rôles existent.

| Rôle | Description | Exemple dans ce projet |
|---|---|---|
| Supplicant | Client demandant l’accès réseau | PC Windows, smartphone, tablette |
| Authenticator | Équipement qui contrôle l’accès | Point d’accès Cisco ou WLC |
| Authentication Server | Serveur qui vérifie l’identité | FreeRADIUS |

La chaîne est la suivante :

```text
Client WiFi
→ demande un accès

WLC / AP Cisco
→ bloque ou autorise le trafic

FreeRADIUS
→ vérifie l’identité de l’utilisateur
→ retourne une réponse d’autorisation ou de refus
```

---

## 3. RADIUS

RADIUS signifie :

```text
Remote Authentication Dial-In User Service
```

C’est un protocole utilisé par les équipements réseau pour demander à un
serveur central si un utilisateur ou un appareil est autorisé à accéder
au réseau.

RADIUS repose sur le modèle AAA.

| Élément AAA | Rôle |
|---|---|
| Authentication | Vérifier l’identité de l’utilisateur ou de l’appareil |
| Authorization | Définir les droits, VLAN, ACL ou attributs d’accès |
| Accounting | Enregistrer les sessions et événements réseau |

Dans le projet :

```text
WLC Cisco
→ envoie une demande RADIUS

FreeRADIUS
→ vérifie l’identité auprès d’Active Directory

FreeRADIUS
→ répond Access-Accept ou Access-Reject

WLC Cisco
→ autorise ou refuse le WiFi
```

### Ports RADIUS

| Usage | Protocole | Port |
|---|---|---:|
| Authentication | UDP | 1812 |
| Accounting | UDP | 1813 |

---

## 4. Access-Request, Access-Accept et Access-Reject

Lors d’une authentification WiFi, plusieurs messages RADIUS sont échangés.

| Message | Signification |
|---|---|
| Access-Request | Le WLC demande à FreeRADIUS si le client est autorisé |
| Access-Challenge | FreeRADIUS demande des informations supplémentaires au client |
| Access-Accept | L’authentification est réussie ; le WLC peut ouvrir l’accès |
| Access-Reject | L’authentification est refusée |

Exemple simplifié :

```text
Poste Windows
→ WLC Cisco
→ Access-Request
→ FreeRADIUS
→ Active Directory

Active Directory valide l’utilisateur

FreeRADIUS
→ Access-Accept
→ WLC Cisco

WLC Cisco
→ accès WiFi autorisé
```

---

## 5. EAP

EAP signifie :

```text
Extensible Authentication Protocol
```

EAP est un cadre d’authentification. Il ne définit pas une seule méthode
d’authentification, mais permet d’utiliser plusieurs méthodes.

Exemples :

```text
PEAP + EAP-MSCHAPv2
EAP-TLS
EAP-TTLS
```

Dans ce projet, la méthode utilisée est :

```text
PEAP
→ EAP-MSCHAPv2
```

---

## 6. PEAP

PEAP signifie :

```text
Protected Extensible Authentication Protocol
```

PEAP crée un tunnel TLS chiffré entre le client WiFi et le serveur
FreeRADIUS.

```text
Poste Windows
→ tunnel TLS sécurisé
→ FreeRADIUS
```

Ce tunnel protège les échanges internes d’authentification.

PEAP nécessite un certificat serveur sur FreeRADIUS.

Le client Windows doit :

```text
Faire confiance à la CA interne.
Vérifier le certificat présenté par FreeRADIUS.
Vérifier que le nom du serveur correspond à un serveur RADIUS attendu.
```

---

## 7. TLS et certificats

TLS signifie :

```text
Transport Layer Security
```

TLS permet de chiffrer la communication entre un client et un serveur.

Dans ce projet, TLS est utilisé à deux endroits.

| Usage | Exemple |
|---|---|
| PEAP | Tunnel sécurisé entre le client WiFi et FreeRADIUS |
| LDAPS | Connexion sécurisée entre FreeRADIUS et Active Directory |

### PKI interne

Une PKI est une infrastructure de gestion de certificats.

```text
CA interne
→ signe les certificats des serveurs

Clients Windows
→ font confiance à la CA

FreeRADIUS
→ présente un certificat signé par la CA
```

Le certificat EAP d’un serveur RADIUS doit idéalement contenir :

```text
CN  = nom DNS du serveur RADIUS
SAN = nom DNS du serveur RADIUS
EKU = Server Authentication
```

Exemple :

```text
CN  = radius01.example.local
SAN = DNS:radius01.example.local
EKU = Server Authentication
```

---

## 8. EAP-MSCHAPv2

EAP-MSCHAPv2 est la méthode d’authentification utilisée à l’intérieur du
tunnel PEAP.

Elle permet à un utilisateur de s’authentifier avec son compte Active
Directory.

```text
Utilisateur Windows
→ identifiant et mot de passe AD

Poste Windows
→ calcule une réponse cryptographique

FreeRADIUS
→ ne reçoit pas simplement un mot de passe exploitable en clair

FreeRADIUS
→ demande à Active Directory de vérifier la réponse
```

Le mot de passe n’est pas envoyé directement en clair dans le flux
MS-CHAPv2.

---

## 9. Active Directory

Active Directory est l’annuaire Microsoft utilisé pour gérer :

```text
Utilisateurs
Groupes
Ordinateurs
Mots de passe
Stratégies de groupe
DNS intégré
Certificats et PKI
```

Dans ce projet, Active Directory est la source d’identité centrale.

```text
Utilisateur WiFi
→ compte Active Directory

FreeRADIUS
→ demande à AD de valider l’authentification

Active Directory
→ accepte ou refuse l’utilisateur
```

---

## 10. LDAP et LDAPS

LDAP signifie :

```text
Lightweight Directory Access Protocol
```

LDAP permet de rechercher des objets dans un annuaire, par exemple :

```text
Utilisateurs
Groupes
Attributs utilisateur
Ordinateurs
Unités d’organisation
```

LDAPS correspond à LDAP protégé par TLS.

```text
LDAP
→ généralement TCP 389

LDAPS
→ TCP 636
→ communication chiffrée
```

Dans ce projet, FreeRADIUS utilise LDAPS pour :

```text
Rechercher un utilisateur Active Directory.
Rechercher des groupes Active Directory.
Lire des attributs nécessaires aux règles d’autorisation.
```

### LDAP ne valide pas MS-CHAPv2

LDAP et MS-CHAPv2 ont des rôles différents.

```text
LDAP / LDAPS
→ recherche dans l’annuaire.

Winbind / ntlm_auth
→ validation réelle de l’authentification MS-CHAPv2.
```

Cette distinction est importante pour éviter de casser un flux
PEAP/EAP-MSCHAPv2 fonctionnel.

---

## 11. Kerberos

Kerberos est le protocole d’authentification principal utilisé par Active
Directory.

Il fonctionne avec des tickets plutôt qu’avec l’envoi répété de mots de
passe.

Dans ce projet, Kerberos est principalement utilisé pour :

```text
Joindre les serveurs Debian au domaine Active Directory.
Permettre à Samba de communiquer avec Active Directory.
Valider que DNS, heure et domaine sont cohérents.
```

Kerberos est sensible à l’heure.

```text
Un décalage important entre Debian et Active Directory
peut empêcher l’authentification.
```

C’est pourquoi NTP ou Chrony est nécessaire.

---

## 12. Samba, Winbind et ntlm_auth

### Samba

Samba permet à Linux d’interagir avec les services Windows et Active
Directory.

```text
Linux
→ Samba
→ Active Directory
```

### Winbind

Winbind est un composant Samba qui permet notamment à Linux de :

```text
Résoudre les utilisateurs Active Directory.
Résoudre les groupes Active Directory.
Vérifier le trust avec le domaine.
Interroger les SID Active Directory.
```

### ntlm_auth

`ntlm_auth` est l’outil qui sert de pont entre FreeRADIUS et Winbind.

```text
FreeRADIUS
→ module mschap
→ ntlm_auth
→ Winbind
→ Active Directory
```

C’est cette chaîne qui permet de valider EAP-MSCHAPv2 contre Active
Directory.

---

## 13. CAPWAP

CAPWAP signifie :

```text
Control And Provisioning of Wireless Access Points
```

CAPWAP est utilisé entre les points d’accès Cisco et le contrôleur WiFi.

```text
Point d’accès Cisco
→ CAPWAP
→ WLC Cisco
```

Le WLC centralise notamment :

```text
Configuration des WLAN.
Diffusion des SSID.
Paramètres de sécurité.
Serveurs RADIUS.
Gestion des points d’accès.
Informations sur les clients WiFi.
```

Les ports CAPWAP fréquemment utilisés sont :

```text
UDP 5246
UDP 5247
```

---

## 14. GPO

GPO signifie :

```text
Group Policy Object
```

Une GPO permet de déployer une configuration sur les ordinateurs ou
utilisateurs Active Directory.

Dans ce projet, une GPO permet de déployer :

```text
Le certificat de la CA interne.
Le profil WiFi.
Le SSID.
La méthode WPA2-Enterprise.
PEAP.
EAP-MSCHAPv2.
Les serveurs RADIUS approuvés.
La validation du certificat serveur.
```

Cela évite une configuration WiFi manuelle ordinateur par ordinateur.

---

## 15. Haute disponibilité RADIUS

La haute disponibilité évite qu’une panne d’un serveur FreeRADIUS bloque
toutes les nouvelles connexions WiFi.

```text
WLC Cisco
→ FreeRADIUS 01 : serveur primaire
→ FreeRADIUS 02 : serveur secondaire
```

Si le serveur primaire est indisponible :

```text
WLC
→ détecte l’absence de réponse
→ bascule vers le serveur secondaire
→ les nouvelles authentifications peuvent continuer
```

Les deux serveurs doivent être indépendants, mais cohérents sur leur
configuration fonctionnelle.

---

## 16. RADIUS Accounting

RADIUS Accounting permet de tracer les événements de session.

| Événement | Signification |
|---|---|
| Accounting-Start | Le client commence une session WiFi |
| Accounting-Interim-Update | Le client est toujours connecté |
| Accounting-Stop | Le client quitte le WiFi ou sa session se ferme |

L’Accounting permet notamment de retrouver :

```text
Utilisateur
Adresse MAC
Adresse IP
WLAN
Point d’accès
Heure de connexion
Heure de déconnexion
Durée de session
Volume de trafic
```

L’Accounting utilise généralement :

```text
UDP 1813
```

---

## 17. UFW

UFW signifie :

```text
Uncomplicated Firewall
```

UFW est l’outil de pare-feu simplifié souvent utilisé sur Debian et Ubuntu.

Dans ce projet, UFW permet notamment de :

```text
Refuser les connexions entrantes non nécessaires.
Autoriser SSH depuis le réseau d’administration.
Autoriser UDP 1812 depuis le WLC.
Autoriser UDP 1813 depuis le WLC.
```

Exemple de principe :

```text
Tout bloquer par défaut
→ n’autoriser que les flux nécessaires
```

---

## 18. Supervision et SIEM

La supervision permet de vérifier que les services sont disponibles.

Exemples de contrôles :

```text
Service FreeRADIUS actif.
Service Winbind actif.
Ports UDP 1812 et UDP 1813 en écoute.
Expiration prochaine des certificats.
Échec de jointure Active Directory.
Échecs RADIUS répétés.
Disponibilité WLC.
```

Un SIEM permet de centraliser et corréler les journaux.

Exemples d’évolutions prévues :

```text
Zabbix
→ supervision des services, ports et certificats.

Wazuh
→ centralisation des logs et détection d’événements de sécurité.
```

---

## Résumé de la chaîne complète

```text
Utilisateur Windows
→ sélectionne le SSID sécurisé

Client WiFi
→ démarre IEEE 802.1X

WLC Cisco
→ transmet RADIUS UDP 1812

FreeRADIUS
→ établit le tunnel PEAP/TLS

EAP-MSCHAPv2
→ transmet les éléments d’authentification internes

mschap
→ appelle ntlm_auth

ntlm_auth
→ appelle Winbind

Winbind
→ interroge Active Directory

Active Directory
→ accepte ou refuse l’utilisateur

FreeRADIUS
→ retourne Access-Accept ou Access-Reject

WLC Cisco
→ autorise ou refuse l’accès WiFi

WLC Cisco
→ envoie ensuite les événements Accounting UDP 1813
```
