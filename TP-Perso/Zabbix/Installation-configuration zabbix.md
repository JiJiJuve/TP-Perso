# Installation et configuration de Zabbix 7 sur Debian 

Cette fiche explique comment installer Zabbix 7 sur Debian avec Apache, PHP‑FPM et MariaDB, en s’appuyant sur la procédure officielle Zabbix pour Debian. 

https://www.zabbix.com/download

Je présente deux situations possibles :

- **Cas 1** : serveur “neuf” (Apache + PHP + MariaDB pas encore installés).  
- **Cas 2** : serveur où **GLPI** tourne déjà (donc Apache + PHP‑FPM + MariaDB déjà OK).

Tu choisis le cas qui correspond à ton labo et tu suis uniquement les étapes de ce cas.

***

## Cas 1 – Zabbix sur serveur “neuf”

### 1. Prérequis

- Debian installée.  
- Accès root ou sudo.

### 2. Mettre le système à jour

```bash
apt update && apt upgrade -y
```

### 3. Installer Apache, MariaDB et PHP‑FPM

```bash
apt install apache2 mariadb-server php8.4-fpm \
  php8.4-mysql php8.4-xml php8.4-gd php8.4-cli \
  php8.4-curl php8.4-ldap php8.4-intl php8.4-zip \
  php8.4-bz2 php8.4-mbstring unzip
```

### 4. Activer PHP‑FPM dans Apache

```bash
a2enmod proxy_fcgi setenvif
a2enconf php8.4-fpm
systemctl restart php8.4-fpm
```

Ensuite, passe **directement** à la section commune “Installation Zabbix (paquets + BDD + interface web)” plus bas.

***

## Cas 2 – Zabbix sur serveur où GLPI existe déjà

Ici, on suppose que :  
- Apache2 est déjà installé.  
- PHP‑FPM est déjà configuré (GLPI tourne).  
- MariaDB est déjà installé.

Dans ce cas, on **ne refait pas** l’install Apache/PHP/MariaDB, on passe directement à l’installation de Zabbix.

Ensuite, tu suis la même section commune “Installation Zabbix (paquets + BDD + interface web)”.

***

## Section commune – Installation Zabbix (paquets + BDD + interface web)

Ces étapes sont **les mêmes** pour les deux cas ci‑dessus. 

### 1. Installer les paquets Zabbix

#### 1.1. Ajouter le dépôt Zabbix

```bash
cd /tmp
wget https://repo.zabbix.com/zabbix/7.0/debian/pool/main/z/zabbix-release/zabbix-release_7.0-2+debian13_all.deb
dpkg -i zabbix-release_7.0-2+debian13_all.deb
apt update
```

#### 1.2. Installer serveur + frontend + agent

```bash
apt install zabbix-server-mysql zabbix-frontend-php zabbix-sql-scripts zabbix-apache-conf zabbix-agent
```

- `zabbix-server-mysql` : service Zabbix. 
- `zabbix-frontend-php` : interface web Zabbix. 
- `zabbix-sql-scripts` : scripts SQL.
- `zabbix-apache-conf` : conf Apache de base (Alias `/zabbix`). 
- `zabbix-agent` : agent (optionnel mais utile).

***

### 2. Base de données MariaDB pour Zabbix

Se connecter à MariaDB :

```bash
mysql
```

Créer la base et l’utilisateur :

