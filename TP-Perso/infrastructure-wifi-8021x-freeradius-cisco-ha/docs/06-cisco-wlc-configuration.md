# Configuration Cisco WLC et WiFi Enterprise

## Objectif

Cette procédure décrit la configuration d’un WLAN sécurisé sur un
contrôleur Cisco Mobility Express.

Le WLAN utilise :

```text
WPA2-Enterprise
AES-CCMP
IEEE 802.1X
PEAP
EAP-MSCHAPv2
FreeRADIUS
Active Directory
RADIUS Authentication
RADIUS Accounting
```

L’objectif est de permettre aux utilisateurs Active Directory de se
connecter au WiFi avec leurs propres identifiants.

> Les noms, IP, WLAN ID, secrets et équipements sont anonymisés.
> Adapter les valeurs à l’environnement cible.

---

## 1. Environnement de référence

| Élément | Valeur d’exemple |
|---|---|
| WLC Cisco Mobility Express | `wlc01.example.local` |
| Adresse WLC | `10.20.30.10` |
| FreeRADIUS 01 | `10.20.20.11` |
| FreeRADIUS 02 | `10.20.20.12` |
| SSID | `CORP-SECURE` |
| WLAN ID | `4` |
| Authentication RADIUS | UDP `1812` |
| Accounting RADIUS | UDP `1813` |
| Sécurité WiFi | WPA2-Enterprise |
| Chiffrement | AES-CCMP |

---

## 2. Prérequis avant modification WLC

Avant de créer ou modifier un WLAN, vérifier les éléments suivants :

```text
Les deux serveurs FreeRADIUS sont actifs.
Les deux serveurs écoutent UDP 1812.
Les deux serveurs reconnaissent l’IP du WLC dans clients.conf.
Le secret RADIUS est connu mais n’est pas affiché dans la documentation.
Le pare-feu Debian autorise UDP 1812 et UDP 1813 depuis le WLC.
La CA interne est déployée sur le poste de test.
Un poste pilote est disponible.
Un accès de secours au WLC est disponible.
```

Vérifications sur chaque serveur FreeRADIUS :

```bash
systemctl is-active freeradius
systemctl is-active winbind

net ads testjoin
wbinfo -t

ss -lunp | grep -E ':(1812|1813)\b'

ufw status verbose
```

Résultat attendu :

```text
freeradius : active
winbind : active
Join is OK
checking the trust secret via RPC calls succeeded
Ports UDP 1812 et UDP 1813 en écoute
Règles UFW présentes pour le WLC
```

---

## 3. Sauvegarde avant modification

Avant une modification importante du WLC :

```text
Exporter ou sauvegarder la configuration Mobility Express.
Relever les WLAN existants.
Relever les serveurs RADIUS existants.
Prendre une capture anonymisée de la configuration si nécessaire.
Noter les paramètres avant modification.
```

Vérifier les WLAN :

```bash
show wlan summary
```

Vérifier les serveurs RADIUS :

```bash
show radius summary
```

Vérifier les statistiques Authentication :

```bash
show radius auth statistics
```

Vérifier les statistiques Accounting :

```bash
show radius acct statistics
```

> Les commandes disponibles peuvent varier selon la version Mobility
> Express. Utiliser `?` dans la CLI du WLC pour vérifier la syntaxe
> supportée par la version installée.

---

## 4. Création du WLAN

Dans l’interface Cisco Mobility Express :

```text
Wireless Settings
→ WLANs
→ Add
```

Créer le WLAN avec les paramètres suivants.

| Paramètre | Valeur d’exemple |
|---|---|
| WLAN ID | `4` |
| Profile Name | `WLAN-CORP-SECURE` |
| SSID | `CORP-SECURE` |
| Admin State | Enabled |
| Radio Policy | ALL |
| Broadcast SSID | Enabled |
| Local Profiling | Disabled ou valeur par défaut |

Enregistrer avec :

```text
Save
ou
Apply
```

### Vérification

Le WLAN doit apparaître dans la liste :

```text
WLAN ID : 4
SSID : CORP-SECURE
State : Enabled
```

> Ne pas modifier les WLAN historiques ou les SSID existants sans besoin
> identifié.

---

## 5. Configuration de la sécurité WiFi

Ouvrir le WLAN créé :

```text
Wireless Settings
→ WLANs
→ WLAN-CORP-SECURE
→ Edit
→ Security
```

Configurer :

| Paramètre | Valeur |
|---|---|
| Guest Network | Disabled |
| MAC Filtering | Disabled |
| Security Type | WPA2-Enterprise |
| Chiffrement | AES-CCMP |
| Authentication | 802.1X |
| Authentication Server | External RADIUS |

Ne pas utiliser :

```text
WPA2-Personal
Clé WiFi partagée
WEP
TKIP
EAP-MD5
```

