# Active Directory, LDAPS, Samba, Winbind et ntlm_auth

## Objectif

Cette procédure décrit l’intégration d’un serveur Debian FreeRADIUS à
Active Directory.

Elle permet de préparer la chaîne suivante :

```text
FreeRADIUS
→ mschap
→ ntlm_auth
→ Winbind
→ Samba
→ Active Directory
```

Cette chaîne est nécessaire pour valider les authentifications
PEAP/EAP-MSCHAPv2 avec les comptes utilisateurs Active Directory.

La procédure couvre :

```text
CA interne
LDAPS
Compte de service LDAP
Kerberos
Samba
Jointure Active Directory
Winbind
ntlm_auth
Permissions du compte freerad
```

> Les adresses IP, noms DNS, comptes, domaines, unités d’organisation et
> mots de passe sont anonymisés.

---

## 1. Rôles des composants

| Composant | Rôle |
|---|---|
| Active Directory | Stocke les comptes utilisateurs, groupes, ordinateurs et mots de passe |
| DNS Active Directory | Résout les noms internes, DC et services Kerberos |
| LDAPS | Permet des recherches LDAP sécurisées via TLS |
| Kerberos | Permet l’authentification au domaine et la jointure Linux/AD |
| Samba | Permet à Debian de communiquer avec Active Directory |
| Winbind | Permet à Linux de résoudre utilisateurs, groupes et SID AD |
| ntlm_auth | Sert de pont entre FreeRADIUS et Winbind |
| FreeRADIUS | Traite les requêtes 802.1X et délègue MS-CHAPv2 à ntlm_auth |

---

## 2. Prérequis Active Directory

Avant de configurer le serveur Debian, vérifier les éléments suivants.

```text
Le domaine Active Directory existe.
Le DNS AD est accessible depuis Debian.
Le serveur Debian résout les noms des DC.
Le port TCP 636 est disponible pour LDAPS.
L’heure de Debian est synchronisée.
Un compte autorisé peut joindre une machine au domaine.
Un compte de service LDAP existe si LDAP doit être utilisé.
```

Exemple d’environnement anonymisé :

| Élément | Valeur |
|---|---|
| Domaine DNS | `example.local` |
| Domaine NetBIOS | `EXAMPLE` |
| DC principal | `dc01.example.local` |
| DC secondaire | `dc02.example.local` |
| DNS / DC principal | `10.20.10.10` |
| DNS / DC secondaire | `10.20.10.11` |
| Base DN LDAP | `DC=example,DC=local` |
| Serveur RADIUS | `radius02.example.local` |

---

## 3. Compte de service LDAP

Un compte de service LDAP permet à FreeRADIUS de rechercher des objets
dans Active Directory.

Ce compte doit être :

```text
Dédié à FreeRADIUS.
Sans privilèges d’administration.
Utilisé uniquement pour les recherches LDAP.
Limité aux permissions nécessaires.
Protégé par un mot de passe fort.
Documenté sans exposer le mot de passe.
```

Exemple :

```text
Nom du compte :
svc_radius_ldap

DN LDAP :
CN=svc_radius_ldap,OU=ServiceAccounts,DC=example,DC=local
```

Le compte de service peut notamment servir à :

```text
Rechercher un utilisateur.
Rechercher des groupes Active Directory.
Lire certains attributs LDAP.
Appliquer ultérieurement des règles RADIUS par groupe.
```

Il ne remplace pas Winbind ou `ntlm_auth` pour la validation
EAP-MSCHAPv2.

---

## 4. Vérifier DNS et connectivité

Avant toute jointure au domaine :

```bash
getent hosts dc01.example.local
getent hosts dc02.example.local

nslookup example.local
nslookup dc01.example.local
nslookup dc02.example.local

ping -c 2 dc01.example.local
ping -c 2 dc02.example.local
```

Résultat attendu :

```text
Les deux DC sont résolus par DNS.
Les noms correspondent aux bonnes adresses IP.
Les contrôleurs de domaine sont joignables.
```

Vérifier également que Debian utilise les DNS Active Directory :

```bash
cat /etc/resolv.conf
```

Exemple attendu :

```text
nameserver 10.20.10.10
nameserver 10.20.10.11
search example.local
```

---

## 5. Installer et vérifier la CA interne

La CA interne doit être installée sur Debian avant d’utiliser LDAPS.

Le certificat CA doit être installé dans :

```text
/usr/local/share/ca-certificates/
```

Exemple :

```bash
ls -l /usr/local/share/ca-certificates/
```

Contrôler le certificat :

```bash
openssl x509 \
  -in /usr/local/share/ca-certificates/CORP-ROOT-CA.crt \
  -noout \
  -subject \
  -issuer \
  -dates
```

