import argparse
from pathlib import Path

def main():
   parser = argparse.ArgumentParser()
   parser.add_argument("--dossier", required=True, help="Chemin du dossier à traiter")
   parser.add_argument("--prefixe", required=True, help="Préfixe pour les nouveaux noms")
   args = parser.parse_args()

   #print("Args reçus :", args)

   dossier = Path(args.dossier)
   prefixe = args.prefixe
   compteur = 1
   extensions_autorisees = {".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov", ".avi"}

   for i in dossier.iterdir():
      if i.is_file():
         extension = i.suffix.lower()
         if extension in extensions_autorisees:
            nouveau_nom = f"{prefixe}_{compteur:03d}{extension}"
            nouvelle_image = i.with_name(nouveau_nom)
            print(i.name, "->", nouveau_nom)
            i.rename(nouvelle_image)
            compteur += 1

if __name__ == "__main__":
    main()

