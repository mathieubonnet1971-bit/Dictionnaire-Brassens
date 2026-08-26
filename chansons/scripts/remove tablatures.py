#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import re

# Dossier contenant les fichiers à traiter
DOSSIER = Path(".")

# Extensions de fichiers à traiter
EXTENSIONS = {".txt", ".text"}

# Accord français :
# Do, Ré, Mi, Fa, Sol, La, Si
# avec variantes : m, 7, maj7, sus4, dim, aug, #, b, etc.
ACCORD = re.compile(
    r"^(?:"
    r"Do|Ré|Re|Mi|Fa|Sol|La|Si"
    r")(?:"
    r"m|M|maj|min|sus|dim|aug|add"
    r"|[0-9]+"
    r"|[#b]"
    r"|[#b]?[0-9]+"
    r"|[#b]?(?:maj|min|sus|dim|aug)[0-9]*"
    r")*"
    r"(?:/(?:Do|Ré|Re|Mi|Fa|Sol|La|Si))?$",
    re.IGNORECASE
)


def est_ligne_d_accords(ligne):
    """Retourne True si la ligne contient essentiellement des accords."""

    texte = ligne.strip()

    if not texte:
        return False

    # Séparation des éléments par les espaces
    elements = texte.split()

    if not elements:
        return False

    # Tous les éléments doivent être des accords
    nb_accords = sum(bool(ACCORD.fullmatch(element)) for element in elements)

    # On considère la ligne comme une ligne d'accords
    # si au moins 2 accords sont présents et qu'ils représentent
    # la quasi-totalité de la ligne.
    return nb_accords >= 2 and nb_accords / len(elements) >= 0.8


def traiter_fichier(fichier):
    texte = fichier.read_text(encoding="utf-8")

    lignes = texte.splitlines()
    nouvelles_lignes = []

    supprimees = 0

    for ligne in lignes:
        if est_ligne_d_accords(ligne):
            supprimees += 1
        else:
            nouvelles_lignes.append(ligne)

    sortie = fichier.with_name(fichier.stem + "_sans_accords" + fichier.suffix)

    sortie.write_text(
        "\n".join(nouvelles_lignes) + "\n",
        encoding="utf-8"
    )

    print(f"{fichier.name:40} → {sortie.name:45} "
          f"({supprimees} lignes supprimées)")


def main():
    fichiers = [
        f for f in DOSSIER.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSIONS
    ]

    if not fichiers:
        print("Aucun fichier trouvé.")
        return

    print(f"{len(fichiers)} fichier(s) trouvé(s).\n")

    for fichier in fichiers:
        traiter_fichier(fichier)


if __name__ == "__main__":
    main()
