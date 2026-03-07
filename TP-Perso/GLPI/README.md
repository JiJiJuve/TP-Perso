# TP – Installation de GLPI 11 sur Debian

## 0. Vérification de l’intégrité des ISO (hash)

Objectif : vérifier l’authenticité des ISO utilisées (Debian, Windows Server) avant installation.

Vérification de l’ISO Debian :

![Vérification du hash ISO Debian](images/verif_hash_iso_debian_13-1-0.png)  
![Hash attendu ISO Debian](images/hash_iso_debian_13-1-0.png)  

Vérification de l’ISO Windows Server :

![Vérification du hash ISO Windows Server](images/verif_hash_iso_WindServer25.png)  
![Hash attendu ISO Windows Server](images/hash_iso_26100.32230.260111-0550.lt_release_svc_refresh_SERVER_EVAL_x64FRE_fr-fr.iso.png)  

---

## 1. Préparation : utilisateur sudo et SSH

Objectif : ne pas travailler en root et pouvoir administrer la VM à distance.

Installer sudo (si nécessaire) :

```bash
su -
apt install sudo -y
```

Ajouter ton utilisateur au groupe sudo :

```bash
usermod -aG sudo tonuser
```

Installer et activer le serveur SSH :

```bash
apt update
apt install openssh-server -y
systemctl enable ssh
systemctl start ssh
```

Vérifier depuis ton user :

```bash
su - tonuser
sudo whoami   # doit retourner : root
```

![Donner les droits sudo et installer OpenSSH](images/donne_droit_user_installation_oppenssh.png)  
![Connexion SSH depuis le PC hôte](images/connexion_ssh_depuis_pc_hote.png)  
![Vérification de SSH](images/verif_ssh.png)  

---

## 2. Installation des paquets nécessaires (LAMP + PHP-FPM)

Objectif : installer le serveur web Apache, la base MariaDB, PHP, PHP‑FPM et les extensions utiles à GLPI.

Mettre à jour le système :

```bash
sudo apt update && sudo apt upgrade -y
```

![Mise à jour du serveur Debian](images/maj_server_debian.png)  

Installer Apache, MariaDB et PHP de base :

```bash
sudo apt install apache2 mariadb-server php -y
```

![Installation du LAMP](images/installation_LAMP.png)  

Installer PHP‑FPM :

```bash
sudo apt install php-fpm -y
```

Installer les extensions PHP pour GLPI :

```bash
sudo apt install php-{mysql,mbstring,curl,gd,xml,intl,ldap,apcu,xmlrpc,zip,bz2,bcmath} -y
```

![Installation des dépendances PHP](images/installation_dependances_php.png)  
![Installation de la gestion des processus PHP (PHP-FPM)](images/installation_gestio_processus_php.png)  

---

## 3. Préparation de la base de données

Objectif : créer une base dédiée à GLPI + un utilisateur SQL avec les droits dessus.

Se connecter à MariaDB :

```bash
sudo mariadb
```

Créer la base de données :

```sql
create database glpi_npt;
```

Créer un utilisateur SQL et lui donner tous les privilèges sur cette base :

```sql
grant all privileges on glpi_npt.* to neptunet_glpi@localhost identified by "votr3-MDP";
```

Quitter MariaDB :

```sql
exit;
```

![Création de la base et de l’utilisateur MariaDB](images/creation_base_donnée_mariadb_utilisateur_motpass.png)  

---

## 4. Téléchargement et installation de GLPI

Objectif : télécharger l’archive GLPI, la décompresser dans `/var/www/html` et mettre les bons droits.

### 4.1. Téléchargement de l’archive

```bash
cd /tmp
wget https://fossies.org/linux/misc/glpi-11.0.5.tgz
```

![Téléchargement de la dernière version de GLPI](images/dowload_last_version_glpi.png)  

### 4.2. Extraction dans la racine web

```bash
sudo tar -xvzf glpi-11.0.5.tgz -C /var/www/html
```

![Décompression de l’archive GLPI](images/decompression_archive_glpi.png)  

### 4.3. Droits sur les fichiers

```bash
sudo chown -R www-data:www-data /var/www/html/glpi
```

![www-data propriétaire des fichiers GLPI](images/utilisateur_services_web_proprietaire_new_files.png)  

---

## 5. Configuration d’Apache et de PHP‑FPM

Objectif : créer un VirtualHost propre pour GLPI, lier Apache à PHP‑FPM, et activer les bons modules.

### 5.1. Vérifier la version PHP

```bash
php -v
```

![Vérification de la version de PHP](images/verif_version_php.png)  

### 5.2. Créer le fichier VirtualHost pour GLPI

```bash
sudo nano /etc/apache2/sites-available/glpi.conf
```

Contenu :

```apache
<VirtualHost *:80>
    ServerName glpi_tp
    ServerAlias 192.168.1.47
    DocumentRoot /var/www/html/glpi/public

    <Directory /var/www/html/glpi/public>
        Options -Indexes +FollowSymLinks
        Require all granted
        RewriteEngine On
        RewriteBase /
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule ^ index.php [QSA,L]
    </Directory>

    <FilesMatch \.php$>
        SetHandler "proxy:unix:/run/php/php8.4-fpm.sock|fcgi://localhost"
    </FilesMatch>

    ErrorLog ${APACHE_LOG_DIR}/glpi_error.log
    CustomLog ${APACHE_LOG_DIR}/glpi_access.log combined
</VirtualHost>
```

![Création du VirtualHost GLPI](images/creation_fichier_virtualhost_glpi.png)  
![VirtualHost GLPI dans Apache](images/virtualhost_glpi.png)  

### 5.3. Activer les modules et la conf

```bash
sudo a2enmod proxy_fcgi setenvif
sudo a2enmod rewrite
sudo a2enconf php8.4-fpm   # adapter la version de PHP si besoin
sudo a2dissite 000-default.conf
sudo a2ensite glpi.conf
sudo apachectl configtest
sudo systemctl restart apache2
```

![Activation des modules PHP pour Apache](images/activation_modules_php_apache.png)  

---

## 6. Installation de GLPI via l’interface web

Objectif : finaliser l’installation avec le navigateur (tests prérequis, connexion DB, création des tables).

Accéder à GLPI depuis un navigateur sur le même réseau :

- `http://192.168.1.47/`  
- ou `http://glpi_tp/` si le nom a été ajouté dans le fichier hosts.

![Accès à l’installation GLPI (1)](images/acces_installation_glpi_GUI.png)  
![Accès à l’installation GLPI (2)](images/acces_installation_glpi_GUI2.png)  
![Accès à l’installation GLPI (3)](images/acces_installation_glpi_GUI3.png)  
![Accès à l’installation GLPI (4)](images/acces_installation_glpi_GUI4.png)  
![Accès à l’installation GLPI (5)](images/acces_installation_glpi_GUI5.png)  
![Accès à l’installation GLPI (6)](images/acces_installation_glpi_GUI6.png)  
![Accès à l’installation GLPI (7)](images/acces_installation_glpi_GUI7.png)  

Une fois l’installation terminée, se connecter avec :

- Utilisateur : `glpi`  
- Mot de passe : `glpi`

![Connexion par défaut glpi/glpi](images/connexion_defaut_glpi_glpi.png)  
![Tableau de bord de GLPI](images/tableau_bord_glpi.png)  

