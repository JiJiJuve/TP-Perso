# PEAP, EAP-MSCHAPv2 et authentification FreeRADIUS

## Objectif

Cette procédure configure et valide l’authentification WiFi utilisateur
avec :

```text
WPA2-Enterprise
IEEE 802.1X
PEAP
TLS
EAP-MSCHAPv2
FreeRADIUS
ntlm_auth
Winbind
Active Directory
```

Chaîne cible :

```text
Client Windows
→ WLC Cisco
→ FreeRADIUS

FreeRADIUS
→ PEAP / tunnel TLS
→ inner-tunnel
→ mschap
→ ntlm_auth
→ Winbind
→ Active Directory

FreeRADIUS
→ Access-Accept ou Access-Reject
→ WLC Cisco
```

> Les noms, IP, domaines, DN LDAP et secrets sont anonymisés.
> Adapter les placeholders avant toute utilisation réelle.

---

## 1. Prérequis

Avant de modifier FreeRADIUS, les éléments suivants doivent fonctionner :

```text
DNS Active Directory fonctionnel.
NTP synchronisé.
FreeRADIUS actif.
Serveur Debian joint au domaine Active Directory.
Samba fonctionnel.
Winbind actif.
wbinfo -t réussi.
ntlm_auth réussi.
ntlm_auth exécuté avec freerad réussi.
Certificat EAP disponible.
WLC déclaré dans clients.conf.
```

Commandes de contrôle :

```bash
systemctl is-active freeradius
systemctl is-active winbind

net ads testjoin
wbinfo -t

ntlm_auth \
  --username=user.test \
  --domain=EXAMPLE \
  --password

id freerad

freeradius -XC
```

Résultats attendus :

```text
active
active
Join is OK
checking the trust secret via RPC calls succeeded
NT_STATUS_OK: Success
Configuration appears to be OK
```

---

## 2. Les virtual servers FreeRADIUS

FreeRADIUS utilise deux serveurs virtuels importants pour PEAP.

| Fichier | Rôle |
|---|---|
| `/etc/freeradius/3.0/sites-enabled/default` | Reçoit les requêtes RADIUS du WLC et gère EAP/PEAP externe |
| `/etc/freeradius/3.0/sites-enabled/inner-tunnel` | Traite l’authentification interne EAP-MSCHAPv2 |

Flux :

```text
WLC Cisco
→ default

default
→ EAP
→ PEAP
→ tunnel TLS

Tunnel PEAP
→ inner-tunnel

inner-tunnel
→ mschap
→ ntlm_auth
→ Winbind
→ Active Directory
```

Ne pas modifier `default` ou `inner-tunnel` sans sauvegarde et sans
validation de syntaxe.

---

## 3. Sauvegarder les fichiers

Exécuter avant toute modification :

```bash
cp -a /etc/freeradius/3.0/sites-enabled/default \
  /root/default.bak-$(date +%F-%H%M)

cp -a /etc/freeradius/3.0/sites-enabled/inner-tunnel \
  /root/inner-tunnel.bak-$(date +%F-%H%M)

cp -a /etc/freeradius/3.0/mods-enabled/mschap \
  /root/mschap.bak-$(date +%F-%H%M)

cp -a /etc/freeradius/3.0/mods-enabled/eap \
  /root/eap.bak-$(date +%F-%H%M)
```

Ne jamais sauvegarder un fichier dans :

```text
/etc/freeradius/3.0/mods-enabled/
```

FreeRADIUS charge les fichiers présents dans ce dossier comme modules.

---

## 4. Contrôler la configuration existante

Avant de modifier, afficher les blocs réellement utilisés.

```bash
grep -n -A 120 'authorize {' \
  /etc/freeradius/3.0/sites-enabled/default

grep -n -A 120 'authorize {' \
  /etc/freeradius/3.0/sites-enabled/inner-tunnel

grep -n -A 100 'authenticate {' \
  /etc/freeradius/3.0/sites-enabled/inner-tunnel

grep -n -A 20 -B 5 'ntlm_auth' \
  /etc/freeradius/3.0/mods-enabled/mschap

grep -nE 'private_key_file|certificate_file|ca_file|tls_min_version' \
  /etc/freeradius/3.0/mods-enabled/eap
```

