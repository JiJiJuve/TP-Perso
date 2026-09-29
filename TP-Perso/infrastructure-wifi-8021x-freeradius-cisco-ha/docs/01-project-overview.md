# Vue d’ensemble du projet

## Contexte

Ce projet documente le déploiement d’une infrastructure WiFi d’entreprise
sécurisée basée sur l’authentification individuelle des utilisateurs.

L’objectif initial était de remplacer un modèle de mot de passe WiFi
partagé par une architecture centralisée intégrée à Active Directory.

Le projet combine infrastructure réseau, administration Linux, gestion
des identités, PKI, sécurité WiFi, haute disponibilité et traçabilité
des sessions.

---

## Objectifs métier et sécurité

L’infrastructure a été conçue pour répondre aux objectifs suivants :

- Remplacer un mot de passe WiFi partagé par une authentification
  individuelle.
- Réutiliser les comptes utilisateurs Active Directory existants.
- Centraliser le contrôle d’accès WiFi.
- Valider l’identité des serveurs RADIUS via une PKI interne.
- Empêcher les utilisateurs de se connecter à un serveur RADIUS non
  approuvé ou malveillant.
- Fournir un service d’authentification redondant.
- Réduire l’impact d’une panne d’un serveur FreeRADIUS.
- Enregistrer les événements de session WiFi pour le dépannage et la
  traçabilité.
- Préparer l’environnement pour une future supervision et intégration
  SIEM.

---

## Périmètre

Le projet couvre les composants suivants :

```text
Clients Windows
Points d’accès Cisco
Contrôleur WiFi Cisco
WPA2-Enterprise
IEEE 802.1X
FreeRADIUS sur Debian
Active Directory
Kerberos
Samba
Winbind
ntlm_auth
LDAP over TLS
PKI interne
PEAP
EAP-MSCHAPv2
Group Policy Windows
Haute disponibilité RADIUS
RADIUS Accounting
```

## Défis techniques

Plusieurs défis techniques ont été résolus pendant le déploiement.

### Intégration à Active Directory

FreeRADIUS doit valider les demandes d’authentification WiFi contre
Active Directory sans exposer les mots de passe utilisateurs.

La solution utilise :

```text
FreeRADIUS
→ module mschap
→ ntlm_auth
→ Winbind
→ Samba
→ Active Directory
```

LDAP over TLS est utilisé pour les requêtes sécurisées dans l’annuaire,
telles que la recherche d’utilisateurs et de groupes. LDAP n’est pas
utilisé comme remplacement de la validation MS-CHAPv2.

---

### Validation du certificat

PEAP repose sur un tunnel TLS entre le client et le serveur RADIUS.

Les clients Windows doivent faire confiance à l’autorité de certification
interne et vérifier l’identité attendue du serveur RADIUS.

Ce projet inclut :

```text
Déploiement d’une CA racine interne
Validation du certificat serveur RADIUS
Configuration de la confiance sur les clients Windows
Déploiement du certificat CA par GPO
Déploiement du profil WiFi par GPO
```

---

### Haute disponibilité

Un seul serveur RADIUS crée une dépendance critique pour le WiFi
d’entreprise.

Deux serveurs FreeRADIUS indépendants sont configurés dans le WLC Cisco :

```text
Serveur RADIUS primaire
→ FreeRADIUS 01

Serveur RADIUS secondaire
→ FreeRADIUS 02
```

La bascule d’authentification a été testée en désactivant temporairement
chaque serveur et en validant que le serveur restant pouvait authentifier
un client WiFi réel.

---

### Traçabilité des sessions

L’authentification confirme si l’accès est autorisé.

RADIUS Accounting fournit des informations complémentaires sur la session :

```text
Identité de l’utilisateur
Adresse MAC du client
Adresse IP du client
Identifiant WLAN
Identifiant de l’infrastructure WiFi
Heure de début de session
Heure de fin de session
Durée de session
Compteurs de trafic
```

Ces données pourront être centralisées dans un SIEM.

---

## Résultats validés

Les résultats suivants ont été validés pendant le projet :

```text
Authentification WiFi WPA2-Enterprise
Authentification IEEE 802.1X
Établissement du tunnel PEAP
Authentification EAP-MSCHAPv2
Validation des utilisateurs Active Directory
Intégration Samba et Winbind
Validation ntlm_auth
Validation du certificat serveur RADIUS
Déploiement du profil WiFi par GPO Windows
Authentification utilisateur
Réponse RADIUS Access-Accept
Réception de RADIUS Accounting
Événements Accounting Start et Stop
Bascule d’authentification de RADIUS 01 vers RADIUS 02
Bascule d’authentification de RADIUS 02 vers RADIUS 01
```

---

## Structure de la documentation

| Document | Objectif |
|---|---|
| `01-project-overview.md` | Contexte, objectifs, périmètre et résultats |
| `02-architecture.md` | Composants, modèle d’adressage et flux |
| `03-freeradius-deployment.md` | Debian, réseau, DNS, NTP, firewall et installation |
| `04-active-directory-ldaps-winbind.md` | AD, Kerberos, LDAPS, Samba, Winbind et ntlm_auth |
| `05-peap-mschapv2-authentication.md` | EAP, PEAP, certificats, mschap et inner-tunnel |
| `06-cisco-wlc-configuration.md` | WLAN, 802.1X et intégration RADIUS |
| `07-windows-gpo-wifi-profile.md` | Confiance CA et déploiement du profil WiFi |
| `08-high-availability-failover.md` | Redondance RADIUS et validation de la bascule |
| `09-radius-accounting.md` | Accounting, journaux et traçabilité des sessions |
| `10-monitoring-and-future-improvements.md` | Supervision, SIEM et améliorations futures |
| `11-troubleshooting.md` | Méthode de diagnostic et problèmes courants |

---

## Avertissement de sécurité

Tous les noms, adresses IP, utilisateurs, domaines, secrets, certificats
et identifiants d’infrastructure utilisés dans ce dépôt sont anonymisés.

Aucune donnée sensible n’est incluse :

```text
Secret RADIUS réel
Mot de passe LDAP réel
Clé privée
Bundle de certificats
Fichier
