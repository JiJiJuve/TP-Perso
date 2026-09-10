# Fiche 2 — TLS et déploiement

Cette fiche explique comment générer un certificat TLS pour OpenBao, faire signer la CSR par la PKI, installer le certificat sur la VM, configurer le service, puis tester l’accès sécurisé au coffre.

## Sommaire
- [Choisir le nom d’hôte](#choisir-le-nom-dhôte)
- [Préparer OpenSSL](#préparer-openssl)
- [Générer la clé privée](#générer-la-clé-privée)
- [Générer la CSR](#générer-la-csr)
- [Faire signer la CSR](#faire-signer-la-csr)
- [Vérifier le certificat](#vérifier-le-certificat)
- [Installer le certificat](#installer-le-certificat)
- [Configurer OpenBao](#configurer-openbao)
- [Redémarrer le service](#redémarrer-le-service)
- [Tester le TLS](#tester-le-tls)
- [Captures](#captures)

## Choisir le nom d’hôte

On commence par choisir le nom DNS de la VM OpenBao.

Exemple :

```text
openbao.celduc.lan
```

Ce nom doit être présent dans le DNS interne, sinon le certificat TLS ne correspondra pas au serveur.

Une fois l’enregistrement A créé dans le DNS, on vérifie que le nom résout bien vers la bonne IP.

Depuis un poste client (ou la VM elle-même) :

```bash
nslookup openbao.celduc.lan
```

On doit voir l’IP de la VM OpenBao dans la réponse.

Puis on teste la connectivité :

```bash
ping openbao.celduc.lan
```

Si le ping passe, c’est que :
- le nom est bien enregistré dans le DNS,
- et qu’il pointe vers la bonne machine.

![Test DNS et ping après enregistrement A](../Images/Test_Nslookup_%26_ping_apres_enregistrement_A_in_DNS_SRV_Openbao.PNG)

## Préparer OpenSSL
On crée un fichier de configuration OpenSSL avec les SAN nécessaires.  
Les SAN doivent contenir le nom DNS de la VM, et éventuellement son IP et `127.0.0.1` pour les tests locaux.

Exemple :

```ini
[ req ]
default_bits       = 4096
prompt             = no
default_md         = sha256
distinguished_name = dn
req_extensions     = req_ext

[ dn ]
commonName = openbao.celduc.lan
organizationName = Celduc
organizationalUnitName = IT
localityName = Sorbiers
stateOrProvinceName = Auvergne-Rhône-Alpes
countryName = FR

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = openbao.celduc.lan
IP.1  = 127.0.0.1
IP.2  = 192.168.1.44
```

## Générer la clé privée
Sur le PC hôte, on génère la clé privée du serveur TLS.

```bash
openssl genrsa -out openbao.key 4096
```

Cette clé privée doit rester secrète.

## Générer la CSR
On génère ensuite la CSR à partir de cette clé privée et du fichier OpenSSL.

```bash
openssl req -new -key openbao.key -out openbao.csr -config openbao-openssl.cnf
```

La CSR sera envoyée à la PKI interne.  
La clé privée, elle, ne doit jamais être transmise.

![CSR envoyée à la PKI interne](../Images/csr_aupres_PKI_interne.png)

## Faire signer la CSR
On envoie uniquement `openbao.csr` à la PKI interne.  
La PKI renvoie ensuite un certificat signé, par exemple :
- `openbao.crt`
- ou `openbao.cer`

![Certificat délivré par la PKI interne](../Images/certif_delivre_par_pki_interne.png)

## Vérifier le certificat
Avant de l’installer, il est important de vérifier le contenu du certificat.

```bash
openssl x509 -in openbao.crt -text -noout
```

Si la PKI fournit un fichier `.cer` au format DER, on peut le vérifier avec :

```bash
openssl x509 -inform der -in openbao.cer -text -noout
```

![Vérification du certificat](../Images/Check_certificat.png)

## Installer le certificat
Sur la VM OpenBao, on crée le dossier TLS puis on copie le certificat et la clé privée.

```bash
sudo mkdir -p /etc/openbao/tls
sudo cp openbao.crt /etc/openbao/tls/openbao.crt
sudo cp openbao.key /etc/openbao/tls/openbao.key
sudo chown root:openbao /etc/openbao/tls/openbao.key
sudo chmod 640 /etc/openbao/tls/openbao.key
```

Le certificat public peut être plus permissif, mais la clé privée doit être protégée.

## Configurer OpenBao
Dans `/etc/openbao/openbao.hcl`, on configure le listener TLS :

```hcl
ui = true

storage "file" {
  path = "/opt/openbao/data"
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/etc/openbao/tls/openbao.crt"
  tls_key_file  = "/etc/openbao/tls/openbao.key"
}

api_addr = "[https://openbao.celduc.lan:8200](https://openbao.celduc.lan:8200)"
```

Si on veut tester aussi avec `127.0.0.1`, il faut que cette adresse figure dans les SAN.

## Redémarrer le service
Après modification de la configuration, on redémarre OpenBao.

```bash
sudo systemctl restart openbao.service
sudo systemctl status openbao.service -l --no-pager
```

## Tester le TLS
Depuis la VM, on définit l’adresse du serveur et la CA à utiliser :

```bash
export BAO_ADDR=[https://openbao.celduc.lan:8200](https://openbao.celduc.lan:8200)
export BAO_CACERT=/etc/openbao/tls/ca.pem
bao status
```

Ou en local :

```bash
export BAO_ADDR=[https://127.0.0.1:8200](https://127.0.0.1:8200)
export BAO_CACERT=/etc/openbao/tls/ca.pem
bao status
```

Si tout est bon, `bao status` doit répondre sans erreur TLS.