Une CA racine autosignée présente généralement :

```text
subject = issuer
```

Mettre à jour le magasin de confiance Debian :

```bash
update-ca-certificates --fresh
```

Contrôler la présence de la CA :

```bash
ls /etc/ssl/certs | grep -i corp
```

---

## 6. Tester LDAPS

LDAPS utilise TCP 636.

Tester le certificat présenté par le contrôleur de domaine :

```bash
openssl s_client \
  -connect dc01.example.local:636 \
  -servername dc01.example.local \
  -CAfile /etc/ssl/certs/ca-certificates.crt \
  -verify_return_error </dev/null
```

Résultat obligatoire :

```text
Verify return code: 0 (ok)
```

Ce test confirme :

```text
Résolution DNS fonctionnelle.
Port TCP 636 joignable.
Service LDAPS actif.
Certificat LDAPS présenté par le DC.
Certificat validé par la CA interne.
Chaîne de confiance TLS correcte.
```

Ne pas passer à la suite tant que ce résultat n’est pas obtenu.

Ne pas contourner un problème de certificat avec :

```text
require_cert = allow
```

en production.

---

## 7. Tester le compte de service LDAP

Tester le bind LDAPS sans inscrire le mot de passe dans une commande :

```bash
ldapwhoami -x \
  -H ldaps://dc01.example.local \
  -D 'CN=svc_radius_ldap,OU=ServiceAccounts,DC=example,DC=local' \
  -W
```

L’option `-W` demande le mot de passe de manière interactive.

Résultat attendu, sous une forme équivalente :

```text
u:EXAMPLE\svc_radius_ldap
```

Tester une recherche utilisateur :

```bash
ldapsearch -x \
  -H ldaps://dc01.example.local \
  -D 'CN=svc_radius_ldap,OU=ServiceAccounts,DC=example,DC=local' \
  -W \
  -b 'DC=example,DC=local' \
  '(sAMAccountName=user.test)' \
  dn
```

Résultat attendu :

```text
result: 0 Success
numEntries: 1
```

La sortie doit également contenir le DN de l’utilisateur trouvé.

Exemple :

```text
dn: CN=User Test,OU=Users,DC=example,DC=local
```

---

## 8. Kerberos

Kerberos est utilisé par Active Directory pour l’authentification des
machines et des utilisateurs du domaine.

Kerberos dépend de trois éléments :

```text
DNS correct.
Heure synchronisée.
Nom de domaine correct.
```

Obtenir un ticket Kerberos :

```bash
kinit Administrator@EXAMPLE.LOCAL
```

Afficher les tickets :

```bash
klist
```

Résultat attendu :

```text
Default principal: Administrator@EXAMPLE.LOCAL
```

La présence d’un ticket valide confirme :

```text
DNS fonctionnel.
NTP fonctionnel.
Domaine correct.
DC joignable.
Kerberos fonctionnel.
```

Supprimer un ticket de test si nécessaire :

```bash
kdestroy
```

---

## 9. Configurer Samba

Sauvegarder la configuration avant toute modification :

```bash
cp -a /etc/samba/smb.conf \
  /root/smb.conf.bak-$(date +%F-%H%M)
```

Éditer :

```bash
nano /etc/samba/smb.conf
```

Exemple de configuration :

```ini
[global]
    workgroup = EXAMPLE
    realm = EXAMPLE.LOCAL
    security = ADS

    kerberos method = secrets and keytab

    winbind use default domain = yes
    winbind refresh tickets = yes
    winbind offline logon = no

    winbind enum users = yes
    winbind enum groups = yes

    idmap config * : backend = tdb
    idmap config * : range = 3000-7999

    template shell = /bin/bash
    template homedir = /home/%U

    log file = /var/log/samba/log.%m
    max log size = 1000
```

Valider la syntaxe :

```bash
testparm -s
```

Résultat attendu :

```text
Loaded services file OK.
ROLE_DOMAIN_MEMBER
```

---

## 10. Joindre Debian au domaine

Vérifier les informations Active Directory disponibles :

```bash
net ads info
```

Joindre ensuite le domaine avec un compte autorisé :

```bash
net ads join -U 'EXAMPLE\Administrator'
```

Le mot de passe est demandé de manière interactive.

Résultat attendu :

```text
Joined '<HOSTNAME>' to dns domain 'example.local'
```

Vérifier la jointure :

```bash
net ads testjoin
```

Résultat obligatoire :

```text
Join is OK
```

---

## 11. Activer et contrôler Winbind

Démarrer Winbind au démarrage :

```bash
systemctl enable --now winbind
```

Contrôler le service :

```bash
systemctl status winbind --no-pager
```

Vérifier le secret de confiance avec Active Directory :

```bash
wbinfo -t
```