Ne remplace jamais un fichier complet uniquement parce qu’un exemple
Internet présente une structure différente.

La configuration réellement installée est toujours la référence.

---

## 5. Vérifier le module mschap

Le module `mschap` permet à FreeRADIUS de traiter MS-CHAPv2 et d’appeler
`ntlm_auth`.

Le fichier concerné est :

```text
/etc/freeradius/3.0/mods-enabled/mschap
```

Vérifier que le fichier existe :

```bash
ls -l /etc/freeradius/3.0/mods-enabled/mschap
```

Ouvrir le fichier :

```bash
nano /etc/freeradius/3.0/mods-enabled/mschap
```

Chercher la directive :

```text
ntlm_auth =
```

Si elle est commentée avec un `#`, retirer uniquement le `#` de cette
ligne.

La logique attendue est :

```text
ntlm_auth = "/usr/bin/ntlm_auth \
  --request-nt-key \
  --allow-mschapv2 \
  --username=%{mschap:User-Name} \
  --domain=EXAMPLE \
  --challenge=%{%{mschap:Challenge}:-00} \
  --nt-response=%{%{mschap:NT-Response}:-00}"
```

Adapter uniquement :

```text
EXAMPLE
```

avec le nom NetBIOS réel du domaine.

Exemple :

```text
--domain=EXAMPLE
```

Ne pas modifier :

```text
--request-nt-key
--allow-mschapv2
--challenge=
--nt-response=
```

Ne pas ajouter d’espace incorrect.

Exemples incorrects :

```text
% {mschap:User-Name}

--nt response
```

Exemples corrects :

```text
%{mschap:User-Name}

--nt-response
```

Vérifier que `ntlm_auth` existe :

```bash
command -v ntlm_auth
```

Résultat attendu :

```text
/usr/bin/ntlm_auth
```

Enregistrer dans Nano :

```text
Ctrl + O
→ Entrée
→ Ctrl + X
```

---

## 6. Vérifier les permissions Winbind

FreeRADIUS s’exécute généralement avec le compte système :

```text
freerad
```

Ce compte doit pouvoir utiliser Winbind.

Vérifier ses groupes :

```bash
id freerad
```

Si `winbindd_priv` n’apparaît pas et que `ntlm_auth` fonctionne en root
mais pas avec `freerad`, ajouter le compte :

```bash
usermod -aG winbindd_priv freerad
```

Vérifier de nouveau :

```bash
id freerad
```

Le résultat doit contenir :

```text
winbindd_priv
```

Tester ensuite avec le compte réellement utilisé par FreeRADIUS :

```bash
sudo -u freerad /usr/bin/ntlm_auth \
  --username=user.test \
  --domain=EXAMPLE \
  --password
```

Résultat attendu :

```text
NT_STATUS_OK: Success
```

> Pour un test MS-CHAPv2 complet, `ntlm_auth` doit recevoir un vrai
> challenge et une vraie NT-Response. Le test ci-dessus valide surtout
> l’accès de `freerad` à Winbind et Active Directory.

---

## 7. Configurer inner-tunnel

Le fichier concerné est :

```text
/etc/freeradius/3.0/sites-enabled/inner-tunnel
```

Ouvrir le fichier :

```bash
nano /etc/freeradius/3.0/sites-enabled/inner-tunnel
```

Chercher le bloc :

```text
authorize {
```

Le bloc EAP doit rester présent avant les traitements suivants :

```text
eap {
    ok = return
}
```

Cette logique évite d’exécuter inutilement certains modules pour chaque
paquet intermédiaire de négociation PEAP.

Exemple de structure à conserver :

```text
authorize {
    filter_username
    chap
    mschap
    suffix

    update control {
        &Proxy-To-Realm := LOCAL
    }

    eap {
        ok = return
    }

    files
    -sql

    expiration
    logintime
    pap
}
```

### LDAP dans inner-tunnel

Selon le besoin, la ligne LDAP peut être présente sous deux formes.

```text
ldap
```

ou :

