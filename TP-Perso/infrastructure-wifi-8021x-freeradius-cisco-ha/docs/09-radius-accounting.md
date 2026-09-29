# RADIUS Accounting et traçabilité des sessions WiFi

## Objectif

Cette procédure décrit la mise en place de RADIUS Accounting entre un
WLC Cisco et deux serveurs FreeRADIUS.

L’Accounting complète l’authentification WiFi.

```text
Authentication
→ décide si un utilisateur peut accéder au WiFi.

Accounting
→ enregistre les événements de session WiFi.
```

Ports utilisés :

```text
UDP 1812
→ RADIUS Authentication

UDP 1813
→ RADIUS Accounting
```

Architecture :

```text
Client WiFi
→ WLC Cisco

WLC Cisco
→ RADIUS Authentication UDP 1812
→ FreeRADIUS

WLC Cisco
→ RADIUS Accounting UDP 1813
→ FreeRADIUS

FreeRADIUS
→ fichiers radacct
→ journaux de sessions
```

> Toutes les adresses, utilisateurs, MAC, WLAN et chemins de cette
> documentation sont anonymisés.

---

## 1. Événements Accounting

Le WLC peut envoyer plusieurs types d’événements.

| Événement | Signification |
|---|---|
| `Accounting-Start` | Le client vient de commencer une session WiFi |
| `Accounting-Interim-Update` | Le client est toujours connecté ; mise à jour périodique |
| `Accounting-Stop` | Le client a quitté le WiFi ou sa session a été fermée |

Exemple de cycle complet :

```text
Utilisateur se connecte au SSID CORP-SECURE
→ Accounting-Start

Utilisateur reste connecté
→ Accounting-Interim-Update éventuel

Utilisateur se déconnecte
→ Accounting-Stop
```

---

## 2. Informations enregistrées

Les journaux Accounting peuvent contenir les attributs suivants.

| Attribut RADIUS | Signification |
|---|---|
| `User-Name` | Identité RADIUS authentifiée |
| `Framed-IP-Address` | Adresse IP attribuée au client |
| `NAS-IP-Address` | Adresse IP du WLC Cisco |
| `NAS-Identifier` | Nom du WLC / NAS |
| `Airespace-Wlan-Id` | Identifiant du WLAN Cisco |
| `Calling-Station-Id` | Adresse MAC WiFi du client |
| `Called-Station-Id` | Identifiant AP/radio transmis par Cisco |
| `Acct-Session-Id` | Identifiant de session attribué par le WLC |
| `Acct-Unique-Session-Id` | Identifiant unique FreeRADIUS |
| `Acct-Status-Type` | Start, Interim-Update ou Stop |
| `Acct-Session-Time` | Durée de session en secondes |
| `Acct-Input-Octets` | Volume de trafic entrant |
| `Acct-Output-Octets` | Volume de trafic sortant |

Exemple anonymisé :

```text
User-Name = "user.test"
Framed-IP-Address = 10.20.40.56
NAS-IP-Address = 10.20.30.10
NAS-Identifier = "WLC-EXAMPLE"
Airespace-Wlan-Id = 4
Calling-Station-Id = "aa-bb-cc-dd-ee-ff"
Acct-Session-Id = "A1B2C3D4"
Acct-Status-Type = Start
```

---

## 3. Prérequis

Avant de configurer l’Accounting, vérifier :

```text
L’authentification WiFi UDP 1812 fonctionne.
Le WLC est déclaré dans clients.conf.
Le secret RADIUS WLC est identique sur le WLC et FreeRADIUS.
FreeRADIUS écoute UDP 1813.
Le pare-feu Debian autorise UDP 1813 depuis le WLC.
Le module detail est actif.
Les deux serveurs RADIUS sont disponibles.
Le WLAN concerné est identifié.
```

Exemple de références :

| Élément | Valeur d’exemple |
|---|---|
| WLC Cisco | `10.20.30.10` |
| FreeRADIUS 01 | `10.20.20.11` |
| FreeRADIUS 02 | `10.20.20.12` |
| WLAN WiFi entreprise | ID `4` |
| SSID | `CORP-SECURE` |
| Port Accounting | UDP `1813` |

---

