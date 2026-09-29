# Infrastructure WiFi d’entreprise sécurisée

## 802.1X, Active Directory, FreeRADIUS, Cisco WLC et haute disponibilité

Ce projet présente la conception, le déploiement et la validation d’une
infrastructure WiFi d’entreprise sécurisée basée sur l’authentification
individuelle des utilisateurs Active Directory.

L’objectif est de remplacer un WiFi utilisant une clé partagée par une
architecture centralisée reposant sur WPA2-Enterprise, IEEE 802.1X,
FreeRADIUS, Active Directory et un contrôleur WiFi Cisco.

> Toutes les adresses IP, noms DNS, noms d’utilisateurs, noms de machines,
> identifiants WiFi et secrets présents dans ce dépôt sont anonymisés.
> Ils ne correspondent pas à une infrastructure réelle.

---

## Objectifs du projet

- Authentifier les utilisateurs WiFi avec leurs comptes Active Directory.
- Remplacer une clé WiFi partagée par une authentification individuelle.
- Utiliser WPA2-Enterprise et IEEE 802.1X.
- Mettre en œuvre PEAP avec EAP-MSCHAPv2.
- Valider l’authentification AD avec Samba, Winbind et `ntlm_auth`.
- Utiliser une PKI interne pour valider l’identité des serveurs RADIUS.
- Déployer le profil WiFi Windows via une stratégie de groupe.
- Mettre en place deux serveurs FreeRADIUS indépendants.
- Tester la haute disponibilité RADIUS avec bascule entre les serveurs.
- Activer RADIUS Accounting pour tracer les sessions WiFi.
- Préparer la supervision et la centralisation future des logs.

---

## Architecture

```text
Windows Client / Mobile Device
          │
          │ WPA2-Enterprise / IEEE 802.1X
          │ PEAP / EAP-MSCHAPv2
          ▼
Cisco Access Points
          │
          │ CAPWAP
          ▼
Cisco Wireless LAN Controller
          │
          ├── RADIUS Authentication — UDP 1812
          │
          ▼
┌───────────────────────┐        ┌───────────────────────┐
│ FreeRADIUS 01         │        │ FreeRADIUS 02         │
│ 10.20.20.11           │        │ 10.20.20.12           │
│ radius01.example.local│        │ radius02.example.local│
└───────────┬───────────┘        └───────────┬───────────┘
            │                                │
            └──────────────┬─────────────────┘
                           │
                           │ Samba / Winbind / ntlm_auth
                           ▼
              ┌──────────────────────────┐
              │ Active Directory         │
              │ dc01.example.local       │
              │ 10.20.10.10              │
              └──────────────────────────┘

Cisco WLC
   │
   └── RADIUS Accounting — UDP 1813
                │
                ▼
      FreeRADIUS Accounting Logs
      → Session Start
      → Interim Update
      → Session Stop
```

---

## Technologies utilisées

| Domaine | Technologies |
|---|---|
| Système d’exploitation | Debian Linux |
| Identité | Active Directory |
| Authentification réseau | RADIUS / IEEE 802.1X |
| Serveur RADIUS | FreeRADIUS |
| Méthode EAP | PEAP |
| Authentification interne | EAP-MSCHAPv2 |
| Intégration AD | Samba, Winbind, ntlm_auth |
| Annuaire sécurisé | LDAP over TLS / LDAPS |
| PKI | Autorité de certification interne |
| WiFi | Cisco WLC / CAPWAP Access Points |
| Sécurité WiFi | WPA2-Enterprise / AES-CCMP |
| Déploiement poste client | Group Policy Object |
| Haute disponibilité | Deux serveurs FreeRADIUS indépendants |
| Traçabilité | RADIUS Accounting |
| Supervision prévue | Zabbix / Wazuh |

---

## Flux d’authentification

```text
1. Le poste détecte le SSID CORP-SECURE.

2. Le poste démarre une authentification IEEE 802.1X.

3. Le WLC Cisco transmet la requête RADIUS au serveur FreeRADIUS.

4. FreeRADIUS crée un tunnel PEAP chiffré en TLS.

5. Le poste valide le certificat du serveur RADIUS.

6. Le client transmet les éléments EAP-MSCHAPv2 dans le tunnel PEAP.

7. FreeRADIUS appelle ntlm_auth.

8. ntlm_auth utilise Winbind et Samba pour demander à Active Directory
   de valider l’authentification.

9. Active Directory accepte ou refuse l’utilisateur.

10. FreeRADIUS retourne Access-Accept ou Access-Reject au WLC.

11. Le WLC autorise ou refuse l’accès au WLAN.
```

---

## Rôles des composants

