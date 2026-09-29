# Haute disponibilité FreeRADIUS et tests de bascule

## Objectif

Cette procédure décrit la mise en place et la validation de la haute
disponibilité RADIUS avec deux serveurs FreeRADIUS indépendants.

L’objectif est de garantir que les nouvelles authentifications WiFi
continuent de fonctionner lorsqu’un serveur RADIUS est indisponible.

Architecture :

```text
Cisco WLC
    │
    ├── Serveur RADIUS primaire
    │   → FreeRADIUS 01
    │   → 10.20.20.11
    │
    └── Serveur RADIUS secondaire
        → FreeRADIUS 02
        → 10.20.20.12
```

> Les noms, IP, utilisateurs et informations d’infrastructure sont
> anonymisés.

---

## 1. Pourquoi la haute disponibilité RADIUS

Sans redondance :

```text
FreeRADIUS unique indisponible
→ nouvelles authentifications WiFi impossibles
→ nouveaux utilisateurs ne peuvent plus rejoindre le réseau
→ incident WiFi d’entreprise
```

Avec deux serveurs :

```text
FreeRADIUS 01 indisponible
→ WLC Cisco
→ FreeRADIUS 02
→ nouvelles authentifications maintenues
```

Le WLC gère la bascule selon :

```text
L’ordre des serveurs configurés.
Les délais d’attente RADIUS.
Le nombre de réémissions.
L’état de disponibilité détecté.
```

Cette architecture est parfois appelée :

```text
Active / Passive du point de vue du WLC
```

Les deux serveurs restent néanmoins actifs techniquement :

```text
Les deux services FreeRADIUS fonctionnent.
Les deux serveurs sont capables d’authentifier les utilisateurs.
Le WLC sélectionne généralement le primaire.
Le secondaire est utilisé lors d’une indisponibilité.
```

---

## 2. Architecture de référence

| Élément | Nom | Adresse d’exemple | Rôle |
|---|---|---:|---|
| Serveur primaire | `radius01.example.local` | `10.20.20.11` | Authentication RADIUS primaire |
| Serveur secondaire | `radius02.example.local` | `10.20.20.12` | Authentication RADIUS secondaire |
| WLC Cisco | `wlc01.example.local` | `10.20.30.10` | NAS / Authenticator 802.1X |
| Poste pilote | `WIN11-TEST-01` | DHCP | Test utilisateur WiFi |
| Active Directory | `dc01.example.local` | `10.20.10.10` | Identités et authentification AD |

Les deux serveurs doivent être déclarés dans le WLC pour :

```text
RADIUS Authentication UDP 1812
RADIUS Accounting UDP 1813
```

La validation de bascule Authentication et la validation de bascule
Accounting sont deux opérations distinctes.

```text
Authentication
→ UDP 1812
→ nécessaire pour autoriser ou refuser l’accès WiFi.

Accounting
→ UDP 1813
→ nécessaire pour tracer les sessions.
```

---

## 3. Ce qui doit être cohérent

Les deux serveurs doivent fournir le même service fonctionnel.

| Élément | FreeRADIUS 01 | FreeRADIUS 02 |
|---|---|---|
| Domaine Active Directory | Identique | Identique |
| DNS AD | Identique | Identique |
| LDAPS | Fonctionnel | Fonctionnel |
| Kerberos | Fonctionnel | Fonctionnel |
| Samba / Winbind | Fonctionnel | Fonctionnel |
| `ntlm_auth` | Fonctionnel | Fonctionnel |
| Module `mschap` | Même logique | Même logique |
| `inner-tunnel` | Même logique | Même logique |
| Client WLC dans `clients.conf` | Même IP WLC | Même IP WLC |
| Secret RADIUS WLC | Même valeur applicable | Même valeur applicable |
| Firewall UDP 1812 | WLC autorisé | WLC autorisé |
| Firewall UDP 1813 | WLC autorisé | WLC autorisé |
| CA interne | Approuvée | Approuvée |
| GPO WiFi client | Même serveurs approuvés | Même serveurs approuvés |

---

## 4. Ce qui doit rester unique

Ne pas copier aveuglément les éléments suivants entre les serveurs :

```text
Hostname Linux
Adresse IP
Adresse MAC VM
Machine ID
Identité Samba / ordinateur AD
Secrets machine Samba
Fichiers d’état Winbind
Clé privée EAP
Certificat EAP
Nom DNS du certificat EAP
Journaux locaux
```

Exemple recommandé :

