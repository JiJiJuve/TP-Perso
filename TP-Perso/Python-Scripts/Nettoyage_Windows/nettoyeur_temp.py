import os
from pathlib import Path

def main():
    total = 0
    dossiers = [
        os.environ["TEMP"],
        "C:/Windows/Temp",
        os.environ["LOCALAPPDATA"] + "/Temp",
        os.environ["LOCALAPPDATA"] + "/LibreWolf/Cache",
        "C:/Users/JiJi/Pictures/Screenshots",
    ]
    

    for dossier in dossiers:

        for fichier in Path(dossier).glob("*"):
            try:
                fichier.unlink()
                total += 1
            except:
                pass
    print(f"{total} fichiers supprimés !")
    input("Appuyez sur Entrée")




if __name__ == "__main__":
    main()