```text
-ldap
```

Signification :

| Ligne | Signification |
|---|---|
| `ldap` | Le module LDAP est appelé dans inner-tunnel |
| `-ldap` | Le module LDAP est volontairement désactivé dans inner-tunnel |

LDAP peut être activé dans `inner-tunnel` si tu as besoin de rechercher
des groupes ou attributs Active Directory dans le tunnel.

Mais LDAP ne doit jamais remplacer le flux :

```text
mschap
→ ntlm_auth
→ Winbind
→ Active Directory
```

Ne force pas cette ligne :

```text
Auth-Type := LDAP
```

dans le flux PEAP/EAP-MSCHAPv2.

Ne décommente pas non plus un bloc LDAP dans `authenticate` juste pour
essayer de résoudre une erreur MS-CHAPv2.

### Bloc authenticate

Chercher le bloc :

```text
authenticate {
```

Le bloc MS-CHAP doit être présent :

```text
authenticate {
    Auth-Type PAP {
        pap
    }

    Auth-Type CHAP {
        chap
    }

    Auth-Type MS-CHAP {
        mschap
    }

    mschap
    eap
}
```

Le bloc essentiel est :

```text
Auth-Type MS-CHAP {
    mschap
}
```

Ne pas supprimer ce bloc.

Enregistrer le fichier :

```text
Ctrl + O
→ Entrée
→ Ctrl + X
```

---

## 8. Normaliser le nom utilisateur

Selon les clients, FreeRADIUS peut recevoir l’utilisateur sous plusieurs
formes :

```text
user.test

EXAMPLE\user.test

user.test@example.local
```

Un mauvais format peut empêcher `ntlm_auth` de valider l’utilisateur.

Vérifier la valeur réellement reçue dans les logs debug avant d’ajouter
une règle de transformation.

Pour lancer un debug :

```bash
systemctl stop freeradius
freeradius -X
```

Connecter ensuite un poste WiFi test et rechercher :

```text
User-Name =
```

Si l’identité reçue est :

```text
EXAMPLE\user.test
```

une logique de normalisation peut créer :

```text
Stripped-User-Name = user.test
```

Exemple de règle à adapter :

```text
if (&request:User-Name =~ /^EXAMPLE\\(.+)$/) {
    update request {
        &Stripped-User-Name := "%{1}"
    }
}
```

Cette règle ne doit être ajoutée que si elle correspond au format
réellement observé dans les logs.

Après le debug :

```text
Ctrl + C
```

Puis remettre le service :

```bash
systemctl start freeradius
systemctl is-active freeradius
```

---

## 9. Vérifier le certificat EAP

Le fichier EAP est :

```text
/etc/freeradius/3.0/mods-enabled/eap
```

Ouvrir le fichier :

```bash
nano /etc/freeradius/3.0/mods-enabled/eap
```

Chercher le bloc existant :

```text
tls-config tls-common {
```

Ne pas créer un deuxième bloc portant ce nom.

La configuration doit référencer le certificat et la clé privée du
serveur RADIUS.

Exemple :

```text
tls-config tls-common {
    private_key_file = ${certdir}/private/radius02.key
    certificate_file = ${certdir}/radius02.crt

    tls_min_version = "1.2"

    require_client_cert = no
}
```

Vérifier que les fichiers existent :

```bash
ls -l /etc/freeradius/3.0/certs/radius02.crt

ls -l /etc/freeradius/3.0/certs/private/radius02.key
```

La clé privée doit être protégée :

```text
Propriétaire :
root

Groupe :
freerad

Permissions :
640
```

Corriger si nécessaire :

```bash
chown root:freerad \
  /etc/freeradius/3.0/certs/private/radius02.key

chmod 640 \
  /etc/freeradius/3.0/certs/private/radius02.key
```

Vérifier le certificat :

```bash
openssl x509 \
  -in /etc/freeradius/3.0/certs/radius02.crt \
  -noout \
  -subject \
  -issuer \
  -dates \
  -ext subjectAltName \
  -ext extendedKeyUsage
```

Le certificat doit contenir idéalement :

