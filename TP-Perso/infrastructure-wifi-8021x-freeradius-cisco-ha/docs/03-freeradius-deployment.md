# Déploiement initial d’un serveur FreeRADIUS

## Objectif

Cette fiche décrit la préparation complète d’un serveur Debian destiné à
héberger FreeRADIUS dans une architecture WiFi d’entreprise : réseau,
DNS/DHCP, NTP, UFW, paquets, CA/LDAPS, Active Directory, certificats EAP
et premiers tests.

Toutes les valeurs suivantes sont anonymisées et doivent être adaptées.

---

## 1. Pré-requis et dimensionnement

| Ressource | Minimum | Recommandé |
|---|---:|---:|
| vCPU | 2 | 4 |
| RAM | 2 Go | 4 Go |
| Disque | 20 Go | 40 Go ou plus |
| OS | Debian stable | Debian stable |

Prévoir deux VM indépendantes pour la haute disponibilité. Chaque VM doit
avoir son propre hostname, IP, identité Samba/AD, machine-id, clé privée
et certificat EAP.

Exemple :

```text
FreeRADIUS 01 : radius01.example.local — 10.20.20.11
FreeRADIUS 02 : radius02.example.local — 10.20.20.12
WLC Cisco      : wlc01.example.local    — 10.20.30.10
DC01 / DNS     : dc01.example.local     — 10.20.10.10
DC02 / DNS     : dc02.example.local     — 10.20.10.11
```

---

## 2. Réseau statique Debian

FreeRADIUS doit être joignable depuis le WLC, les DC/DNS, les
administrateurs et la supervision.

Définir le hostname :

```bash
hostnamectl set-hostname radius02
hostname
hostname -f
```

Exemple `/etc/network/interfaces` :

```ini
auto ens33
iface ens33 inet static
    address 10.20.20.12/24
    gateway 10.20.20.1
    dns-nameservers 10.20.10.10 10.20.10.11
```

Avant toute modification :

```bash
cp -a /etc/network/interfaces /root/interfaces.bak-$(date +%F-%H%M)

ip -br addr
ip route
cat /etc/resolv.conf
```

Une erreur réseau coupe SSH. Ouvrir la console VMware avant de relancer
le réseau :

```bash
systemctl restart networking
```

Ou redémarrer la VM depuis la console après validation :

```bash
reboot
```

Contrôles :

```bash
ip -br addr
ip route

ping -c 2 10.20.20.1
ping -c 2 10.20.10.10
ping -c 2 10.20.30.10
```

---

## 3. Préparation DNS et DHCP Windows

### 3.1 DNS Active Directory

Le serveur Debian doit utiliser les DNS Active Directory, jamais un DNS
public pour résoudre le domaine interne.

```bash
cat /etc/resolv.conf

nslookup example.local
nslookup dc01.example.local
nslookup dc02.example.local

getent hosts dc01.example.local
```

### 3.2 Créer l’enregistrement A du serveur RADIUS

Créer le DNS avant de générer le certificat EAP.

Sur Windows :

```text
Win + R
→ dnsmgmt.msc
→ Zones de recherche directes
→ example.local
→ clic droit
→ Nouvel hôte (A ou AAAA)
```

Exemple :

```text
Nom :
radius02

Adresse IP :
10.20.20.12
```

Puis vérifier depuis Debian :

```bash
nslookup radius02.example.local
getent hosts radius02.example.local
```

Le FQDN est utilisé dans :

```text
Le certificat EAP.
Le profil WiFi Windows.
La liste des serveurs RADIUS approuvés.
La documentation.
```

---

## 4. NTP et outils Debian

L’heure doit être cohérente entre FreeRADIUS, DC, WLC et clients.
Kerberos, les certificats et les logs en dépendent.

```bash
apt update
apt upgrade -y

apt install -y \
  curl \
  wget \
  vim \
  net-tools \
  dnsutils \
  openssl \
  ldap-utils \
  chrony \
  ca-certificates

systemctl enable --now chrony

chronyc sources -v
timedatectl
```

Résultat attendu :

```text
System clock synchronized: yes
NTP service: active
Time zone: Europe/Paris
```

---

## 5. Pare-feu UFW

Installer UFW :

```bash
apt install -y ufw

ufw default deny incoming
ufw default allow outgoing
```

Autoriser SSH avant l’activation :

```bash
ufw allow from 10.20.99.0/24 to any port 22 proto tcp
```

Autoriser RADIUS uniquement depuis le WLC :

```bash
ufw allow from 10.20.30.10 to any port 1812 proto udp
ufw allow from 10.20.30.10 to any port 1813 proto udp
```

Si plusieurs NAS utilisent RADIUS, ajouter une règle par IP :

```bash
ufw allow from <IP_NAS_2> to any port 1812 proto udp
ufw allow from <IP_NAS_2> to any port 1813 proto udp
```

Activer et contrôler :

```bash
ufw enable

ufw status numbered
ufw status verbose
```

---

## 6. Installer FreeRADIUS et les composants AD

```bash
apt install -y \
  krb5-user \
  samba \
  winbind \
  libnss-winbind \
  libpam-winbind \
  ntlm-auth \
  freeradius \
  freeradius-eap \
  freeradius-ldap \
  freeradius-utils
```

Contrôler :

```bash
smbd --version
wbinfo --version
ntlm_auth --version
freeradius -v

systemctl enable --now freeradius
systemctl status freeradius --no-pager

ss -lunp | grep -E ':(1812|1813)\b'
```

Les emplacements FreeRADIUS importants :

