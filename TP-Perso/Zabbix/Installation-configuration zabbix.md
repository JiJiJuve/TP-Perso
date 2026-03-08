## 2. Installation Zabbix (serveur + frontend)

### 2.1. Paquets Zabbix

Suivre la procédure officielle pour Debian/Ubuntu (dépôt + paquets serveur + frontend Apache). [libra-linux](https://www.libra-linux.com/blog/15-supervision-avec-zabbix-7-0-lts-sur-debian-ubuntu)
Exemple Debian 12 :

```bash
# 1) Ajouter le dépôt Zabbix (commande copiée depuis zabbix.com/download)
wget https://repo.zabbix.com/zabbix/7.0/debian/pool/main/z/zabbix-release/zabbix-release_7.0-2+debian12_all.deb
sudo dpkg -i zabbix-release_7.0-2+debian12_all.deb
sudo apt update

# 2) Installer serveur + frontend + agent + scripts SQL
sudo apt install zabbix-server-mysql zabbix-frontend-php zabbix-sql-scripts zabbix-apache-conf zabbix-agent
```

Les paquets `zabbix-frontend-php` et `zabbix-apache-conf` installent notamment une conf Apache type `/etc/zabbix/apache.conf` avec Alias `/zabbix` et les `php_value` recommandés. [zabbix](https://www.zabbix.com/forum/zabbix-troubleshooting-and-problems/374281-apache-config-file-not-working)

***

## 3. Base de données MariaDB pour Zabbix

```bash
sudo mysql

CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
CREATE USER 'zabbix'@'localhost' IDENTIFIED BY 'MotDePasseZabbix!';
GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Importer le schéma fourni par les paquets : [libra-linux](https://www.libra-linux.com/blog/15-supervision-avec-zabbix-7-0-lts-sur-debian-ubuntu)

```bash
zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql -uzabbix -p zabbix
```

Configurer `/etc/zabbix/zabbix_server.conf` :

```ini
DBName=zabbix
DBUser=zabbix
DBPassword=MotDePasseZabbix!
```

Puis activer le serveur :

```bash
sudo systemctl enable zabbix-server
sudo systemctl start zabbix-server
```

***

## 4. PHP‑FPM côté Zabbix

Tu as déjà PHP‑FPM fonctionnel grâce à GLPI.  
On s’assure juste que les **valeurs minimales requises par Zabbix** sont OK, soit : [zabbix](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)

- `max_execution_time` ≥ 300  
- `memory_limit` ≥ 128M (tu peux mettre 256M)  
- `post_max_size` ≥ 16M  
- `upload_max_filesize` ≥ 2M  
- `max_input_time` ≥ 300  
- `max_input_vars` ≥ 10000  
- `date.timezone` défini (Europe/Paris)

Tu peux soit :

- les définir **globalement** dans `/etc/php/8.4/fpm/php.ini`,  
- soit laisser global “raisonnable” (ce que tu as déjà pour GLPI) et mettre des `php_value` spécifiques Zabbix dans le vhost / `apache.conf` (plus propre). [support.zabbix](https://support.zabbix.com/secure/attachment/84738/zabbix-php-fpm.conf)

Dans tous les cas, après modif du `php.ini` FPM :

```bash
sudo systemctl restart php8.4-fpm
```

***

## 5. Vhost Apache dédié à Zabbix

Au lieu de l’Alias `/zabbix` global, on met Zabbix dans un **vhost séparé**, comme GLPI. [geekistheway](https://geekistheway.com/2022/12/30/hardening-zabbix-server-installation-using-apache-virtualhosts-and-lets-encrypt-certificates/)

### 5.1. Contenu du vhost

Créer `/etc/apache2/sites-available/zabbix.conf` :

```apache
<VirtualHost *:80>
    ServerName zabbix.lab.local

    DocumentRoot /usr/share/zabbix

    # Répertoires Zabbix
    <Directory "/usr/share/zabbix">
        Options FollowSymLinks
        AllowOverride None
        Require all granted

        # Spécifiques PHP pour Zabbix
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

    # PHP-FPM (même pool que GLPI)
    <FilesMatch \.php$>
        SetHandler "proxy:unix:/run/php/php8.4-fpm.sock|fcgi://localhost/"
    </FilesMatch>
</VirtualHost>
```

Les blocs `<Directory>` et `php_value` reprennent la logique des exemples Zabbix officiels : Alias ou vhost, avec les bons paramètres PHP pour que l’install frontend ne se plaigne pas. [zabbix](https://www.zabbix.com/forum/zabbix-help/40211-what-does-zabbix-do-when-the-php-max_execution_time-is-exceeded)

### 5.2. Activation du vhost

```bash
sudo a2ensite zabbix.conf
sudo systemctl reload apache2
```

Assure-toi aussi que la conf globale `/etc/zabbix/apache.conf` ne crée pas de conflit (par exemple, si elle définit déjà un Alias `/zabbix`, tu peux soit la laisser, soit la désactiver si tu utilises uniquement le vhost). [zabbix](https://www.zabbix.com/forum/zabbix-troubleshooting-and-problems/374281-apache-config-file-not-working)

***

## 6. Fin d’installation côté web

Depuis ton poste client (ou la VM), ouvre :

```text
http://zabbix.lab.local
```

- L’installeur Zabbix vérifie les paramètres PHP (tu dois passer toutes les lignes en vert grâce aux `php_value`). [zabbix](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- Renseigne :
  - DB : `zabbix`  
  - user : `zabbix`  
  - mot de passe : `MotDePasseZabbix!`  
- Termine le wizard.

Identifiants par défaut : `Admin` / `zabbix`. [youtube](https://www.youtube.com/watch?v=CwgpE2ZBhbw)