Enregistrer avec :

```text
Save
ou
Apply
```

---

## 6. Ajouter les serveurs RADIUS Authentication

Le WLC doit connaître deux serveurs RADIUS.

```text
Serveur primaire :
FreeRADIUS 01
10.20.20.11
UDP 1812

Serveur secondaire :
FreeRADIUS 02
10.20.20.12
UDP 1812
```

Dans l’interface Mobility Express :

```text
Wireless Settings
→ WLANs
→ WLAN-CORP-SECURE
→ Edit
→ Security
→ RADIUS Authentication Server
```

Ajouter le premier serveur :

| Champ | Valeur |
|---|---|
| Server IP Address | `10.20.20.11` |
| Port | `1812` |
| Shared Secret | `<RADIUS_SHARED_SECRET>` |
| Confirm Shared Secret | `<RADIUS_SHARED_SECRET>` |

Ajouter le second serveur :

| Champ | Valeur |
|---|---|
| Server IP Address | `10.20.20.12` |
| Port | `1812` |
| Shared Secret | `<RADIUS_SHARED_SECRET>` |
| Confirm Shared Secret | `<RADIUS_SHARED_SECRET>` |

Le secret doit correspondre exactement à celui défini dans :

```text
/etc/freeradius/3.0/clients.conf
```

Exemple de client RADIUS FreeRADIUS :

```text
client wlc_cisco {
    ipaddr = 10.20.30.10
    secret = <RADIUS_SHARED_SECRET>
    shortname = WLC-CISCO
    require_message_authenticator = yes
}
```

> Ne jamais publier le vrai secret RADIUS dans une capture, un commit,
> un ticket, un fichier de configuration public ou une documentation.

Enregistrer avec :

```text
Save
ou
Apply
```

---

## 7. VLAN et firewall du WLAN

Dans l’interface Mobility Express :

```text
Wireless Settings
→ WLANs
→ WLAN-CORP-SECURE
→ Edit
→ VLAN & Firewall
```

Pour un premier déploiement 802.1X sans VLAN dynamique :

| Paramètre | Valeur d’exemple |
|---|---|
| Client IP Management Network | Network (Default) |
| Use VLAN Tagging | No |
| Native VLAN ID | Valeur adaptée à l’infrastructure |
| DHCP Scope | Scope DHCP du WLAN si utilisé |
| Peer-to-Peer Blocking | Selon politique de sécurité |
| Firewall | Selon politique de sécurité |

Le VLAN dynamique RADIUS peut être ajouté ultérieurement. Il nécessite
une cohérence entre :

```text
Attributs RADIUS
VLAN configurés sur le WLC
VLAN autorisés sur les switches
DHCP du VLAN
Routage inter-VLAN
Pare-feu
```

Ne pas activer le VLAN dynamique sans plan de test.

---

## 8. QoS et trafic

Dans l’interface Mobility Express :

```text
Wireless Settings
→ WLANs
→ WLAN-CORP-SECURE
→ Edit
→ Traffic Shaping
ou
QoS
```

Pour un premier WLAN entreprise :

| Paramètre | Valeur recommandée |
|---|---|
| QoS | Silver / Best Effort |
| Fastlane | Disabled |
| Application Visibility Control | Disabled |
| Règles AVC | Aucune au départ |

Ces paramètres peuvent être adaptés plus tard selon les usages réels :

```text
VoIP
Visioconférence
Terminaux métiers
Invités
IoT
Applications critiques
```

---

## 9. Ajouter RADIUS Accounting

### 9.1 Objectif

RADIUS Accounting permet au WLC d’envoyer les événements de session à
FreeRADIUS.

```text
Connexion WiFi
→ Accounting-Start

Session active
→ Accounting-Interim-Update éventuel

Déconnexion WiFi
→ Accounting-Stop
```

L’Accounting utilise :

```text
UDP 1813
```

### 9.2 Ajouter les serveurs Accounting

Dans la CLI Mobility Express, ajouter les deux serveurs :

```bash
config radius acct add 1 10.20.20.11 1813 ascii <RADIUS_SHARED_SECRET>
config radius acct add 2 10.20.20.12 1813 ascii <RADIUS_SHARED_SECRET>
```

Correspondance :

```text
Index 1
→ FreeRADIUS 01
→ 10.20.20.11:1813

Index 2
→ FreeRADIUS 02
→ 10.20.20.12:1813
```

### 9.3 Associer Accounting au WLAN

Ajouter ensuite les serveurs Accounting au WLAN ID `4` :

```bash
config wlan radius_server acct add 4 1
config wlan radius_server acct add 4 2
config wlan radius_server acct enable 4
```

Cette étape est importante.

```text
Ajouter un serveur dans la table globale RADIUS Accounting
≠
Associer ce serveur au WLAN concerné
```