```text
CN  = radius02.example.local
SAN = DNS:radius02.example.local
EKU = Server Authentication
```

---

## 10. Vérifier la correspondance clé/certificat

Le certificat et la clé privée doivent correspondre.

```bash
openssl x509 -noout -modulus \
  -in /etc/freeradius/3.0/certs/radius02.crt | openssl sha256

openssl rsa -noout -modulus \
  -in /etc/freeradius/3.0/certs/private/radius02.key | openssl sha256
```

Les deux empreintes doivent être identiques.

---

## 11. Valider avant redémarrage

Après chaque modification FreeRADIUS :

```bash
freeradius -XC
```

Résultat attendu :

```text
Configuration appears to be OK
```

Si la commande retourne une erreur :

```text
Ne pas redémarrer le service.
Lire l’erreur.
Restaurer le fichier de sauvegarde si nécessaire.
Corriger uniquement l’élément concerné.
Relancer freeradius -XC.
```

Si la validation est correcte :

```bash
systemctl restart freeradius

systemctl status freeradius --no-pager

journalctl -u freeradius -n 80 --no-pager
```

---

## 12. Tester une authentification WiFi réelle

Un test `radtest` peut être utile pour certains contrôles simples, mais il
ne remplace pas un test WiFi PEAP/EAP-MSCHAPv2 réel.

Pour analyser une connexion WiFi :

```bash
systemctl stop freeradius
freeradius -X
```

Depuis un poste Windows pilote :

```text
Se déconnecter du SSID CORP-SECURE.
Se reconnecter.
S’authentifier avec un compte Active Directory valide.
```

Dans la sortie debug, rechercher :

```text
PEAP Session established
eap_peap: Success
MS-CHAP authentication succeeded
EAP: Sending EAP Success
Sent Access-Accept
MS-MPPE-Recv-Key
MS-MPPE-Send-Key
```

Interprétation :

| Élément | Signification |
|---|---|
| `PEAP Session established` | Tunnel TLS PEAP établi |
| `MS-CHAP authentication succeeded` | Validation AD réussie |
| `EAP Success` | Succès envoyé au client |
| `Access-Accept` | Succès RADIUS envoyé au WLC |
| `MS-MPPE-*` | Matériel de clés de session généré |

Après le test :

```text
Ctrl + C
```

Puis :

```bash
systemctl start freeradius
systemctl is-active freeradius
journalctl -fu freeradius
```

Résultat attendu :

```text
active
```

---

## 13. Access-Accept et accès réseau

Un résultat :

```text
Access-Accept
```

signifie que l’authentification RADIUS est réussie.

Il ne garantit pas automatiquement un accès réseau complet.

Si le poste est authentifié mais n’obtient pas de connexion utilisable,
vérifier ensuite :

```text
DHCP
VLAN
Passerelle
Routage
DNS
Pare-feu
Politique WLC
```

---

## 14. Dépannage courant

| Symptôme | Cause probable | Contrôle |
|---|---|---|
| `Access-Reject` immédiat | WLC non déclaré ou mauvais secret | `clients.conf`, IP WLC, secret partagé |
| Échec PEAP | Certificat non approuvé | CA Windows, CN/SAN, noms autorisés |
| ntlm_auth échoue | Winbind ou trust AD | `wbinfo -t`, `net ads testjoin` |
| ntlm_auth marche en root seulement | Permissions freerad | `id freerad`, `winbindd_priv` |
| Nom utilisateur incorrect | Format `EXAMPLE\user` | Debug, `User-Name`, normalisation |
| LDAP fonctionne mais MS-CHAP échoue | LDAP ne valide pas MS-CHAPv2 | `mschap`, `ntlm_auth`, Winbind |
| FreeRADIUS ne démarre plus | Erreur de syntaxe | `freeradius -XC` |
| Port déjà occupé en debug | Service encore actif | `systemctl stop freeradius` |
| Access-Accept sans Internet | Problème réseau après authentification | DHCP, VLAN, route, DNS |

---

## Étape suivante

Poursuivre avec :

```text
docs/06-cisco-wlc-configuration.md
```

Cette prochaine fiche couvre :

```text
Cisco Mobility
