import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help = "Dossier à trier")
    parser.add_argument("--dry-run", action="store_true", help="Simuler le tri sans déplacer les fichiers")
    args = parser.parse_args()


    source = Path(args.source)
    print("Dossier source :", source)

    for i in source.iterdir():
        if i.is_file():
            extension = i.suffix.lower()
            sous_dossier_nom = extension[1:].upper() 
            sous_dossier = source / sous_dossier_nom
            sous_dossier.mkdir(exist_ok=True)

            destination = sous_dossier / i.name

            print("FICHIER :", i.name, "|EXTENSION :", extension, "|DOSSIER :", sous_dossier_nom, "|DESTINATION :", destination)

            if args.dry_run:
                print("MODE DRY-RUN : Fichier NON déplacé")
            else:
                i.replace(destination)
       

if __name__ == "__main__":
    main()
