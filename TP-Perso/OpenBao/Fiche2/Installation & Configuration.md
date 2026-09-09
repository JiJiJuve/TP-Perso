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
CN = openbao.celduc.lan
O  = Celduc
OU = IT
L  = Sorbiers
S  = Auvergne-Rhône-Alpes
C  = FR

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

## Faire signer la CSR
On envoie uniquement `openbao.csr` à la PKI interne.  
La PKI renvoie ensuite un certificat signé, par exemple :
- `openbao.crt`
- ou `openbao.cer`

## Vérifier le certificat
Avant de l’installer, il est important de vérifier le contenu du certificat.

```bash
openssl x509 -in openbao.crt -text -noout
```

Si la PKI fournit un fichier `.cer` au format DER, on peut le vérifier avec :

```bash
openssl x509 -inform der -in openbao.cer -text -noout
```

On doit retrouver dans le certificat le DNS attendu, et si besoin l’IP de la VM.

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

## Captures
![Extrait du fichier de configuration OpenSSL](Images/Extrait_fichier_conf_openssl.png)

![Récupération de la dernière version OpenBao via GitHub](Images/Interrogation_API_github_recuperer_derniere_version_openbao.png)

![Organisation du dossier TLS](Images/Check_Organisation_dossier_TLS.png)

![Ouverture du fichier de configuration OpenBao](Images/acceder_fichier_conf_openbao_hcl.png)

![Configuration de `tls_cert_file` et `tls_key_file`](Images/extrait_fichier_conf_openbao_hcl_avec_modif_tls_cert_file_%26_tsl_key_file.png)

![CSR envoyée à la PKI interne](Images/csr_aupres_PKI_interne.PNG)

![Certificat délivré par la PKI interne](Images/certif_delivre_par_pki_interne.PNG)

![Conversion du fichier CER en CRT](Images/Convertion_fichier_cer_en_crt.png)

![Conversion du certificat CA en PEM](Images/Convertion_certif_cA_en_pem.png)

![Vérification du certificat](Images/Check_certificat.png)

![Vérification du fichier PEM](Images/Check_fichier_pem.png)

![Copie du certificat CA sur la VM](Images/Copie_certif_CA_racine_in_srv_openbao_avec_scp_depuis_pc_hote.png)

![Déplacement des fichiers TLS et droits appliqués](Images/Deplace_fichiers_depuis_tmp_vers_tls_srv_openbao_%26_conf_droits_fichiers_key_cert.png)

![Copie du certificat CA dans `ca.crt` et droits `644`](Images/copie_certif_ca_in_tls_ca_crt_%26_droit_chmod_644.png)

![Test en échec avec mauvais format de certificat CA](Images/Test_KO_mauvais_format_certif_cA.png)

![Vérification du nouveau format PEM](Images/Verification_new_format_certif_CA_pem_OK.png)

![Test DNS et ping après enregistrement](Images/Test_Nslookup_%26_ping_apres_enregistrement_A_in_DNS_SRV_Openbao.PNG)

![Test d’accès au serveur OpenBao et état du coffre](Images/Test_acces_srv_openbao_%26_etat_coffre_Sealed_OK.png)

![Ouverture du coffre avec 3 clés](Images/Ouverture_coffre_avec_3keys.png)

![Déverrouillage réussi avec 3 clés](Images/Unseal_3_key_deverouillages_OK.png)
