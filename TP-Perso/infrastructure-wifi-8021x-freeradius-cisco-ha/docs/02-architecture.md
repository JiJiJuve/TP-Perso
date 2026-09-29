# Architecture technique

## Vue d’ensemble

L’infrastructure repose sur une authentification WiFi d’entreprise
centralisée avec Active Directory, FreeRADIUS et un contrôleur WiFi Cisco.

Les clients se connectent au SSID sécurisé. Le contrôleur WiFi transmet
les requêtes d’authentification aux serveurs FreeRADIUS. FreeRADIUS
valide ensuite les identifiants utilisateurs auprès d’Active Directory.

```text
Client WiFi
    │
    │ WPA2-Enterprise / IEEE 802.1X
    │ PEAP / EAP-MSCHAPv2
    ▼
Points d’accès Cisco
    │
    │ CAPWAP
    ▼
Cisco Wireless LAN Controller
    │
    ├── RADIUS Authentication — UDP 1812
    │
    ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│ FreeRADIUS 01            │      │ FreeRADIUS 02            │
│ radius01.example.local   │      │ radius02.example.local   │
│ 10.20.20.11              │      │ 10.20.20.12              │
└─────────────┬────────────┘      └─────────────┬────────────┘
              │                                 │
              └──────────────┬──────────────────┘
                             │
                             │ Samba / Winbind / ntlm_auth
                             ▼
              ┌──────────────────────────────┐
              │ Active Directory             │
              │ dc01.example.local           │
              │ 10.20.10.10                  │
              │                              │
              │ dc02.example.local           │
              │ 10.20.10.11                  │
              └──────────────────────────────┘

Cisco WLC
    │
    └── RADIUS Accounting — UDP 1813
                    │
                    ▼
      FreeRADIUS Accounting Logs
```

---

## Segmentation logique

| Zone | Sous-réseau d’exemple | Composants |
|---|---|---|
| Infrastructure Active Directory | `10.20.10.0/24` | DC, DNS, LDAPS, PKI |
| Services RADIUS | `10.20.20.0/24` | FreeRADIUS 01 et 02 |
| Infrastructure WiFi | `10.20.30.0/24` | WLC, AP et administration WiFi |
| Réseau clients WiFi | `10.20.40.0/24` | Postes et équipements connectés |
| Administration | `10.20.99.0/24` | Administration SSH, VMware et supervision |

> Les adresses de cette documentation sont des exemples anonymisés.
> Elles ne correspondent pas à une infrastructure réelle.

---

## Composants

| Composant | Exemple de nom | Exemple d’adresse | Rôle |
|---|---|---:|---|
| Contrôleur de domaine principal | `dc01.example.local` | `10.20.10.10` | Active Directory, DNS, LDAPS et PKI |
| Contrôleur de domaine secondaire | `dc02.example.local` | `10.20.10.11` | Redondance Active Directory et DNS |
| FreeRADIUS primaire | `radius01.example.local` | `10.20.20.11` | RADIUS Authentication et Accounting |
| FreeRADIUS secondaire | `radius02.example.local` | `10.20.20.12` | Redondance RADIUS Authentication et Accounting |
| WLC Cisco | `wlc01.example.local` | `10.20.30.10` | Gestion des AP, WLAN et RADIUS |
| Points d’accès Cisco | `ap01`, `ap02`, etc. | Réseau WiFi | Diffusion du SSID et accès radio |
| Poste Windows pilote | `WIN11-TEST-01` | Réseau clients WiFi | Test de la GPO et de 802.1X |

---

## Flux réseau

### Authentification WiFi

```text
Poste Windows
→ WLC Cisco
→ FreeRADIUS
→ ntlm_auth / Winbind
→ Active Directory
→ Access-Accept ou Access-Reject
```

| Source | Destination | Protocole | Port | Utilité |
|---|---|---|---:|---|
| Client WiFi | AP / WLC | IEEE 802.1X / EAPOL | N/A | Échange d’authentification WiFi |
| AP Cisco | WLC Cisco | CAPWAP | UDP 5246 / 5247 | Gestion et contrôle des points d’accès |
| WLC Cisco | FreeRADIUS 01/02 | RADIUS Authentication | UDP 1812 | Demande et réponse d’authentification |
| FreeRADIUS 01/02 | Active Directory | LDAPS | TCP 636 | Recherche utilisateur et groupes |
| FreeRADIUS 01/02 | Active Directory | Kerberos | TCP/UDP 88 | Authentification et jointure au domaine |
| FreeRADIUS 01/02 | Active Directory | DNS | TCP/UDP 53 | Résolution des noms AD |
| FreeRADIUS 01/02 | Active Directory | SMB/RPC | Selon services AD | Samba, Winbind et opérations domaine |
| Administration | FreeRADIUS 01/02 | SSH | TCP 22 | Administration sécurisée |

---

## Flux RADIUS Accounting

L’Accounting complète l’authentification en traçant les événements
de session WiFi.

```text
WLC Cisco
→ UDP 1813
→ FreeRADIUS
→ Journaux Accounting
```

Les événements principaux sont :

```text
Accounting-Start
→ début de connexion WiFi

Accounting-Interim-Update
→ mise à jour périodique éventuelle

Accounting-Stop
→ fin de connexion WiFi
```

Les journaux permettent notamment d’identifier :

```text
Utilisateur RADIUS
Adresse MAC du client
Adresse IP attribuée
WLAN utilisé
Point d’accès ou radio concernée
Durée de session
Volume de trafic
```

---

## Haute disponibilité

Le WLC Cisco possède deux serveurs RADIUS.

```text
Serveur primaire
→ FreeRADIUS 01
→ 10.20.20.11

Serveur secondaire
→ FreeRADIUS 02
→ 10.20.20.12
```

Le comportement attendu est :

```text
FreeRADIUS 01 disponible
→ le WLC envoie les requêtes vers FreeRADIUS 01.

FreeRADIUS 01 indisponible
→ le WLC bascule vers FreeRADIUS 02.

FreeRADIUS 02 indisponible
→ le WLC utilise FreeRADIUS 01.
```

Les deux serveurs sont indépendants. Ils doivent maintenir une
configuration fonctionnellement cohérente, mais ne doivent pas partager :

```text
Hostname Linux
Adresse IP
Identité Samba / Active Directory
Machine ID
Clé privée EAP
Certificat EAP
```

---

## Chaîne de confiance des certificats

```text
Autorité de certification interne
            │
            ▼
Certificat LDAPS du contrôleur de domaine
            │
            ▼
FreeRADIUS valide LDAPS
            │
            ▼
Certificat EAP de FreeRADIUS
            │
            ▼
Poste Windows valide le serveur RADIUS via la CA interne
```

La CA interne est distribuée aux postes Windows par stratégie de groupe.

Les certificats EAP des serveurs RADIUS doivent contenir :

```text
Nom commun correspondant au FQDN RADIUS
Subject Alternative Name DNS
Usage étendu Server Authentication
```

Exemple :

```text
CN  = radius01.example.local
SAN = DNS:radius01.example.local
EKU = Server Authentication
```

---

## Principes de sécurité appliqués

```text
RADIUS autorisé uniquement depuis les équipements NAS/WLC connus.
Secrets RADIUS longs et non publiés.
LDAPS utilisé pour les recherches Active Directory.
Validation obligatoire du certificat serveur RADIUS.
Déploiement du profil WiFi par GPO.
Authentification individuelle des utilisateurs.
Deux serveurs RADIUS indépendants.
Journalisation RADIUS Accounting.
Accès SSH limité au réseau d’administration.
```
