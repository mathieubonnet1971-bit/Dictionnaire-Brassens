from pathlib import Path

DOSSIER = Path(".")
SORTIE = DOSSIER / "tous_les_textes.txt"

fichiers = sorted(
    f for f in DOSSIER.glob("*.txt")
    if f.name != SORTIE.name
)

with SORTIE.open("w", encoding="utf-8") as destination:

    for i, fichier in enumerate(fichiers):

        if i > 0:
            destination.write("\n\n\n")

        titre = fichier.stem

        destination.write(titre + "\n")
        destination.write("=" * len(titre) + "\n\n")

        contenu = fichier.read_text(encoding="utf-8").strip()

        destination.write(contenu)
        destination.write("\n")

print(f"{len(fichiers)} fichiers fusionnés dans : {SORTIE}")
