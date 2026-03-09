# 🔏 FICHE MÉMO – Signature de scripts PowerShell avec certificat auto-signé

Objectif : créer un certificat auto-signé de **code signing**, l’installer dans les bons magasins, puis signer et vérifier des scripts PowerShell.

***

## 1. Lancer PowerShell en administrateur

Certaines opérations sur les certificats et la politique d’exécution nécessitent une console PowerShell **élevée** (clic droit → Exécuter en tant qu’administrateur).

***

## 2. Créer un certificat auto-signé de code signing

```powershell
$SelfSignedCert = New-SelfSignedCertificate `
    -Subject "ScriptPowerShell" `
    -Type CodeSigningCert `
    -CertStoreLocation Cert:\LocalMachine\My `
    -FriendlyName "Signer scripts PowerShell" `
    -NotAfter (Get-Date).AddYears(5)
```

- `-Type CodeSigningCert` : certificat destiné à la **signature de code**.  
- `-CertStoreLocation` : ici magasin personnel de l’ordinateur (`LocalMachine\My`).  
- `-FriendlyName` : nom lisible pour retrouver le certificat facilement.  
- `-NotAfter` : durée de validité (ici 5 ans).

La variable `$SelfSignedCert` contient le certificat et sera réutilisée ensuite.

***

## 3. Exporter la partie publique en fichier .cer

```powershell
Export-Certificate -Cert $SelfSignedCert -FilePath "C:\Certificats\ScriptPowerShell.cer"
```

- Génère un fichier `.cer` contenant la **clé publique**.  
- Ce fichier servira à ajouter la confiance dans les magasins Windows.

***

## 4. Importer le certificat dans les magasins de confiance

Pour que Windows et PowerShell fassent confiance au certificat auto-signé, importer le `.cer` dans :  

```powershell
Import-Certificate -FilePath "C:\Certificats\ScriptPowerShell.cer" -CertStoreLocation Cert:\LocalMachine\Root
Import-Certificate -FilePath "C:\Certificats\ScriptPowerShell.cer" -CertStoreLocation Cert:\LocalMachine\TrustedPublisher
```

- `Root` : Autorités de certification racines de confiance.  
- `TrustedPublisher` : éditeurs approuvés (éditeurs de scripts / logiciels).  

Sans ces imports, la signature sera souvent refusée, surtout avec la politique `AllSigned`.

***

## 5. Signer un script PowerShell

```powershell
Set-AuthenticodeSignature -FilePath "C:\Scripts\MonScript.ps1" -Certificate $SelfSignedCert
```

- Ajoute une **signature numérique** au script.  
- Si le fichier est modifié après coup, la signature devient invalide.

Vérifier la signature :

```powershell
Get-AuthenticodeSignature -FilePath "C:\Scripts\MonScript.ps1"
```

- Regarder la propriété `Status` (`Valid`, `NotSigned`, `UnknownError`, etc.).

***

## 6. Configurer la politique d’exécution

```powershell
Set-ExecutionPolicy RemoteSigned
# ou
Set-ExecutionPolicy AllSigned
```

- `RemoteSigned` : les scripts **locaux** peuvent être non signés, ceux téléchargés doivent être signés par un éditeur de confiance.  
- `AllSigned` : **tous** les scripts doivent être signés par un éditeur de confiance.  

Vérifier la politique actuelle :

```powershell
Get-ExecutionPolicy
```

***

## 7. Réutiliser le certificat plus tard

Plus tard, pour retrouver ton certificat via son FriendlyName :

```powershell
$certificat = Get-ChildItem -Path Cert:\LocalMachine\My |
    Where-Object { $_.FriendlyName -eq "Signer scripts PowerShell" }
```

Signer un autre script :

```powershell
Set-AuthenticodeSignature -FilePath "C:\Scripts\AutreScript.ps1" -Certificate $certificat
```

***

## 8. Points clés à retenir

- Certificat **auto-signé** : suffisant pour tes scripts perso, lab, dev.  
- Fichier `.cer` : contient la clé publique, à importer dans `Root` et `TrustedPublisher`.  
- Signature : garantit l’**intégrité** et la **provenance** du script. Toute modification rend la signature invalide.  
- Politique d’exécution : avec `RemoteSigned` ou `AllSigned`, PowerShell n’exécute que les scripts considérés comme fiables.