```text
FreeRADIUS 01 :
Hostname : radius01
IP       : 10.20.20.11
Certificat : radius01.example.local

FreeRADIUS 02 :
Hostname : radius02
IP       : 10.20.20.12
Certificat : radius02.example.local
```

Les deux serveurs peuvent utiliser la même CA interne, mais chaque
serveur doit posséder son propre certificat et sa propre clé privée.

---

## 5. Contrôle avant test de bascule

Avant tout test, vérifier l’état des deux serveurs.

### 5.1 Contrôles sur FreeRADIUS 01

```bash
systemctl is-active freeradius
systemctl is-active winbind

net ads testjoin
wbinfo -t

freeradius -XC

ss -lunp | grep -E ':(1812|1813)\b'
```

### 5.2 Contrôles sur FreeRADIUS 02

```bash
systemctl is-active freeradius
systemctl is-active winbind

net ads testjoin
wbinfo -t

freeradius -XC

ss -lunp | grep -E ':(1812|1813)\b'
```

Résultat attendu sur les deux serveurs :

```text
freeradius : active
winbind : active
Join is OK
checking the trust secret via RPC calls succeeded
Configuration appears to be OK
UDP 1812 en écoute
UDP 1813 en écoute
```

### 5.3 Contrôles WLC

Sur le WLC :

```bash
show radius summary
show radius auth statistics
show radius acct statistics
show wlan 4
```

Vérifier que les deux serveurs sont présents et activés.

Exemple attendu :

```text
Authentication Servers

1  10.20.20.11  1812  Enabled
2  10.20.20.12  1812  Enabled

Accounting Servers

1  10.20.20.11  1813  Enabled
2  10.20.20.12  1813  Enabled
```

### 5.4 Préparer le poste pilote

Avant le test, vérifier :

```text
Le poste est joint au domaine.
Le certificat CA interne est présent.
La GPO WiFi est appliquée.
Le profil CORP-SECURE est présent.
Un utilisateur Active Directory de test est disponible.
Le poste peut être déconnecté/reconnecté au WiFi.
```

Sur Windows :

```cmd
gpresult /r
netsh wlan show profiles
netsh wlan show interfaces
```

---

## 6. Préparer les journaux

Sur FreeRADIUS 01, ouvrir un terminal :

```bash
journalctl -fu freeradius
```

Sur FreeRADIUS 02, ouvrir un second terminal :

```bash
journalctl -fu freeradius
```

Ne pas lancer immédiatement :

```bash
freeradius -X
```

Le suivi avec `journalctl` est moins intrusif et ne nécessite pas
d’arrêter le service de production.

Si une analyse détaillée est nécessaire, utiliser le debug uniquement
pendant une fenêtre de test contrôlée.

---

## 7. Test 1 : validation du serveur primaire

Objectif :

```text
Vérifier que FreeRADIUS 01 authentifie correctement un client WiFi.
```

### Étapes

1. Vérifier que les deux serveurs sont activés dans le WLC.
2. Sur FreeRADIUS 01, laisser `journalctl -fu freeradius` ouvert.
3. Déconnecter le poste pilote du SSID `CORP-SECURE`.
4. Attendre quelques secondes.
5. Reconnecter le poste.
6. S’authentifier avec un compte Active Directory valide.
7. Vérifier les logs de FreeRADIUS 01.
8. Vérifier les statistiques Authentication du WLC.

### Résultat attendu

Dans les logs FreeRADIUS 01 :

```text
PEAP Session established
MS-CHAP authentication succeeded
EAP Success
Access-Accept
```

Sur le WLC :

```bash
show radius auth statistics
```

Les compteurs du serveur primaire doivent augmenter.

---

## 8. Test 2 : bascule vers FreeRADIUS 02

Objectif :

```text
Vérifier que FreeRADIUS 02 peut authentifier un client
lorsque FreeRADIUS 01 est indisponible.
```

### Méthode recommandée

Dans un environnement de production, éviter de couper brutalement
l’interface réseau de la VM.

La méthode la plus maîtrisée consiste à désactiver temporairement le
serveur primaire dans le WLC ou à l’arrêter pendant une fenêtre de
maintenance contrôlée.

### Option A : désactiver temporairement FreeRADIUS 01 dans le WLC

Dans l’interface Mobility Express :

```text
Wireless Settings
→ RADIUS
→ Authentication
→ FreeRADIUS 01
→ Disable
```

Ou utiliser la commande adaptée à la version WLC :

```text
config radius auth disable <INDEX_RADIUS_01>
```

