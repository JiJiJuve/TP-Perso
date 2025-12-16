# TP Réseau – Siège, Succursale et Site Home

## Sommaire

- [Présentation générale](#présentation-générale)
- [Objectifs pédagogiques](#objectifs-pédagogiques)
- [Topologie et adressage (résumé)](#topologie-et-adressage-résumé)
- [Contenu du dépôt](#contenu-du-dépôt)
- [Infrastructure LAN du siège](#2-infrastructure-lan-du-siège-social)
  - [VTP](#vtp-vlan-trunking-protocol)
  - [VLAN](#vlan-virtual-local-area-network)
  - [Ports access et trunks](#configuration-des-interfaces-en-mode-access-ou-trunk)
  - [EtherChannel](#etherchannel-entre-switches-l2-et-l3-agrégation-de-liens)
  - [STP](#spanning-tree-protocol-stp)
  - [Routage inter-VLAN](#routage-inter-vlan)
  - [HSRP / FHRP](#fhrp-first-hop-redundancy-protocolpasserelle-par-défaut-redondante)
  - [DHCP et ip helper-address](#serveur-dhcp-central-et-ip-helper-address)
  - [Téléphonie IP / TFTP / CME](#téléphonie-ip-et-rôle-du-serveur-tftp)
  - [OSPF au siège](#routage-ospf-open-shortest-path-first)
  - [NAT/PAT](#natnetwork-address-translation-et-patport-address-translation-pour-laccès-internet)
- [WAN, succursale et VPN](#à-compléter-plus-tard)


---

## Présentation générale

Ce dépôt contient un projet complet réalisé sous Cisco Packet Tracer :

- Un site **siège** avec plusieurs VLAN, routage inter-VLAN, HSRP et OSPF.
- Une **succursale** avec serveur web publié sur Internet via NAT.
- Un site **Home** pour un utilisateur distant.
- Un **routeur ISP** qui interconnecte les sites.
- De la **téléphonie IP** avec Cisco CME (CallManager Express).
- Un **VPN IPsec site-à-site** entre le siège (192.168.0.0/16) et le site Home (172.16.60.0/24). 

## Objectifs pédagogiques

Ce TP a pour but de :

- Concevoir et configurer un réseau multi-sites (siège, succursale, home) avec séparation en VLAN.
- Mettre en œuvre le routage inter-VLAN, OSPF, HSRP et le DHCP relay au siège.
- Configurer le NAT/PAT et la publication d’un serveur web sur la succursale.
- Déployer une solution de téléphonie IP de base avec Cisco CME.
- Sécuriser les échanges entre le site Home et le siège via un VPN IPsec site-à-site avec exemption de NAT. 

## Topologie et adressage (résumé)

- **Siège (R1 + switches L3)**  
  - VLAN utilisateurs : 192.168.10.0/24, 192.168.20.0/24, 192.168.30.0/24, 192.168.40.0/24, etc.  
  - Routage inter-VLAN + HSRP sur les switches L3.  
  - Lien WAN vers ISP : 200.0.0.1/30. 

- **Succursale (RSuccursale)**  
  - LAN succursale : 172.16.10.0/24.  
  - PAT vers Internet et publication d’un serveur web interne.  
  - Lien WAN vers ISP : 200.0.0.10/30.

- **Site Home (RHOME)**  
  - LAN Home : 172.16.60.0/24 (utilisateur distant).  
  - PAT vers Internet et VPN IPsec vers le siège.  
  - Lien WAN vers ISP : 200.0.0.14/30.

- **ISP**  
  - Relie les liens WAN 200.0.0.x des trois routeurs.  
  - Contient des routes statiques vers tous les LAN internes (siège, succursale, home).

> Les détails complets d’adressage et de configuration sont décrits dans les fichiers du dossier `docs/`.

## Contenu du dépôt

- `docs/` : documentation détaillée (config expliquée, commandes de vérification).
- `packet-tracer/` : fichiers `.pkt` pour ouvrir la topologie dans Packet Tracer.
- `notes/` : pense-bêtes de commandes et raccourcis CLI.
- 
## Documentation détaillée

La documentation est découpée en plusieurs parties :

# 01 – Infrastructure LAN du siège : VLAN, VTP, trunks, EtherChannel, STP, routage inter-VLAN, HSRP, DHCP, téléphonie IP, OSPF et NAT

## 1. Objectif de cette partie

L’objectif est de mettre en place l’infrastructure de niveau 2/3 au **siège** :

- Segmenter le LAN en plusieurs VLAN (utilisateurs, voix, serveurs, management).
- Distribuer automatiquement la base de VLAN avec **VTP**.
- Relier les switches via des **trunks** et un **EtherChannel**.
- Activer le **routage inter-VLAN** sur les switches L3.
- Assurer une **passerelle redondante** pour les clients avec **HSRP**.

---

## 2. Infrastructure LAN du siège social

### 2.1 Configuration des VLAN, VTP, trunks, EtherChannel, routage inter-VLAN, HSRP, DHCP, téléphonie IP et OSPF dans le LAN du siège social.
  
#### VTP (Vlan Trunking Protocol)
VTP permet de synchroniser la configuration des VLAN entre les switch.
    
- Mode Server sur les deux Switch Distributions/Core L3:
      
<img width="638" height="253" alt="conf_VTP_Server" src="https://github.com/user-attachments/assets/4c88c4d2-eb9d-44b9-831d-68f16990ef28" />

<BVR><BVR>

<img width="635" height="243" alt="conf_VTP_Server2" src="https://github.com/user-attachments/assets/09ec08b7-b1f9-4ee6-b2cd-28997edf8d12" />

<BVR><BVR>

- Mode Client sur les trois Switch d'accès L2 :

<img width="579" height="236" alt="conf_VTP_Client" src="https://github.com/user-attachments/assets/9deeb420-bff5-40c0-8d49-a3a0507ce893" />

<BVR><BVR>

<img width="545" height="238" alt="conf_VTP_Client2" src="https://github.com/user-attachments/assets/8da68c93-7f0d-4449-8821-320362ed013a" />

<BVR><BVR>

<img width="580" height="250" alt="conf_VTP_Client3" src="https://github.com/user-attachments/assets/72266f70-370c-4cde-a035-f9a8745e80be" />

<BVR><BVR>

```
vtp mode server
vtp domain
vtp password
vtp version 2
show vtp status
```

#### VLAN (Virtual Local Area Network)
Les VLAN permettent de segmenter les réseaux physiques en sous réseaux-logiques.

<img width="557" height="251" alt="conf_Vlan_L3" src="https://github.com/user-attachments/assets/bdb0e239-97dd-4cdb-a6ea-0d32d54edebb" />

<BVR><BVR>

<img width="561" height="277" alt="conf_Vlan_L2" src="https://github.com/user-attachments/assets/3ce136ab-14b5-42ff-89e3-6ab9f7fdd273" />

<BVR><BVR>

```
vlan 10
name
show vlan brief
```

#### Configuration des interfaces en mode ACCESS ou TRUNK
Les ports TRUNK laissent passer plusieurs VLANs grâce aux trames taggées (802.1Q), contrairement aux ports ACCESS qui n'acceptent qu'un seul VLAN.

- Exemple de port ACCESS avec VLAN data + voix :

<img width="329" height="146" alt="interf_mode_access_voice" src="https://github.com/user-attachments/assets/e78b3c58-7ede-4b47-891e-d280ed67cc96" />

<BVR><BVR>

- Exemple de port TRUNK (liaison entre switches L2 et L3) :

<img width="332" height="125" alt="interf_mode_trunk_native" src="https://github.com/user-attachments/assets/426094a7-feba-4b44-a0f8-21e8383cec2b" />

<BVR><BVR>

Dans ce TP, le VLAN 99 est utilisé comme VLAN natif sur les trunks à la place du VLAN 1.  
Tout le trafic non taggé circule ainsi dans un VLAN dédié qui n’est pas utilisé par les utilisateurs.  
C’est plus sécurisé, car le VLAN 1 est le VLAN par défaut de tous les switches et transporte souvent du trafic de gestion (CDP, VTP, STP, DTP...).  
En déplaçant le VLAN natif vers un VLAN spécifique (99) et en évitant d’y connecter des équipements utilisateurs, on isole ce trafic de gestion du trafic user et on réduit les risques d’attaques liées au VLAN 1.

<BVR><BVR>

```
interface fastethernet 0/5
switchport mode access
switchport access vlan 10
switchport voice vlan 40
show interfaces switchport
```

```
interface fastethernet 0/3
switchport mode trunk
switchport trunk native vlan 99
show interfaces switchport
```

<BVR><BVR>

#### EtherChannel entre switches L2 et L3 (agrégation de liens)
Etherchannel permet d’agréger plusieurs liens physiques en un seul lien logique (Port-Channel), pour augmenter la bande passante et la redondance.

<BVR><BVR>

<img width="423" height="281" alt="conf_etherchannel_pagp" src="https://github.com/user-attachments/assets/a5a8a6e8-d9c9-4fb1-9999-6680863d11f8" />

<BVR><BVR>

<img width="490" height="322" alt="conf_etherchannel_pagp2" src="https://github.com/user-attachments/assets/795837df-5eed-4807-873f-d821c6e5b96d" />

<BVR><BVR>

- Il existe deux principaux protocoles d’agrégation de liens : LACP (Link Aggregation Control Protocol) et PAgP (Port Aggregation Protocol). LACP est un standard ouvert (IEEE 802.3ad) supporté par la plupart des constructeurs, tandis que PAgP est un protocole propriétaire Cisco utilisé uniquement entre équipements Cisco. Il existe aussi un mode d’EtherChannel sans protocole de négociation, en mode "on" des deux côtés, qui force la création du bundle sans utiliser ni LACP ni PAgP.

```
interface range Fa0/1 - 2
  switchport mode trunk
  switchport trunk encapsulation dot1q    ! si nécessaire (sur les modèles L3, pas L2)
  switchport trunk native vlan 99
```

```
interface range Fa0/1 - 2
  channel-group 1 mode desirable       
```

```
interface range Fa0/1 - 2
  channel-group 1 mode auto
```

<BVR><BVR>


#### Spanning Tree Protocol (STP)
STP est utilisé pour éviter les boucles de niveau 2 lorsque plusieurs liens redondants existent entre les switches.

Dans cette topologie, le protocole Spanning Tree (STP) est activé par défaut sur les switches Cisco et fonctionne ici conjointement avec l’EtherChannel pour garantir qu’il n’existe qu’un seul chemin logique actif, tout en conservant de la redondance en cas de panne de lien.​

STP échange des BPDUs (Bridge Protocol Data Units) entre les switches afin d’élire un root bridge et de placer certains ports en état bloqué si nécessaire, ce qui empêche les trames de tourner en boucle dans le réseau. Dans ce TP, aucune configuration avancée de STP (changement de priorité, Rapid PVST+, etc.) n’a été effectuée : le comportement par défaut du switch est conservé, ce qui est suffisant pour cette topologie de test.

<BVR><BVR>

#### Routage inter-VLAN
Il permet à des périphériques appartenant à des VLAN différents de communiquer entre eux en passant par un routeur ou un switch de couche 3.

- Un switch de couche 3 permet de connecter plusieurs réseaux IP entre eux et de diriger les paquets en fonction de leur adresse IP, tout en continuant à commuter les trames au niveau 2 à l’intérieur des VLAN.
- Il joue donc à la fois le rôle de switch L2 pour la commutation locale et de routeur pour le routage inter-VLAN et entre sous-réseaux.

<BVR><BVR>

Principe du routage inter-VLAN avec un switch L3 :

- Chaque VLAN dispose d’une interface virtuelle de type SVI (Switch Virtual Interface) sur le switch de couche 3, avec une adresse IP qui sert de passerelle par défaut pour les hôtes de ce VLAN.​
- Une fois la commande ip routing activée, le switch L3 réalise le routage entre ces interfaces VLAN (SVI), ce qui permet la communication entre les différents VLAN.

<BVR><BVR>

<img width="575" height="508" alt="routage_inter_vlan" src="https://github.com/user-attachments/assets/79cd7bb8-d760-4bc6-9a23-1f386cc66b7d" />

<BVR><BVR>

<img width="358" height="489" alt="routage_inter_vlan2" src="https://github.com/user-attachments/assets/4d1a62b3-68d4-4b2b-9202-9daeb2e5f48b" />

<BVR><BVR>

- Les interfaces Vlan10, Vlan20, Vlan30, Vlan40 et Vlan50 sont en état up/up et possèdent chacune une adresse IP, qui sert de passerelle par défaut aux hôtes de chaque VLAN.
- Le switch de couche 3 dispose donc d’une SVI par VLAN, ce qui lui permet d’assurer le routage inter-VLAN entre ces sous-réseaux.

<BVR><BVR>

<img width="570" height="439" alt="routage_inter_vlan3" src="https://github.com/user-attachments/assets/f7eb7526-acdb-4b92-b117-ded05df26296" />

<BVR><BVR>

- Les réseaux 192.168.10.0/24, 192.168.20.0/24, 192.168.30.0/24, 192.168.40.0/24 et 192.168.50.0/24 apparaissent en C (connected), chacun associé à son interface VlanX, ce qui confirme que le switch L3 possède une SVI par VLAN et peut router entre ces sous-réseaux.​

<BVR><BVR>

- Ne pas oublier de configurer le lien vers les autres switches en trunk (déjà fait avec l'etherchannel)

```
interface range Fa0/1 - 2
 switchport trunk encapsulation dot1q
 switchport mode trunk
```


1 - Activer le routage IPv4 sur les Switch L3

```
conf t
 ip routing
```
2 - SVI (SVI = interface VlanX) pour chaque VLAN

```
interface Vlan10
 ip address 192.168.10.1 255.255.255.0
 no shutdown

interface Vlan20
 ip address 192.168.20.1 255.255.255.0
 no shutdown
```

<BVR><BVR>

#### FHRP (First Hop Redundancy Protocol/passerelle par défaut redondante)
FHRP désigne une famille de protocoles qui assurent la redondance de la passerelle par défaut pour les hôtes d’un réseau local. L’idée est de faire fonctionner plusieurs routeurs ou switches L3 comme s’ils étaient une seule passerelle IP, afin qu’en cas de panne de l’un d’eux, un autre prenne automatiquement le relais sans changement de configuration côté clients.

Parmi ces protocoles, HSRP (Hot Standby Router Protocol, propriétaire Cisco) permet de créer une passerelle IP virtuelle partagée entre plusieurs équipements, avec un routeur/switch L3 actif et un standby prêt à prendre la main en cas de défaillance.

- Dans cette topologie, deux switches de couche 3 participent à des groupes HSRP pour les VLAN 10, 20, 30, 40 et 50. Une adresse IP virtuelle HSRP est définie par VLAN (par exemple 192.168.10.254 pour le VLAN 10), et c’est cette adresse qui est configurée comme passerelle par défaut sur les clients.​
Le switch S1 est configuré avec une priorité plus élevée pour être l’équipement actif sur ces VLAN, tandis que le second switch S2 reste en standby et prend automatiquement le relais si S1 devient indisponible.

<BVR><BVR>

<img width="572" height="132" alt="conf_HSRP_S1" src="https://github.com/user-attachments/assets/f3606622-2f7a-4ea6-8822-cb92c3a10557" />

<BVR><BVR>

<img width="569" height="133" alt="conf_HSRP_S2" src="https://github.com/user-attachments/assets/aae295fc-8920-4dd8-997e-1288130e55b0" />

<BVR><BVR>

Sur S1, les VLAN 10, 20 et 50 sont en état Active, tandis que les VLAN 30 et 40 sont en Standby, ce qui signifie que S1 est la passerelle active pour certains VLAN et le switch de secours pour d’autres.​
Sur S2, c’est l’inverse : il est Active pour les VLAN 30 et 40, et Standby pour les VLAN 10, 20 et 50, ce qui répartit la charge tout en assurant la redondance pour chaque passerelle virtuelle (192.168.X.254) utilisée par les clients.


  - Sur S1 (actif préféré) :
 
```
interface Vlan10
 ip address 192.168.10.1 255.255.255.0
 standby 10 ip 192.168.10.254
 standby 10 priority 110
 standby 10 preempt

interface Vlan20
 ip address 192.168.20.1 255.255.255.0
 standby 20 ip 192.168.20.254
 standby 20 priority 110
 standby 20 preempt
! ... même logique pour Vlan30,40,50
```

  - Sur S2 (backup) :

```
interface Vlan10
 ip address 192.168.10.2 255.255.255.0
 standby 10 ip 192.168.10.254
 standby 10 priority 100
 standby 10 preempt
! ... idem pour les autres VLAN
```

<BVR><BVR>

#### Serveur DHCP central et ip helper-address
Un serveur DHCP attribue automatiquement aux clients leur adresse IP, leur masque, leur passerelle et éventuellement leurs DNS. Dans un réseau multi‑VLAN, il est courant d’utiliser un serveur DHCP central pour tous les VLANs.
​​
- Les requêtes DHCP des clients sont envoyées en broadcast et ne sont pas routées entre les VLANs. La commande **ip helper-address**, configurée sur les SVI des switches de couche 3, permet de relayer ces requêtes vers le serveur DHCP situé dans un autre réseau : le switch L3 transforme le broadcast reçu dans un VLAN en unicast vers l’adresse IP du serveur DHCP.​

- Pour rappel, un broadcast est un message envoyé à toutes les machines d’un même réseau (même VLAN) en utilisant une adresse de diffusion, et qui n’est pas transmis aux autres réseaux.

<BVR><BVR>

<img width="364" height="489" alt="Conf_ip_helper_dhcp" src="https://github.com/user-attachments/assets/05fee952-a228-49bc-bc87-700eee41b8b9" />

<BVR><BVR>

Ce résultat montre la configuration des interfaces VLAN (SVI) sur le switch de couche 3 S1. Chaque VLAN dispose d’une adresse IP qui sert de passerelle par défaut pour les clients (ex. 192.168.10.1 pour le VLAN 10). La commande ip helper-address 192.168.30.253 sur chaque SVI permet de relayer les requêtes DHCP vers le serveur situé dans le réseau 192.168.30.0/24.​

Sur le serveur DHCP central, un pool (ou scope) est configuré pour chaque VLAN utilisateur, avec une plage d’adresses, un masque et une passerelle adaptés à ce VLAN.

<BVR><BVR>

<img width="641" height="527" alt="pool_dhcp" src="https://github.com/user-attachments/assets/8b79d674-942a-43b4-b14c-24d0e4068fce" />

<BVR><BVR>

  - Ce screenshot montre les différents scopes DHCP correspondant aux VLANs du réseau, chacun avec son réseau, sa passerelle par défaut et son DNS.

<BVR><BVR>

<img width="641" height="530" alt="pool_dhcp_vlan40_voice_server_tftp" src="https://github.com/user-attachments/assets/ef280062-d5f2-4c8c-86a6-ff3793a81825" />

<BVR><BVR>

  - Pour le VLAN 40 dédié à la voix, le pool DHCP fournit également l’adresse du serveur TFTP, hébergé sur le routeur R1, afin que les téléphones IP puissent télécharger automatiquement leurs fichiers de configuration et leur firmware nécessaires à l’enregistrement et au fonctionnement de la téléphonie.

```
interface Vlan10
  ip address 192.168.10.1 255.255.255.0
  ip helper-address 192.168.30.253
```

<BVR><BVR>

#### Téléphonie IP et rôle du serveur TFTP
La téléphonie IP de l’entreprise s’appuie sur un serveur TFTP hébergé sur le routeur R1, vers lequel les téléphones IP sont dirigés grâce aux informations fournies par le serveur DHCP (option dédiée dans le pool du VLAN voix 40). Après avoir obtenu leur adresse IP, leur passerelle et l’adresse du serveur TFTP, les téléphones téléchargent automatiquement, depuis ce serveur, leurs fichiers de configuration et leur firmware, ce qui leur permet de s’enregistrer correctement sur la plateforme de téléphonie et de fonctionner.

<BVR><BVR>

Les ports des switches auxquels sont raccordés les téléphones sont configurés en mode access avec un VLAN voix dédié (VLAN 40), ce qui permet de séparer le trafic de téléphonie du trafic data tout en partageant le même lien physique avec le PC utilisateur éventuellement connecté derrière le téléphone.

Lors de son démarrage, un téléphone IP rejoint d’abord le VLAN voix, obtient une adresse IP via DHCP, ainsi que l’adresse du serveur TFTP, puis contacte ce serveur pour récupérer ses fichiers de configuration et, si nécessaire, son firmware avant de s’enregistrer sur le serveur de téléphonie.


<BVR><BVR>

<img width="505" height="165" alt="conf_tel_IP" src="https://github.com/user-attachments/assets/d01a4c5a-21dd-446c-b264-f7c47de89a69" />


<BVR><BVR>

<img width="524" height="399" alt="conf_tel_IP2" src="https://github.com/user-attachments/assets/555e4008-246b-4e0b-8328-61a673bd065e" />


<BVR><BVR>

<img width="373" height="80" alt="conf_tel_service" src="https://github.com/user-attachments/assets/94a090bd-2b05-4814-9411-8beda0730ae0" />

<BVR><BVR>

Cette section **telephony-service** configure Cisco CME sur R1 : elle définit le nombre maximal de téléphones (max-ephones) et de numéros (max-dn), ainsi que l’adresse IP source utilisée par le routeur pour dialoguer avec les téléphones IP sur le port SCCP 2000. Dans ce TP, l’adresse 10.0.0.2 correspond au serveur TFTP hébergé sur R1, tandis que 192.168.40.254 est la passerelle du VLAN voix 40 utilisée comme ip source-address pour le service de téléphonie.


<img width="360" height="289" alt="conf_tel_service2" src="https://github.com/user-attachments/assets/475bf46f-d2fe-4bbe-a3b8-107c251fc7b4" />

<BVR><BVR>

<img width="612" height="176" alt="conf_tel_service3" src="https://github.com/user-attachments/assets/3ead9cb9-259d-4fb3-b37d-81c0d7c9b7bb" />

<BVR><BVR>

La section ephone-dn définit les numéros internes (101 à 105), tandis que les blocs ephone associent chaque téléphone physique (identifié par son adresse MAC et son modèle 7960) à un de ces numéros via la commande button. La commande show ephone confirme que les téléphones sont bien REGISTERED et qu’ils ont obtenu une adresse IP dans le VLAN voix (192.168.40.51 et 192.168.40.52), prêts à passer des appels.



```
R1(config)#telephony-service
R1(config-telephony)#max-ephones 5
R1(config-telephony)#max-dn 5
R1(config-telephony)#ip source-address 192.168.40.254 port 2000
R1(config-telephony)#auto assign 1 to 5
R1(config-telephony)#create cnf-files
```

<BVR><BVR>

```
! Numéros internes
R1(config)#ephone-dn 1
R1(config-ephone-dn)#number 101
R1(config-ephone-dn)#exit
R1(config)#ephone-dn 2
R1(config-ephone-dn)#number 102
```

<BVR><BVR>

#### Routage OSPF (Open Shortest Path First)
OSPF est un protocole de routage dynamique de type « état de liens » qui permet aux routeurs et switches L3 d’échanger automatiquement les informations de routes au sein d’un même domaine. Chaque routeur construit une carte complète de la topologie en échangeant l’état de ses liens avec ses voisins, puis calcule le meilleur chemin vers chaque réseau à l’aide de l’algorithme de Dijkstra (coût), ce qui évite de maintenir manuellement des routes statiques et offre une convergence rapide, adaptée aux réseaux de taille moyenne à grande.

Dans cette topologie, les liaisons OSPF entre les switches L3 et les routeurs R1/R2 sont de type point-à-point, ce qui simplifie le fonctionnement du protocole (pas de DR/BDR) et accélère la convergence entre deux équipements

Le routage interne au siège entre les switches de couche 3 et les routeurs R1 et R2 repose sur OSPF, qui diffuse automatiquement les différents réseaux du LAN (VLAN utilisateurs, VLAN voix, etc.) entre les équipements. Ainsi, chaque équipement connaît les sous-réseaux présents au siège sans recourir à des routes statiques, ce qui facilite l’évolution et la maintenance de la topologie.

<BVR><BVR>

<img width="539" height="346" alt="conf_R1_Ospf" src="https://github.com/user-attachments/assets/910712c2-2cc5-4467-a339-5a702ddc23f3" />


<BVR><BVR>

<img width="536" height="341" alt="conf_R1_Ospf2" src="https://github.com/user-attachments/assets/a76cf65e-c237-4b2c-bc6f-5a1c08946063" />


La commande show ip ospf database affiche la base de données de LSAs OSPF, qui représente la vision complète de la topologie partagée entre les routeurs : on y retrouve les routeurs OSPF présents au siège ainsi que les différents réseaux annoncés (VLAN utilisateurs, VLAN voix, liens de transit). Cela confirme que tous les équipements partagent la même carte du réseau et peuvent calculer les meilleurs chemins.​
Ces captures montrent que les équipements du siège partagent le même processus OSPF (process ID 10) mais possèdent chacun un Router ID différent, ce qui permet de les identifier de façon unique dans la base OSPF tout en appartenant au même domaine de routage.

<img width="590" height="151" alt="conf_R1_Ospf3" src="https://github.com/user-attachments/assets/44d5bcce-0e1a-4a75-8b44-79ea149a51a1" />

La commande show ip ospf neighbor permet de vérifier les relations de voisinage OSPF entre les switches L3 et les routeurs R1/R2 (état FULL), ce qui confirme que les adjacences sont établies et que les LSAs peuvent être échangées. L’état FULL indique que la synchronisation de la base de données OSPF est complète avec ces voisins.

<img width="575" height="449" alt="conf_R1_Ospf4" src="https://github.com/user-attachments/assets/d851d8d3-917b-44f2-ab30-ac166042b2aa" />

Dans la table de routage, les routes apprises par OSPF sont marquées par la lettre O, ce qui permet de distinguer facilement les réseaux appris dynamiquement de ceux qui sont directement connectés (C) ou configurés en statique (S)

```
S1(config)#router ospf 10
S1(config-router)#router-id 1.1.1.1
S1(config-router)#do show ip route connected
S1(config-router)#network 10.0.0.0 0.0.0.3 area 0
S1(config-router)#network 192.168.10.0 0.0.0.255 area 0
S1(config-router)#network 192.168.20.0 0.0.0.255 area 0
S1(config-router)#network 192.168.30.0 0.0.0.255 area 0
S1(config-router)#network 192.168.40.0 0.0.0.255 area 0
S1#show ip ospf database
S1#show ip ospf neighbor
```

#### NAT(Network Address Translation) et PAT(Port Address Translation) pour l’accès Internet 
La traduction d’adresses (NAT) permet aux hôtes des réseaux privés d’accéder à Internet en utilisant une ou plusieurs adresses IP publiques portées par le routeur. Le PAT (Port Address Translation), aussi appelé NAT overload, permet à de nombreux clients internes de partager une seule adresse publique en différenciant les connexions par les numéros de port source.


```
! 1) Marquer les interfaces inside / outside
R1(config)#interface FastEthernet0/0
R1(config-if)#ip address 172.16.10.1 255.255.255.0
R1(config-if)#ip nat inside
R1(config-if)#exit

R1(config)#interface Serial0/3/0
R1(config-if)#ip address 200.0.0.1 255.255.255.252
R1(config-if)#ip nat outside
R1(config-if)#exit
```

```
! 2) ACL des réseaux internes à traduire
R1(config)#access-list 1 permit 172.16.10.0 0.0.0.255
```

```
! 3) NAT overload (PAT) vers l’interface WAN
R1(config)#ip nat inside source list 1 interface Serial0/3/0 overload
```

```
R1#show ip nat translations
```

La commande show ip nat translations permet de vérifier les traductions NAT/PAT en cours (correspondance entre les adresses privées du LAN et l’adresse publique 200.0.0.1 avec des ports différents).









- `docs/02-routage-ospf-et-acces-internet.md`  
  OSPF interne, liens WAN vers l’ISP, routes par défaut et routage de retour.

- `docs/03-dhcp-dns-et-nat-par-site.md`  
  DHCP, DNS, PAT/NAT sur le siège, la succursale et le site Home.

- `docs/04-voip-cme-au-siege.md`  
  Mise en place de Cisco CME, VLAN voix, DHCP/TFTP pour les téléphones IP.

- `docs/05-vpn-ipsec-r1-rhome.md`  
  Configuration complète du VPN IPsec site-à-site entre le siège (R1) et RHOME, avec exemption NAT et commandes de vérification. 

Chaque fichier contient :

- Les extraits de configuration IOS.
- Une explication ligne par ligne des commandes importantes.
- Les commandes de vérification à lancer (ping, `show ip route`, `show standby`, `show crypto ...`, etc.)
