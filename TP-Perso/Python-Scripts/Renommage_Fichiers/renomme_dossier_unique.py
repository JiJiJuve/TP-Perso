from pathlib import Path

dossier = Path(r"C:\Users\JiJi\Pictures\Vac")
prefixe = "Vacances_2025_Mai_Grde_Motte"
compteur = 1
extensions_autorisees = {".jpg", ".mp4"}

for image in dossier.iterdir():
    if image.is_file():
        extension = image.suffix.lower()
        if extension in extensions_autorisees:
            nouveau_nom = f"{prefixe}_{compteur:03d}{extension}"
            nouvelle_image = image.with_name(nouveau_nom)
            print(image.name, "->", nouveau_nom)
            image.rename(nouvelle_image)
            compteur += 1