```sql
CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
CREATE USER 'zabbix'@'localhost' IDENTIFIED BY 'MotDePasseZabbix!';
GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Importer le schéma Zabbix :

```bash
zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql -uzabbix -p zabbix
```

Configurer `/etc/zabbix/zabbix_server.conf` :

```ini
DBName=zabbix
DBUser=zabbix
DBPassword=MotDePasseZabbix!
```

Activer le service :

```bash
systemctl enable zabbix-server
systemctl start zabbix-server
```

***

### 3. Vérifier / ajuster la conf PHP‑FPM pour Zabbix

Zabbix a besoin de certains paramètres PHP minimum, sinon l’interface web Zabbix dans le navigateur affiche des erreurs sur l’écran de vérification. [zabbix](https://www.zabbix.com/documentation/current/en/manual/installation/frontend)

Dans `/etc/php/8.4/fpm/php.ini`, vérifier au moins :

```ini
memory_limit = 256M
post_max_size = 16M
upload_max_filesize = 2M
max_execution_time = 300
max_input_time = 300
date.timezone = Europe/Paris
```

Puis :

```bash
systemctl restart php8.4-fpm
```

- Si tu veux isoler Zabbix de GLPI, tu peux mettre ces valeurs uniquement dans la conf Apache de Zabbix (`php_value` dans le vhost ou `/etc/zabbix/apache.conf`).


- C’est typiquement ici que tu avais eu des soucis : valeurs trop basses → interface web Zabbix qui se plaint.

***

### 4. Config Apache pour le frontend Zabbix

Deux options, à toi de choisir.

#### Option 1 – Utiliser l’Alias `/zabbix` (simple)

La conf fournie par `zabbix-apache-conf` crée souvent un Alias `/zabbix`. 

Dans ce cas, l’interface web Zabbix dans le navigateur sera accessible à l’adresse :

```text
http://IP/zabbix
```

#### Option 2 – Vhost dédié sur port 81 (comme ton TP GLPI + Zabbix)

Si tu veux Zabbix séparé sur le port 81 (GLPI sur 80, Zabbix sur 81) :

1. Vérifier que le port 81 est écouté dans `/etc/apache2/ports.conf` :

```apache
Listen 80
Listen 81
```

2. Créer `/etc/apache2/sites-available/zabbix.conf` :

```apache
<VirtualHost *:81>
    ServerName zabbix_tp

    DocumentRoot /usr/share/zabbix/ui

    <Directory "/usr/share/zabbix/ui">
        Options FollowSymLinks
        AllowOverride All
        Require all granted

        php_value max_execution_time 300
        php_value memory_limit 256M
        php_value post_max_size 16M
        php_value upload_max_filesize 2M
        php_value max_input_time 300
        php_value max_input_vars 10000
        php_value date.timezone "Europe/Paris"
    </Directory>

    <Directory "/usr/share/zabbix/conf">
        Require all denied
    </Directory>

    <Directory "/usr/share/zabbix/app">
        Require all denied
    </Directory>

    <Directory "/usr/share/zabbix/include">
        Require all denied
    </Directory>

    <Directory "/usr/share/zabbix/local">
        Require all denied
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/zabbix_error.log
    CustomLog ${APACHE_LOG_DIR}/zabbix_access.log combined

    <FilesMatch \.php$>
        SetHandler "proxy:unix:/run/php/php8.4-fpm.sock|fcgi://localhost/"
    </FilesMatch>
</VirtualHost>
```

3. Activer le vhost :

```bash
a2ensite zabbix.conf
systemctl reload apache2
```

L’interface web Zabbix dans le navigateur sera alors accessible à l’adresse :

```text
http://IP:81
```

***

### 5. Interface web Zabbix dans le navigateur (fin de l’installation)

Dans le navigateur, aller sur :

- `http://IP/zabbix` (option Alias),  
ou  
- `http://IP:81` (option vhost).

Sur la page de vérification :

- Zabbix affiche une page qui contrôle les prérequis PHP (tout doit être **vert** ou OK).
- Si ce n’est pas le cas, revenir à la section 3 pour corriger la conf PHP.

Sur les écrans suivants de l’interface web Zabbix dans le navigateur :

- Indiquer les paramètres de base de données :
  - Database name : `zabbix`  
  - User : `zabbix`  
  - Password : `MotDePasseZabbix!`  
- Laisser les autres paramètres par défaut si tu ne sais pas.

Une fois l’installation terminée, tu peux te connecter à l’interface web Zabbix dans le navigateur avec :

- Utilisateur : `Admin`  
- Mot de passe : `zabbix` (par défaut). 
***

Avec cette fiche, tu as tout au même endroit pour :  
- partir d’un serveur vierge,  
- ou ajouter Zabbix sur un serveur où GLPI existe déjà,  
et dans les deux cas, finir proprement dans l’interface web Zabbix dans ton navigateur.
