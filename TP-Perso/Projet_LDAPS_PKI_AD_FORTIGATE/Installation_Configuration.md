# Projet LDAPS : PKI, Active Directory et FortiGate

## Sommaire
- [Contexte et objectif](#contexte-et-objectif)
- [Préparation de l’environnement](#préparation-de-lenvironnement)
- [Durcissement LDAP sur Active Directory](#durcissement-ldap-sur-active-directory)
- [Mise en place de la PKI / AD CS](#mise-en-place-de-la-pki--ad-cs)
- [Création et émission des certificats](#création-et-émission-des-certificats)
- [Vérification des certificats](#vérification-des-certificats)
- [Configuration LDAPS sur le DC](#configuration-ldaps-sur-le-dc)
- [Configuration FortiGate](#configuration-fortigate)
- [Tests de connexion](#tests-de-connexion)
- [Journalisation et validation](#journalisation-et-validation)
- [Conclusion](#conclusion)

***

## Contexte et objectif

Ce projet s’inscrit dans la continuité d’un audit de sécurité réalisé sur l’environnement Active Directory à l’aide d’outils comme ADMiner, BloodHound et SharpHound. L’analyse a permis d’identifier plusieurs faiblesses, notamment autour de la gestion des comptes administrateurs locaux et de la sécurisation des authentifications LDAP.

En complément de la remédiation initiale sur les comptes administrateurs locaux, qui a conduit à la mise en place de GPO et de LAPS côté Active Directory, un mécanisme qui génère et stocke automatiquement un mot de passe administrateur local unique pour chaque poste dans l’annuaire, le projet s’est ensuite concentré sur la sécurisation des authentifications LDAP via LDAP signing, une PKI interne et LDAPS.

Dans la continuité, le projet s’est orienté vers la sécurisation des échanges entre le FortiGate et l’Active Directory, avec la mise en place de l’infrastructure PKI puis la configuration de LDAPS pour chiffrer les communications avec le contrôleur de domaine.

***

## Préparation de l’environnement

Avant de commencer, une machine Windows Server a été préparée et reliée au domaine afin de servir de base au déploiement AD / PKI.

***

## Durcissement LDAP sur Active Directory

La première étape de sécurisation a consisté à activer **LDAP signing** sur le contrôleur de domaine.  
Cette configuration permet d’imposer une signature des requêtes LDAP et de réduire les risques liés aux authentifications non sécurisées.



La journalisation LDAP a également été activée afin d’identifier les clients utilisant des binds non sécurisés.





***

## Mise en place de la PKI / AD CS

Pour permettre le fonctionnement de LDAPS, une infrastructure de certificats a été mise en place via le rôle **Active Directory Certificate Services**.



La CA racine du projet a ensuite été configurée.



***

## Création et émission des certificats

Une demande de certificat serveur a été préparée pour le service LDAPS du contrôleur de domaine.



Le fichier de demande a ensuite été généré.



La demande a été délivrée manuellement par l’autorité de certification.



Le certificat serveur émis par la CA a ensuite été récupéré.



Le certificat serveur du DC a aussi été exporté, ainsi que le certificat racine public.





***

## Vérification des certificats

Avant de poursuivre, plusieurs vérifications ont été faites pour confirmer que les certificats étaient valides et correctement émis.









Les imports ont également été contrôlés dans l’interface.





Une erreur liée à un certificat auto-signé a été observée avant la correction de la chaîne de confiance.



***

## Configuration LDAPS sur le DC

Les fichiers de certificat utilisés pour LDAPS ont été conservés et validés pour le contrôleur de domaine.





Une fois la CA importée et le certificat serveur installé, le contrôleur de domaine a pu exposer le service LDAP en mode sécurisé.

***

## Configuration FortiGate

Le FortiGate a ensuite été préparé pour faire confiance à la CA interne et utiliser le serveur LDAPS du domaine.



La configuration DNS a été adaptée pour permettre la résolution du contrôleur de domaine interne.



Un utilisateur / groupe a également été créé pour l’intégration à l’authentification VPN SSL.



***

## Tests de connexion

Plusieurs tests ont été effectués pour valider le bon fonctionnement de LDAPS.

### Test avec LDP.exe
La connexion LDAPS a d’abord été testée avec l’outil LDP.





### Test depuis FortiGate
Le test LDAP/LDAPS depuis FortiGate a confirmé le bon fonctionnement de la configuration.







### Test VPN FortiClient
Un test de connexion VPN SSL avec FortiClient a également été réalisé.



***

## Journalisation et validation

Les journaux du contrôleur de domaine ont permis de confirmer que les connexions LDAPS étaient bien prises en compte et que le fonctionnement était conforme à ce qui était attendu.



***

## Conclusion

Ce projet a permis de sécuriser l’authentification entre Active Directory et le FortiGate grâce à une combinaison de **LDAP signing**, de **PKI interne** et de **LDAPS**.

Il a également permis de valider la chaîne complète de confiance, depuis la création de la CA jusqu’aux tests fonctionnels sur le VPN SSL.

***

Si tu veux, je peux maintenant te faire une **version encore plus propre et plus “README GitHub final”**, avec un style plus fluide et plus pro, prête à copier directement.
