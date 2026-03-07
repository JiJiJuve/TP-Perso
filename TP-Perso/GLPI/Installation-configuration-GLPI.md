## 0. Préparation : utilisateur sudo et SSH

Objectif : ne pas travailler en root et pouvoir administrer la VM à distance.

1. Installer sudo (si nécessaire) :

```bash
su -
apt install sudo -y
```


- `su -` : ouvre une session en tant que root.  
- `apt install sudo -y` : installe le paquet `sudo` sans poser de questions (réponse “yes” automatique).

2. Ajouter ton utilisateur au groupe sudo :

```bash
usermod -aG sudo tonuser
```


- `-aG sudo` : ajoute ton user au groupe `sudo` (sans enlever les autres groupes).  
- Ça lui donne le droit d’exécuter des commandes avec `sudo`.

3. Installer et activer le serveur SSH :

```bash
apt update
apt install openssh-server -y
systemctl enable ssh
systemctl start ssh
```


- `openssh-server` : permet d’accepter des connexions SSH entrantes.  
- `enable` : active SSH au démarrage.  
- `start` : démarre le service immédiatement.

4. Vérifier depuis ton user :

```bash
su - tonuser
sudo whoami
# doit retourner : root
```


Tu travailleras ensuite avec `tonuser` + `sudo`.

***

## 1. Installation des paquets nécessaires (LAMP + PHP-FPM)

Objectif : installer le serveur web Apache, la base MariaDB, PHP, PHP‑FPM et les extensions utiles à GLPI. 

1. Mettre à jour le système :

```bash
sudo apt update && sudo apt upgrade -y
```


- `update` : récupère la liste à jour des paquets.  
- `upgrade` : installe les dernières versions des paquets déjà présents.

2. Installer Apache, MariaDB et PHP de base :

```bash
sudo apt install apache2 mariadb-server php -y
```


- `apache2` : service web qui servira GLPI.  
- `mariadb-server` : base de données.  
- `php` : langage côté serveur utilisé par GLPI.

3. Installer PHP‑FPM :

```bash
sudo apt install php-fpm -y
```


- PHP‑FPM sépare l’exécution du PHP d’Apache, pour de meilleures performances et stabilité.

4. Installer les extensions PHP pour GLPI :

```bash
sudo apt install php-{mysql,mbstring,curl,gd,xml,intl,ldap,apcu,xmlrpc,zip,bz2,bcmath} -y
```


- `mysql` : connexion DB.  
- `mbstring` : gestion des chaînes multibyte.  
- `curl`, `gd`, `xml`, `intl`, `ldap`… : fonctionnalités avancées de GLPI (API, images, XML, internationalisation, LDAP, cache, etc.).  

***

## 2. Préparation de la base de données

Objectif : créer une base dédiée à GLPI + un utilisateur SQL avec les droits dessus.

1. Se connecter à MariaDB :

```bash
sudo mariadb
```


2. Créer la base de données (nom au choix) :

```sql
create database glpi_npt;
```


- Ici, la base s’appelle `glpi_npt`.  
- Note ce nom, tu en auras besoin dans l’assistant web.

3. Créer un utilisateur SQL et lui donner tous les privilèges sur cette base :

```sql
grant all privileges on glpi_npt.* to neptunet_glpi@localhost identified by "votr3-MDP";
```


- `neptunet_glpi` : nom de l’utilisateur SQL (modifiable).  
- `"votr3-MDP"` : mot de passe (à choisir).  
- `@localhost` : l’utilisateur ne peut se connecter que depuis la machine locale.

4. Quitter MariaDB :

```sql
exit;
```

***

## 3. Téléchargement et installation de GLPI

Objectif : télécharger l’archive GLPI, la décompresser dans `/var/www/html` et mettre les bons droits.

### 3.1. Téléchargement de l’archive (via Fossies)

Comme l’URL GitHub te renvoie une erreur 404, on utilise le miroir Fossies.

```bash
cd /tmp
wget https://fossies.org/linux/misc/glpi-11.0.5.tgz
```


- `cd /tmp` : tu te places dans un dossier temporaire.  
- `wget ...glpi-11.0.5.tgz` : télécharge l’archive GLPI 11.0.5.

### 3.2. Extraction dans la racine web

```bash
sudo tar -xvzf glpi-11.0.5.tgz -C /var/www/html
```


- `-x` : extrait.  
- `-v` : verbeux (affiche les fichiers).  
- `-z` : indique gzip.  
- `-f` : fichier à traiter.  
- `-C /var/www/html` : extrait directement dans `/var/www/html`.  

Tu obtiens `/var/www/html/glpi`.

### 3.3. Droits sur les fichiers

```bash
sudo chown -R www-data:www-data /var/www/html/glpi
```


-  Met tout le dossier GLPI sous la propriété de www-data (user Apache).   
- GLPI pourra ainsi créer/modifier ses fichiers (config, plugins, logs).

***

## 4. Configuration d’Apache et de PHP‑FPM

Objectif : créer un VirtualHost propre pour GLPI, lier Apache à PHP‑FPM, et activer les bons modules. 

### 4.1. Vérifier la version PHP

```bash
php -v
```


- Note la version majeure (par exemple 8.4), elle apparaît dans le nom du socket `/run/php/php8.4-fpm.sock`.

### 4.2. Créer le fichier VirtualHost pour GLPI

On utilise la version **corrigée** que tu as maintenant sur ta VM : vhost dédié GLPI, DocumentRoot sur `glpi/public`. 

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