> Vérifier la syntaxe exacte avec `?` sur la version WLC concernée.
> Ne pas exécuter une commande générique sans contrôle préalable.

### Option B : arrêter temporairement le service

Sur FreeRADIUS 01 :

```bash
systemctl stop freeradius
systemctl is-active freeradius
```

Résultat attendu :

```text
inactive
```

Cette méthode ne doit être utilisée que si le secondaire a été validé
avant le test.

### Générer une nouvelle authentification

Sur le poste pilote :

```text
1. Se déconnecter de CORP-SECURE.
2. Désactiver/réactiver le WiFi si nécessaire.
3. Se reconnecter au SSID.
4. S’authentifier avec un utilisateur AD valide.
```

### Vérifier FreeRADIUS 02

Dans les logs FreeRADIUS 02, rechercher :

```text
PEAP Session established
MS-CHAP authentication succeeded
EAP: Sending EAP Success
Sent Access-Accept
MS-MPPE-Recv-Key
MS-MPPE-Send-Key
```

Ces éléments prouvent que FreeRADIUS 02 a réellement traité une
authentification WiFi complète.

### Vérifier le WLC

```bash
show radius auth statistics
```

Les compteurs du serveur secondaire doivent augmenter.

### Résultat attendu

```text
FreeRADIUS 01 indisponible
→ le WLC sélectionne FreeRADIUS 02
→ le poste pilote rejoint le WiFi
→ FreeRADIUS 02 envoie Access-Accept
```

---

## 9. Restaurer FreeRADIUS 01

Si le service a été arrêté :

```bash
systemctl start freeradius
systemctl is-active freeradius

freeradius -XC
journalctl -u freeradius -n 50 --no-pager
```

Résultat attendu :

```text
active
Configuration appears to be OK
```

Si le serveur a été désactivé dans le WLC :

```text
Wireless Settings
→ RADIUS
→ Authentication
→ FreeRADIUS 01
→ Enable
```

Puis sauvegarder :

```bash
save config
```

Vérifier :

```bash
show radius summary
```

---

## 10. Test 3 : bascule vers FreeRADIUS 01

Objectif :

```text
Vérifier que FreeRADIUS 01 peut authentifier un client
lorsque FreeRADIUS 02 est indisponible.
```

### Étapes

1. Vérifier que FreeRADIUS 01 est actif.
2. Préparer les logs sur FreeRADIUS 01.
3. Désactiver temporairement FreeRADIUS 02 dans le WLC ou arrêter son service.
4. Déconnecter le poste pilote du SSID.
5. Reconnecter le poste.
6. Vérifier les logs FreeRADIUS 01.
7. Vérifier les statistiques RADIUS du WLC.
8. Restaurer FreeRADIUS 02.
9. Sauvegarder la configuration WLC si elle a été modifiée.

### Résultat attendu

Dans les logs FreeRADIUS 01 :

```text
PEAP Session established
eap_peap: Success
EAP: Sending EAP Success
Sent Access-Accept
```

Conclusion :

```text
FreeRADIUS 02 indisponible
→ le WLC utilise FreeRADIUS 01
→ l’authentification WiFi continue de fonctionner
```

---

## 11. Résultats de validation

Une haute disponibilité Authentication est considérée comme validée si les
deux tests suivants réussissent :

```text
FreeRADIUS 01 temporairement indisponible
→ FreeRADIUS 02 authentifie le poste pilote.

FreeRADIUS 02 temporairement indisponible
→ FreeRADIUS 01 authentifie le poste pilote.
```

---

## 12. Authentication et Accounting

Il faut distinguer les deux validations.

| Flux | Port | Objectif | État à tester |
|---|---:|---|---|
| RADIUS Authentication | UDP 1812 | Autoriser/refuser le WiFi | Bascule dans les deux sens |
| RADIUS Accounting | UDP 1813 | Enregistrer les sessions | Réception et bascule à tester séparément |

Un test de bascule Authentication réussi ne prouve pas automatiquement que
la bascule Accounting est également fonctionnelle.

La validation Accounting est décrite dans :

```text
docs/09-radius-accounting.md
```

---

## Étape suivante

Poursuivre avec :

```text
docs/09-radius-accounting.md
```

Cette prochaine fiche couvre :

```text
UDP 1813
Accounting-Start
Accounting-Interim-Update
Accounting-Stop
Fichiers radacct
Filtrage des sessions
Statistiques WLC
Traçabilité utilisateur
Rétention des journaux
Test de