```text
/etc/freeradius/3.0/clients.conf
/etc/freeradius/3.0/mods-enabled/
/etc/freeradius/3.0/sites-enabled/default
/etc/freeradius/3.0/sites-enabled/inner-tunnel
/etc/freeradius/3.0/certs/
/var/log/freeradius/radacct/
```

Avant modification :

```bash
cp -a /etc/freeradius/3.0 \
  /root/freeradius-3.0.bak-$(date +%F-%H%M)

cp -a /etc/samba \
  /root/samba.bak-$(date +%F-%H%M)
```

Ne jamais placer de sauvegarde dans :

```text
/etc/freeradius/3.0/mods-enabled/
```

FreeRADIUS chargerait ce fichier comme un module.

---

## 7. Installer la CA interne et tester LDAPS

Copier la CA depuis Windows :

```powershell
scp C:\TFTP\CORP-ROOT-CA.crt admin@10.20.20.12:/tmp/CORP-ROOT-CA.crt
```

Tester le format :

```bash
head -n 1 /tmp/CORP-ROOT-CA.crt
```

Si le certificat est déjà en PEM :

```bash
mv /tmp/CORP-ROOT-CA.crt \
  /usr/local/share/ca-certificates/CORP-ROOT-CA.crt

chmod 644 \
  /usr/local/share/ca-certificates/CORP-ROOT-CA.crt

update-ca-certificates --fresh
```

S’il est en DER :

```bash
mv /tmp/CORP-ROOT-CA.crt \
  /usr/local/share/ca-certificates/CORP-ROOT-CA.der

openssl x509 \
  -inform DER \
  -in /usr/local/share/ca-certificates/CORP-ROOT-CA.der \
  -outform PEM \
  -out /usr/local/share/ca-certificates/CORP-ROOT-CA.crt

chmod 644 \
  /usr/local/share/ca-certificates/CORP-ROOT-CA.crt

update-ca-certificates --fresh
```

Vérifier la CA :

```bash
openssl x509 \
  -in /usr/local/share/ca-certificates/CORP-ROOT-CA.crt \
  -noout \
  -subject \
  -issuer \
  -dates
```

Tester LDAPS avant FreeRADIUS :

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

---

## 8. Kerberos, Samba et Winbind

Exemple minimal `/etc/samba/smb.conf` :

```ini
[global]
    workgroup = EXAMPLE
    realm = EXAMPLE.LOCAL
    security = ADS

    kerberos method = secrets and keytab

    winbind use default domain = yes
    winbind enum users = yes
    winbind enum groups = yes

    idmap config * : backend = tdb
    idmap config * : range = 3000-7999
```

Valider Samba :

```bash
testparm -s
```

Obtenir un ticket Kerberos :

```bash
kinit Administrator@EXAMPLE.LOCAL
klist
```

Joindre le domaine :

```bash
net ads join -U 'EXAMPLE\Administrator'
```

Vérifier :

```bash
net ads testjoin

systemctl enable --now winbind

wbinfo -t
wbinfo -n user.test
```

Résultats attendus :

```text
Join is OK

checking the trust secret via RPC calls succeeded
```

Tester l’authentification AD :

```bash
ntlm_auth \
  --username=user.test \
  --domain=EXAMPLE \
  --password
```

Résultat attendu :

```text
NT_STATUS_OK: Success
```

---

## 9. Préparer FreeRADIUS pour le WLC

Créer un secret sans le documenter :

```bash
openssl rand -base64 32
```

Dans :

```text
/etc/freeradius/3.0/clients.conf
```

ajouter :

```text
client wlc_cisco {
    ipaddr = 10.20.30.10
    secret = <RADIUS_SHARED_SECRET>
    shortname = WLC-CISCO
    require_message_authenticator = yes
}
```

Valider puis redémarrer :

```bash
freeradius -XC

systemctl restart freeradius
systemctl status freeradius --no-pager
```

---

## 10. Certificat EAP

Le certificat RADIUS doit contenir un FQDN, un SAN DNS et l’usage étendu
`Server Authentication`.

```bash
install -d -m 750 -o root -g freerad \
  /etc/freeradius/3.0/certs/private

openssl genpkey \
  -algorithm RSA \
  -pkeyopt rsa_keygen_bits:3072 \
  -out /etc/freeradius/3.0/certs/private/radius02.key

chown root:freerad \
  /etc/freeradius/3.0/certs/private/radius02.key

chmod 640 \
  /etc/freeradius/3.0/certs/private/radius02.key
```

Créer une CSR :

```bash
openssl req -new \
  -key /etc/freeradius/3.0/certs/private/radius02.key \
  -out /root/radius02.example.local.csr \
  -subj '/CN=radius02.example.local/O=EXAMPLE/OU=IT/C=FR' \
  -addext 'subjectAltName = DNS:radius02.example.local' \
  -addext 'extendedKeyUsage = serverAuth'
```

Faire signer la CSR par la CA interne, puis vérifier le certificat :

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

Configurer le bloc EAP existant :

```text
private_key_file = ${certdir}/private/radius02.key
certificate_file = ${certdir}/radius02.crt
tls_min_version = '1.2'
require_client_cert = no
```

Ne pas créer un second bloc :

```text
tls-config tls-common
```

---

## 11. Contrôle avant WLC

```bash
freeradius -XC

systemctl is-active freeradius
systemctl is-active winbind

net ads testjoin
wbinfo -t

ss -lunp | grep -E ':(1812|1813)\b'

ufw status verbose
```

---

## 12. Suite

Poursuivre avec la configuration détaillée de LDAPS, Winbind, `ntlm_auth`,
`mschap`, `inner-tunnel`, PEAP et EAP-MSCHAPv2 dans :

```text
04-active-directory-ldaps-winbind.md
05-peap-mschapv2-authentication.md
```
