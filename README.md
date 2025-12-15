# TP Réseau – Siège, Succursale et Site Home

## Sommaire

- [Présentation générale](#présentation-générale)
- [Objectifs pédagogiques](#objectifs-pédagogiques)
- [Topologie et adressage (résumé)](#topologie-et-adressage-résumé)
- [Contenu du dépôt](#contenu-du-dépôt)
- [Documentation détaillée](#documentation-détaillée)

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

# 01 – Commutation au siège : VLAN, VTP, trunks, EtherChannel, HSRP

## 1. Objectif de cette partie

L’objectif est de mettre en place l’infrastructure de niveau 2/3 au **siège** :

- Segmenter le LAN en plusieurs VLAN (utilisateurs, voix, serveurs, management).
- Distribuer automatiquement la base de VLAN avec **VTP**.
- Relier les switches via des **trunks** et un **EtherChannel**.
- Activer le **routage inter-VLAN** sur les switches L3.
- Assurer une **passerelle redondante** pour les clients avec **HSRP**.

---

## 2. VTP et base VLAN au siège

### 2.1 Configuration des VLAN, VTP, trunks, EtherChannel et HSRP dans le LAN du siège social.
  
#### VTP (Vlan Trunking Protocol) : permet de synchroniser la configuration des VLAN entre les switch.
    
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

### VLAN (Virtual Local Area Network) permettent de segmenter les réseaux physiques en sous réseaux-logiques.

<img width="557" height="251" alt="conf_Vlan_L3" src="https://github.com/user-attachments/assets/bdb0e239-97dd-4cdb-a6ea-0d32d54edebb" />

<BVR><BVR>

<img width="561" height="277" alt="conf_Vlan_L2" src="https://github.com/user-attachments/assets/3ce136ab-14b5-42ff-89e3-6ab9f7fdd273" />

<BVR><BVR>

```
vlan 10
name
show vlan brief
```

### Configuration des interfaces en mode ACCESS ou TRUNK : Les ports TRUNK laissent passer plusieurs VLANs grâce aux trames taggées (802.1Q), contrairement aux ports ACCESS qui n'acceptent qu'un seul VLAN.


la suite arrive bientot




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