## 4. Vérifier l’écoute UDP 1813

Sur FreeRADIUS 01 :

```bash
ss -lunp | grep ':1813'
```

Sur FreeRADIUS 02 :

```bash
ss -lunp | grep ':1813'
```

Résultat attendu :

```text
UNCONN ... 0.0.0.0:1813 ... freeradius
```

Ou une ligne équivalente indiquant :

```text
Protocole : UDP
Port : 1813
Processus : freeradius
```

Si UDP 1813 n’apparaît pas, vérifier les fichiers de configuration
FreeRADIUS avant toute modification :

```bash
grep -RniE '1813|Accounting-Request|listen.*acct|listen.*accounting' \
  /etc/freeradius/3.0/sites-enabled \
  /etc/freeradius/3.0/sites-available \
  2>/dev/null
```

Contrôler également la syntaxe :

```bash
freeradius -XC
```

Ne redémarrer le service que si la validation est réussie.

---

## 5. Vérifier le firewall UFW

Le WLC doit être autorisé à joindre UDP 1813.

Vérifier :

```bash
ufw status numbered
```

Exemple de règle attendue :

```text
1813/udp ALLOW IN 10.20.30.10
```

Si la règle est absente, ajouter :

```bash
ufw allow from 10.20.30.10 to any port 1813 proto udp
```

Vérifier ensuite :

```bash
ufw status verbose
```

L’Authentication doit également rester autorisée :

```bash
ufw allow from 10.20.30.10 to any port 1812 proto udp
```

Ne pas ouvrir UDP 1812 ou UDP 1813 à tous les réseaux sans besoin
identifié.

---

## 6. Vérifier le client WLC dans FreeRADIUS

L’Accounting utilise le même client RADIUS et le même secret partagé que
l’Authentication.

Sur chaque serveur :

```bash
grep -n -A 8 -B 2 '10.20.30.10' \
  /etc/freeradius/3.0/clients.conf
```

Exemple attendu :

```text
client wlc_cisco {
    ipaddr = 10.20.30.10
    secret = <RADIUS_SHARED_SECRET>
    shortname = WLC-CISCO
    require_message_authenticator = yes
}
```

Il n’est normalement pas nécessaire de créer un second client RADIUS
uniquement pour UDP 1813.

> Ne jamais écrire le vrai secret RADIUS dans une documentation publique.

---

## 7. Activer le module detail

Le module `detail` enregistre les requêtes Accounting reçues dans des
fichiers de logs structurés.

Le fichier de configuration principal est généralement :

```text
/etc/freeradius/3.0/sites-enabled/default
```

Avant modification, sauvegarder :

```bash
cp -a /etc/freeradius/3.0/sites-enabled/default \
  /root/default.bak-$(date +%F-%H%M)
```

Ouvrir le fichier :

```bash
nano /etc/freeradius/3.0/sites-enabled/default
```

Chercher le bloc :

```text
accounting {
```

Le module `detail` doit être appelé dans ce bloc.

Exemple :

```text
accounting {
    detail
}
```

Si la ligne est commentée :

```text
# detail
```

retirer uniquement le caractère :

```text
#
```

Ne pas supprimer les autres modules du bloc `accounting` sans comprendre
leur rôle.

Enregistrer dans Nano :

```text
Ctrl + O
→ Entrée
→ Ctrl + X
```

Valider avant redémarrage :

```bash
freeradius -XC
```

Puis, uniquement si la validation est correcte :

```bash
systemctl restart freeradius
systemctl status freeradius --no-pager
```

Vérifier le journal :

```bash
journalctl -u freeradius -n 80 --no-pager
```

> Certains environnements possèdent déjà `detail` activé. Dans ce cas,
> ne rien modifier : documenter simplement la configuration existante.

---

## 8. Vérifier le répertoire radacct

Le module `detail` crée généralement les journaux dans :

```text
/var/log/freeradius/radacct/
```

Le WLC peut disposer de son propre répertoire basé sur son adresse IP.

Exemple :

```text
/var/log/freeradius/radacct/10.20.30.10/
```

Lister les fichiers :

```bash
find /var/log/freeradius/radacct -maxdepth 2 -type f -ls
```

Exemple de journal quotidien :