### 9.4 Sauvegarder la configuration WLC

Après validation :

```bash
save config
```

Répondre :

```text
y
```

si le WLC demande confirmation.

---

## 10. Vérifier la configuration RADIUS WLC

Après ajout des serveurs, lancer :

```bash
show radius summary
```

Résultat attendu, sous une forme équivalente :

```text
Authentication Servers

1  10.20.20.11  1812  Enabled
2  10.20.20.12  1812  Enabled

Accounting Servers

1  10.20.20.11  1813  Enabled
2  10.20.20.12  1813  Enabled
```

Vérifier le WLAN :

```bash
show wlan 4
```

Résultat attendu :

```text
WLAN ID : 4
SSID : CORP-SECURE
WPA2-Enterprise : Enabled
802.1X : Enabled
RADIUS Authentication : Enabled
RADIUS Accounting : Enabled
```

La sortie exacte dépend de la version du contrôleur.

---

## 11. Vérifier les statistiques Authentication

Avant de lancer un test WiFi, relever les statistiques :

```bash
show radius auth statistics
```

Rechercher notamment :

```text
First Requests
Retry Requests
Access Accepts
Access Rejects
Timeout Requests
Malformed Messages
Bad Authenticator Messages
```

Exemple de résultat sain :

```text
First Requests        : 10
Access Accepts        : 10
Retry Requests        : 0
Timeout Requests      : 0
Malformed Messages    : 0
Bad Authenticator Msgs: 0
```

Interprétation :

| Compteur | Signification |
|---|---|
| First Requests | Requêtes RADIUS initiales envoyées |
| Access Accepts | Authentifications réussies |
| Access Rejects | Authentifications refusées |
| Retry Requests | Réémissions du WLC |
| Timeout Requests | Serveur RADIUS sans réponse |
| Bad Authenticator | Secret incorrect ou paquet altéré |

---

## 12. Vérifier les statistiques Accounting

Avant une connexion de test :

```bash
show radius acct statistics
```

Après une connexion et déconnexion du client :

```bash
show radius acct statistics
```

Exemple attendu :

```text
First Requests        : 2
Accounting Responses  : 2
Retry Requests        : 0
Timeout Requests      : 0
Malformed Messages    : 0
Bad Authenticator Msgs: 0
```

Les deux requêtes peuvent correspondre à :

```text
Accounting-Start
+
Accounting-Stop
```

---

## 13. Tester le WLAN avec un poste pilote

Utiliser un poste de test Windows.

Avant de tester :

```text
Le certificat CA doit être présent sur le poste.
Le profil WiFi doit être configuré ou déployé par GPO.
Le poste doit connaître le SSID CORP-SECURE.
PEAP doit être configuré.
EAP-MSCHAPv2 doit être configuré.
Les serveurs RADIUS doivent être validés.
```

Test :

```text
1. Se déconnecter du SSID CORP-SECURE.
2. Attendre quelques secondes.
3. Se reconnecter au SSID.
4. Entrer les identifiants Active Directory si demandés.
5. Vérifier que le poste reçoit une adresse IP.
6. Vérifier la passerelle.
7. Vérifier DNS.
8. Vérifier l’accès au réseau.
```

Côté FreeRADIUS, suivre les journaux :

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
PEAP Session established
MS-CHAP authentication succeeded
EAP Success
Access-Accept
```

Après le debug :

```text
Ctrl + C
```

Puis :

```bash
systemctl start freeradius
systemctl is-active freeradius
```

---

## 14. Dépannage WLC et RADIUS

| Symptôme | Cause probable | Vérification |
|---|---|---|
| Aucun paquet reçu par FreeRADIUS | WLC, routage ou firewall | Ping WLC, UFW, IP du client RADIUS |
| Access-Reject immédiat | Secret ou clients.conf | Secret WLC, IP source, `clients.conf` |
| Timeout WLC | FreeRADIUS indisponible ou firewall | `systemctl status`, UFW, port 1812 |
| Bad Authenticator | Secret RADIUS différent | Comparer WLC et `clients.conf` |
| Échec certificat sur Windows | CA ou nom serveur | GPO CA, CN/SAN, noms approuvés |
| Access-Accept mais pas de réseau | DHCP, VLAN ou routage | DHCP, gateway, DNS, VLAN |
| Accounting absent | Serveur non associé au WLAN | `show radius summary`, `show wlan 4` |
| Accounting timeout | UDP 1813 bloqué | UFW, écoute FreeRADIUS, secret |
| Failover absent | Second serveur non configuré | WLC, statistiques, état RADIUS 02 |

---

## Étape suivante

Poursuivre avec :

```text
docs/07-windows-gpo-wifi-profile.md
```

Cette prochaine fiche couvre :

```text
Déploiement de la CA interne.
Création d’une GPO