| Composant | Rôle |
|---|---|
| Supplicant | Poste Windows, smartphone ou tablette demandant l’accès WiFi |
| Authenticator | AP Cisco ou WLC Cisco ; contrôle l’accès réseau |
| Authentication Server | FreeRADIUS ; traite EAP et retourne la réponse RADIUS |
| Identity Store | Active Directory ; stocke comptes, groupes et identités |
| LDAP / LDAPS | Recherche d’utilisateurs, d’attributs et de groupes |
| Winbind / ntlm_auth | Validation de l’authentification EAP-MSCHAPv2 contre AD |
| PKI interne | Signature et validation des certificats RADIUS |
| GPO | Déploiement du certificat CA et du profil WiFi Windows |

---

## Résultats validés

- Authentification WiFi WPA2-Enterprise opérationnelle.
- IEEE 802.1X opérationnel.
- PEAP avec EAP-MSCHAPv2 validé.
- Validation des identifiants Active Directory avec Winbind et `ntlm_auth`.
- Validation du certificat serveur RADIUS sur un poste Windows.
- Déploiement du profil WiFi via GPO.
- Authentification utilisateur Active Directory validée.
- Deux serveurs FreeRADIUS indépendants intégrés au WLC.
- Bascule Authentication testée dans les deux sens.
- RADIUS Accounting activé.
- Réception et journalisation des événements :
  - `Accounting-Start`
  - `Accounting-Interim-Update`
  - `Accounting-Stop`
- Traçabilité des sessions WiFi : utilisateur, MAC, adresse IP, WLAN,
  point d’accès, durée et volumes de trafic.

---

## Documentation

| Document | Description |
|---|---|
| [Vue d’ensemble du projet](docs/01-project-overview.md) | Objectifs, périmètre et résultats |
| [Architecture](docs/02-architecture.md) | Réseau, composants et flux |
| [Déploiement FreeRADIUS](docs/03-freeradius-deployment.md) | Debian, réseau, UFW, DNS, NTP et prérequis |
| [Active Directory, LDAPS et Winbind](docs/04-active-directory-ldaps-winbind.md) | Kerberos, Samba, Winbind, LDAP et ntlm_auth |
| [PEAP et EAP-MSCHAPv2](docs/05-peap-mschapv2-authentication.md) | Certificats, EAP, mschap et inner-tunnel |
| [Cisco WLC](docs/06-cisco-wlc-configuration.md) | WLAN, WPA2-Enterprise et serveurs RADIUS |
| [GPO WiFi Windows](docs/07-windows-gpo-wifi-profile.md) | Certificat CA, profil WiFi et authentification utilisateur |
| [Haute disponibilité](docs/08-high-availability-failover.md) | FreeRADIUS 01/02 et tests de bascule |
| [RADIUS Accounting](docs/09-radius-accounting.md) | UDP 1813, logs et traçabilité |
| [Supervision et évolutions](docs/10-monitoring-and-future-improvements.md) | Zabbix, Wazuh et améliorations |
| [Dépannage](docs/11-troubleshooting.md) | Méthode de diagnostic par couche |

---

## Compétences démontrées

```text
Active Directory
LDAP / LDAPS
Kerberos
Samba
Winbind
ntlm_auth
FreeRADIUS
RADIUS
IEEE 802.1X
PEAP
EAP-MSCHAPv2
WPA2-Enterprise
Cisco Wireless LAN Controller
CAPWAP
PKI interne
Certificats TLS
Group Policy
Haute disponibilité
RADIUS Accounting
Linux Debian
UFW
DNS
NTP
Diagnostic réseau
Documentation technique
```

---

## Évolutions envisagées

- Migration vers WPA3-Enterprise lorsque l’infrastructure le permet.
- Déploiement EAP-TLS pour certains postes ou équipements sensibles.
- Politiques RADIUS basées sur les groupes Active Directory.
- VLAN dynamiques selon l’utilisateur ou le groupe.
- Supervision de FreeRADIUS, Winbind, certificats et WLC dans Zabbix.
- Centralisation des logs RADIUS, WLC et réseau dans Wazuh.
- Alertes sur les échecs d’authentification répétés.
- Gestion de la rétention des journaux Accounting.
- Automatisation de la configuration avec Ansible.

---

## Sécurité du dépôt

Ce dépôt ne contient volontairement aucun :

```text
Secret RADIUS réel
Mot de passe LDAP réel
Clé privée
Certificat interne réel
Fichier keytab
Fichier de secret Samba
Adresse IP publique
Nom de domaine interne réel
Utilisateur réel
Adresse MAC réelle
Capture d’écran non anonymisée
```

Les fichiers de configuration présents dans `examples/` utilisent des
placeholders tels que :

```text
<RADIUS_SHARED_SECRET>
<LDAP_SERVICE_ACCOUNT_DN>
<LDAP_SERVICE_PASSWORD>
<EXAMPLE_IP_ADDRESS>
```

---

## Licence

Ce projet est publié à des fins éducatives et de démonstration technique.

Les noms, adresses, utilisateurs, secrets, certificats et schémas ont été
anonymisés.
