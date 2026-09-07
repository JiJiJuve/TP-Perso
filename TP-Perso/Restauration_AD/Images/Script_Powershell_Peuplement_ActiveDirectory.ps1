Import-Module ActiveDirectory
Import-Module GroupPolicy

$DomainDN = (Get-ADDomain).DistinguishedName
$DNSRoot = (Get-ADDomain).DNSRoot

# Création des OU
$OUs = @(
    @{Name="LAB-Utilisateurs"; Path=$DomainDN},
    @{Name="LAB-Groupes"; Path=$DomainDN},
    @{Name="LAB-Ordinateurs"; Path=$DomainDN},
    @{Name="LAB-Administratifs"; Path="OU=LAB-Utilisateurs,$DomainDN"},
    @{Name="LAB-Techniques"; Path="OU=LAB-Utilisateurs,$DomainDN"}
)

foreach ($OU in $OUs) {
    $ExistingOU = Get-ADOrganizationalUnit `
        -Filter "Name -eq '$($OU.Name)'" `
        -SearchBase $OU.Path `
        -ErrorAction SilentlyContinue

    if (-not $ExistingOU) {
        New-ADOrganizationalUnit `
            -Name $OU.Name `
            -Path $OU.Path `
            -ProtectedFromAccidentalDeletion $false
    }
}

# Création des groupes
$GroupPath = "OU=LAB-Groupes,$DomainDN"

$Groups = @(
    "LAB-Admins",
    "LAB-Users",
    "LAB-IT",
    "LAB-Test-GPO"
)

foreach ($Group in $Groups) {
    if (-not (Get-ADGroup `
        -Filter "SamAccountName -eq '$Group'" `
        -ErrorAction SilentlyContinue)) {

        New-ADGroup `
            -Name $Group `
            -SamAccountName $Group `
            -GroupScope Global `
            -GroupCategory Security `
            -Path $GroupPath
    }
}

# Mot de passe de laboratoire uniquement
$Password = ConvertTo-SecureString `
    "Lab-Test-2026!" `
    -AsPlainText `
    -Force

# Utilisateurs de test
$Users = @(
    @{
        First="Alice"
        Last="Martin"
        Login="amartin"
        OU="LAB-Administratifs"
        Group="LAB-Users"
    },
    @{
        First="Karim"
        Last="Durand"
        Login="kdurand"
        OU="LAB-Techniques"
        Group="LAB-IT"
    },
    @{
        First="Sophie"
        Last="Bernard"
        Login="sbernard"
        OU="LAB-Techniques"
        Group="LAB-IT"
    },
    @{
        First="Paul"
        Last="Robert"
        Login="probert"
        OU="LAB-Administratifs"
        Group="LAB-Users"
    },
    @{
        First="Julie"
        Last="Petit"
        Login="jpetit"
        OU="LAB-Techniques"
        Group="LAB-IT"
    }
)

foreach ($User in $Users) {
    $UserPath = "OU=$($User.OU),OU=LAB-Utilisateurs,$DomainDN"

    $ExistingUser = Get-ADUser `
        -Filter "SamAccountName -eq '$($User.Login)'" `
        -ErrorAction SilentlyContinue

    if (-not $ExistingUser) {
        New-ADUser `
            -Name "$($User.First) $($User.Last)" `
            -GivenName $User.First `
            -Surname $User.Last `
            -DisplayName "$($User.First) $($User.Last)" `
            -SamAccountName $User.Login `
            -UserPrincipalName "$($User.Login)@$DNSRoot" `
            -Path $UserPath `
            -AccountPassword $Password `
            -Enabled $true `
            -ChangePasswordAtLogon $false
    }

    Add-ADGroupMember `
        -Identity $User.Group `
        -Members $User.Login `
        -ErrorAction SilentlyContinue
}

# Création de la GPO de test
$GPOName = "LAB - GPO Test"

$GPO = Get-GPO `
    -Name $GPOName `
    -ErrorAction SilentlyContinue

if (-not $GPO) {
    New-GPO -Name $GPOName
}

# Liaison de la GPO à l'OU des utilisateurs
$TargetOU = "OU=LAB-Utilisateurs,$DomainDN"

$ExistingLink = Get-GPInheritance `
    -Target $TargetOU

if ($ExistingLink.GpoLinks.DisplayName -notcontains $GPOName) {
    New-GPLink `
        -Name $GPOName `
        -Target $TargetOU `
        -LinkEnabled Yes
}

Write-Host "Peuplement du laboratoire terminé." -ForegroundColor Green