```text
/var/log/freeradius/radacct/10.20.30.10/detail-20260101
```

Le nom exact peut varier selon la configuration du module `detail`.

---

## 9. Ajouter les serveurs Accounting dans le WLC

Le WLC possède une table RADIUS Accounting distincte de la table
Authentication.

Sur Cisco Mobility Express, ajouter les serveurs :

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

Le secret doit correspondre à :

```text
Le secret du WLC dans clients.conf.
Le secret Authentication déjà configuré.
```

---

## 10. Associer Accounting au WLAN

Ajouter les serveurs Accounting dans la table globale ne suffit pas.

Ils doivent être associés au WLAN concerné.

Exemple avec le WLAN ID `4` :

```bash
config wlan radius_server acct add 4 1
config wlan radius_server acct add 4 2
config wlan radius_server acct enable 4
```

Correspondance :

```text
WLAN 4
→ CORP-SECURE

Index Accounting 1
→ FreeRADIUS 01

Index Accounting 2
→ FreeRADIUS 02
```

Sauvegarder ensuite :

```bash
save config
```

Répondre :

```text
y
```

si le WLC demande confirmation.

---

## 11. Vérifier la configuration WLC

Vérifier les serveurs RADIUS :

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
RADIUS Authentication : Enabled
RADIUS Accounting : Enabled
```

La sortie exacte dépend de la version Mobility Express.

---

## 12. Relever les statistiques avant test

Avant de reconnecter un client :

```bash
show radius acct statistics
```

Noter les compteurs actuels :

```text
First Requests
Retry Requests
Responses
Timeout Requests
Malformed Messages
Bad Authenticator Messages
Other Drops
```

L’objectif est de comparer les valeurs avant et après le test.

Exemple avant test :

```text
First Requests        : 0
Accounting Responses  : 0
Retry Requests        : 0
Timeout Requests      : 0
```

---

## 13. Suivre les logs FreeRADIUS

Sur FreeRADIUS 01 :

```bash
journalctl -fu freeradius
```

Sur FreeRADIUS 02 :

```bash
journalctl -fu freeradius
```

Pour suivre directement le fichier `detail` :

```bash
tail -F \
  /var/log/freeradius/radacct/10.20.30.10/detail-$(date +%Y%m%d)
```

Afficher les dernières lignes :

```bash
tail -n 100 \
  /var/log/freeradius/radacct/10.20.30.10/detail-$(date +%Y%m%d)
```

> Le nom du fichier peut varier selon la configuration réelle.
> Utiliser `find /var/log/freeradius/radacct -type f` pour l’identifier.

---

## 14. Générer un Accounting-Start

Sur le poste pilote :

```text
1. Se déconnecter du SSID CORP-SECURE.
2. Attendre quelques secondes.
3. Se reconnecter au SSID.
4. S’authentifier si nécessaire.
5. Attendre que la connexion WiFi soit établie.
```

Côté FreeRADIUS, rechercher :

```text
Received Accounting-Request
Acct-Status-Type = Start
```

Exemple :

```text
User-Name = "user.test"
Airespace-Wlan-Id = 4
Acct-Authentic = RADIUS
Acct-Status-Type = Start
```

Cela confirme :

```text
Le client s’est connecté au WLAN.
Le WLC a envoyé un événement Accounting.
FreeRADIUS a reçu et journalisé la session.
```

---

## 15. Générer un Accounting-Stop

Sur le poste pilote :

```text
1. Ouvrir les paramètres WiFi Windows.
2. Sélectionner CORP-SECURE.
3. Cliquer sur Déconnecter.

ou

1. Désactiver temporairement l’interface WiFi.
```

Côté FreeRADIUS, rechercher :

```text
Received Accounting-Request
Acct-Status-Type = Stop
```

Cela confirme :

```text
La fin de session est journalisée.
La durée de session peut être calculée.
Les compteurs de trafic peuvent être enregistrés.
```

---

## 16. Vérifier les compteurs après test

Retourner sur le WLC :

```bash
show radius acct statistics
```

Comparer les valeurs avec celles relevées avant le test.

Exemple :

```text
Avant test :

First Requests        : 0
Accounting Responses  : 0

Après test :