Résultat attendu :

```text
checking the trust secret via RPC calls succeeded
```

Lister des utilisateurs du domaine :

```bash
wbinfo -u | head
```

Lister des groupes du domaine :

```bash
wbinfo -g | head
```

Résoudre un utilisateur :

```bash
wbinfo -n user.test
```

Résultat attendu :

```text
S-1-5-21-...
```

Le SID confirme que Winbind peut interroger Active Directory.

---

## 12. Tester ntlm_auth

`ntlm_auth` permet à FreeRADIUS de demander à Winbind et Active Directory
de valider une authentification MS-CHAPv2.

Tester un utilisateur :

```bash
ntlm_auth \
  --username=user.test \
  --domain=EXAMPLE \
  --password
```

Le mot de passe est demandé à l’invite.

Résultat attendu :

```text
NT_STATUS_OK: Success
```

Cette commande valide la chaîne :

```text
ntlm_auth
→ Winbind
→ Samba
→ Active Directory
```

---

## 13. Tester MS-CHAPv2

Le test MS-CHAPv2 nécessite un vrai challenge et une vraie réponse NT.

Exemple de structure :

```bash
ntlm_auth \
  --request-nt-key \
  --allow-mschapv2 \
  --username='user.test' \
  --domain='EXAMPLE' \
  --challenge='<CHALLENGE_HEX>' \
  --nt-response='<NT_RESPONSE_HEX>'
```

Résultat attendu :

```text
NT_KEY: ...
```

Les valeurs `<CHALLENGE_HEX>` et `<NT_RESPONSE_HEX>` doivent être
réelles. Des valeurs vides ne constituent pas un test MS-CHAPv2 utile.

---

## 14. Permissions du compte freerad

FreeRADIUS ne s’exécute généralement pas avec le compte `root`.

Il utilise le compte système :

```text
Utilisateur :
freerad

Groupe :
freerad
```

Le processus FreeRADIUS doit pouvoir utiliser les services Winbind.

Vérifier les groupes du compte :

```bash
id freerad
```

Dans certains environnements, le compte doit appartenir au groupe :

```text
winbindd_priv
```

Ajouter le compte si nécessaire :

```bash
usermod -aG winbindd_priv freerad
```

Vérifier de nouveau :

```bash
id freerad
```

Le groupe `winbindd_priv` doit apparaître.

Redémarrer FreeRADIUS après cette modification :

```bash
systemctl restart freeradius
```

---

## 15. Test critique avec freerad

Le test final doit être exécuté avec le même compte système que
FreeRADIUS.

```bash
sudo -u freerad /usr/bin/ntlm_auth \
  --request-nt-key \
  --allow-mschapv2 \
  --username='user.test' \
  --domain='EXAMPLE' \
  --challenge='<CHALLENGE_HEX>' \
  --nt-response='<NT_RESPONSE_HEX>'
```

Résultat attendu :

```text
NT_KEY: ...
```

Ce test prouve que la chaîne de production fonctionne avec les
permissions réellement utilisées par FreeRADIUS :

```text
freerad
→ ntlm_auth
→ Winbind
→ Samba
→ Active Directory
```

Tant que ce test échoue, ne pas poursuivre vers la configuration
PEAP/EAP-MSCHAPv2 du WLC.

---

## 16. Dépannage courant

| Symptôme | Vérification |
|---|---|
| Le DC ne répond pas | `getent hosts dc01.example.local` |
| Le DC n’est pas résolu | `/etc/resolv.conf`, `nslookup` |
| LDAPS échoue | `openssl s_client` |
| Erreur de certificat LDAPS | CA interne, FQDN, SAN et chaîne de confiance |
| Kerberos échoue | DNS, NTP, `kinit`, `klist` |
| Jointure AD échoue | `net ads info`, `net ads testjoin` |
| Winbind échoue | `systemctl status winbind`, `wbinfo -t` |
| Utilisateur non résolu | `wbinfo -u`, `wbinfo -n user.test` |
| ntlm_auth échoue | Domaine, mot de passe, Winbind, trust AD |
| ntlm_auth marche en root seulement | Vérifier le groupe `winbindd_priv` |
| FreeRADIUS échoue avec Winbind | Tester `sudo -u freerad ntlm_auth` |

---

## Étape suivante

Une fois Active Directory, LDAPS, Samba, Winbind et `ntlm_auth` validés,
poursuivre avec :

```text
docs/05-peap-mschapv2-authentication.md
```

Cette prochaine fiche couvre :

```text
Configuration LDAP dans FreeRADIUS
Normalisation des utilisateurs
Module mschap
inner-tunnel
Certificats EAP
PEAP
EAP-MSCHAPv2
Debug FreeRADIUS
Access-Accept et