Détail :

- `ServerName glpi_tp` : nom logique du site (peut être ajouté dans le fichier `hosts` de ton poste).  
- `ServerAlias 192.168.1.47` : l’IP de ta VM ; Apache utilisera ce vhost quand tu appelles cette IP.  
- `DocumentRoot /var/www/html/glpi/public` : très important pour GLPI 11, on ne sert que le dossier `public`.


Bloc `<Directory>` :

- `Options -Indexes +FollowSymLinks` : pas d’index de répertoire, autorise les symlinks.  
- `Require all granted` : permet l’accès aux clients.  
- `RewriteEngine On` : active les réécritures d’URL.  
- `RewriteBase /` : base des URL réécrites = racine du site.  
- `RewriteCond ... !-f / !-d` : si la cible n’est pas un fichier/dossier existant…  
- `RewriteRule ^ index.php [QSA,L]` : …alors tout passe par `index.php` (GLPI route en interne).


Bloc `<FilesMatch \.php$>` :

- S’applique à tous les fichiers `.php`.  
- `SetHandler "proxy:unix:/run/php/php8.4-fpm.sock|fcgi://localhost"` :  
  - envoie les requêtes PHP au socket Unix de PHP‑FPM,  
  - utilise FastCGI pour la communication. 

Logs :

- `glpi_error.log` : erreurs spécifiques au site GLPI.  
- `glpi_access.log` : toutes les requêtes HTTP vers GLPI.


### 4.3. Activer les modules et la conf

1. Activer les modules nécessaires :

```bash
sudo a2enmod proxy_fcgi setenvif
sudo a2enmod rewrite
```


- `proxy_fcgi` : permet à Apache de discuter avec PHP‑FPM.  
- `setenvif` : gère certaines variables d’environnement.  
- `rewrite` : indispensable pour les URL dynamiques.

2. Activer la conf PHP‑FPM adaptée :

```bash
sudo a2enconf php8.4-fpm
```


- Active la configuration de PHP‑FPM (par ex. `php8.4-fpm.conf`) pour Apache.

3. Désactiver le vhost par défaut :

```bash
sudo a2dissite 000-default.conf
```


4. Activer ton vhost GLPI :

```bash
sudo a2ensite glpi.conf
```


5. Vérifier la configuration :

```bash
sudo apachectl configtest
# attendu : Syntax OK
```


6. Redémarrer Apache :

```bash
sudo systemctl restart apache2
```


À ce stade, côté serveur, GLPI est servi via `http://192.168.1.47/`.

***

## 5. Installation de GLPI via l’interface web

Objectif : finaliser l’installation avec le navigateur : tests prérequis + connexion DB + création des tables. 

1. Sur un PC du même réseau, ouvre un navigateur :

```text
http://192.168.1.47/
```

(ou `http://glpi_tp/` si tu as ajouté le nom dans ton fichier `hosts`). 

2. Sélectionner la langue (Français), valider.

3. Accepter les conditions, cliquer sur « Installer ».

4. L’assistant lance des tests :  
   - Vérifie la version PHP, les extensions, les permissions.  
   - Si tout est vert, cliquer sur « Continuer ». Sinon, corriger (paquets ou droits) puis relancer. 

5. Renseigner la base de données :
   - Serveur SQL : `localhost`.  
   - Utilisateur SQL : `neptunet_glpi` (ou celui que tu as créé).  
   - Mot de passe : celui choisi dans `grant all privileges`.  


6. Choisir la base `glpi_npt` dans la liste.

7. Laisser GLPI initialiser la base, puis continuer.

8. Eventuellement : accepter / refuser l’envoi de stats anonymes à l’équipe GLPI.

9. Un écran de fin affiche les comptes par défaut (à noter) :

- `glpi / glpi` : super admin.  
- `tech / tech`, `normal / normal`, `post-only / postonly`. 

10. Cliquer sur « Utiliser GLPI » et se connecter avec `glpi / glpi`.

***

## 6. Post-installation : sécurisation rapide

Objectif : sécuriser un minimum ton instance.

1. Changer les mots de passe des 4 comptes par défaut :  
   - Menu « Administration » → « Utilisateurs ».  
   - Modifier chaque compte, cliquer sur « Modifier le mot de passe », enregistrer.
  

2. Supprimer le répertoire d’installation :

```bash
sudo rm -rf /var/www/html/glpi/install
```


3. Désactiver les données de démonstration si tu ne veux pas travailler avec.

***

## 7. Bonus : inventorier le serveur GLPI lui‑même

Objectif : faire remonter la VM GLPI dans GLPI via l’agent. 

1. Dans GLPI :  
   Administration → Inventaire → cocher « Activer l’inventaire » → Sauvegarder.

2. Sur la VM :

```bash
cd /tmp
wget https://github.com/glpi-project/glpi-agent/releases/download/1.15/glpi-agent-1.15-linux-installer.pl
sudo perl glpi-agent-1.15-linux-installer.pl
```


- Lors de l’install, mettre l’URL de GLPI : `http://192.168.1.47/` (ou `/glpi` si tu gardes un sous-dossier).

3. Lancer un inventaire immédiat :

```bash
sudo glpi-agent
```


4. Vérifier dans GLPI : Parc → Ordinateurs : ta VM doit apparaître.

***

Si tu veux, message suivant je peux te faire une version “ultra courte” (suite de commandes + 1 phrase max de description) pour t’en servir comme antisèche en TP.