First Requests        : 2
Accounting Responses  : 2
Retry Requests        : 0
Timeout Requests      : 0
```

Interprétation :

```text
1 Accounting-Start
+
1 Accounting-Stop
=
2 requêtes Accounting
```

Résultat attendu :

```text
Les requêtes augmentent.
Les réponses augmentent.
Aucun timeout.
Aucun retry.
Aucun Bad Authenticator Message.
```

---

## 17. Filtrer les sessions du WLAN

Pour retrouver les sessions du WLAN ID `4` :

```bash
grep -n -B 25 -A 20 \
  'Airespace-Wlan-Id = 4' \
  /var/log/freeradius/radacct/10.20.30.10/detail-$(date +%Y%m%d)
```

Pour suivre uniquement les nouveaux blocs du WLAN `4` :

```bash
tail -F \
  /var/log/freeradius/radacct/10.20.30.10/detail-$(date +%Y%m%d) | \
awk 'BEGIN { RS=""; ORS="\n\n" } /Airespace-Wlan-Id = 4/ { print }'
```

Pour retrouver une MAC précise :

```bash
grep -n -B 30 -A 30 \
  'Calling-Station-Id = "aa-bb-cc-dd-ee-ff"' \
  /var/log/freeradius/radacct/10.20.30.10/detail-$(date +%Y%m%d)
```

Pour afficher le dernier bloc lié à une MAC précise sur le WLAN `4` :

```bash
awk 'BEGIN { RS="" } \
/Airespace-Wlan-Id = 4/ && \
/Calling-Station-Id = "aa-bb-cc-dd-ee-ff"/ \
{ last=$0 } \
END { print last }' \
/var/log/freeradius/radacct/10.20.30.10/detail-$(date +%Y%m%d)
```

---

## 18. Interim Updates

Le WLC peut envoyer des mises à jour périodiques pendant qu’un client
reste connecté.

```text
Acct-Status-Type = Interim-Update
```

Ces événements peuvent fournir :

```text
Durée actuelle de session.
Volume de trafic actuel.
Adresse IP.
Identité utilisateur.
WLAN.
```

Pour une première mise en œuvre, valider d’abord :

```text
Accounting-Start
Accounting-Stop
```

Si les mises à jour périodiques sont nécessaires, configurer un intervalle
documenté.

Exemple :

```text
900 secondes
→ 15 minutes
```

Un intervalle court produit plus de paquets, plus de logs et plus de
données à stocker.

---

## 19. Rétention et protection des logs

Les journaux Accounting peuvent contenir :

```text
Identité utilisateur.
Adresse MAC.
Adresse IP.
Horaires de connexion.
Durée de session.
Point d’accès.
Volumes de trafic.
```

Ces informations doivent être protégées.

Définir une politique documentée :

```text
Finalité :
Diagnostic réseau, sécurité et investigation d’incident.

Accès :
Administrateurs réseau et sécurité habilités uniquement.

Rétention :
Durée définie par l’organisation selon les besoins légaux,
de sécurité et de conformité.

Suppression :
Purge automatique à l’expiration de la durée retenue.

Sauvegarde :
Conforme à la politique de sauvegarde de l’organisation.
```

Avant d’automatiser une suppression, vérifier le format réel des fichiers :

```bash
find /var/log/freeradius/radacct -type f -printf '%TY-%Tm-%Td %p\n' | sort
```

Exemple de commande de recherche des fichiers anciens, sans suppression :

```bash
find /var/log/freeradius/radacct \
  -type f \
  -name 'detail-*' \
  -mtime +180 \
  -print
```

Ne pas ajouter automatiquement `-delete` avant :

```text
Validation de la politique de rétention.
Test sur un environnement non critique.
Sauvegarde disponible.
Validation des fichiers réellement ciblés.
```

---

## Étape suivante

Poursuivre avec :

```text
docs/10-monitoring-and-future-improvements.md
```

Cette prochaine fiche couvre :

```text
Supervision FreeRADIUS.
Surveillance Winbind.
Expiration des certificats.
Contrôles Zabbix.
Centralisation Wazuh.
Alertes RADIUS.
Évolutions WPA3-Enterprise.
EAP-TLS.
VLAN dynamique.
Ansible.
```
