#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV -> LaTeX pour le dictionnaire Brassens.

CSV attendu : séparateur ';'
Colonnes utilisées :
    ID, Inclure, entrée, type, catégorie, registre, nature,
    définition, expression_ou_image, extrait, chanson,
    occurrences, statut, source, Commentaire

Sortie :
    - commandes \letterXtrue pour les lettres présentes ;
    - entrées \entry{mot}{prononciation}{nature}{définition}{extrait}{source} ;
    - tri alphabétique français sur l'entrée.

Par défaut, seules les lignes dont "Inclure" vaut OUI sont exportées.
Pour tester le fichier actuel (où les 450 lignes sont "À VOIR"),
utiliser --all.
"""

import argparse
import csv
import re
import unicodedata
from pathlib import Path


TRUTHY = {"oui", "yes", "y", "1", "x", "true", "vrai"}
FALSEY = {"non", "no", "n", "0", "x", "false", "faux"}


def strip_accents(text):
    """Supprime les accents pour les tests/sorties de contrôle."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def first_letter(text):
    """Première lettre alphabétique, normalisée pour A-Z."""
    for char in text.strip():
        # É, À, Ç, etc. -> E, A, C...
        base = strip_accents(char).upper()
        if "A" <= base <= "Z":
            return base
    return None


def french_sort_key(text):
    """
    Clé de tri alphabétique simple et stable :
    accents ignorés pour l'ordre, mais le texte original est conservé.
    """
    normalized = unicodedata.normalize("NFD", text.casefold())
    normalized = "".join(
        c for c in normalized if unicodedata.category(c) != "Mn"
    )
    return normalized


def latex_escape(text):
    """
    Protection minimale des caractères spéciaux LaTeX.
    On conserve les accents UTF-8 pour pdfLaTeX + T1.
    """
    if text is None:
        return ""

    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    return "".join(replacements.get(c, c) for c in text)


def clean_text(text):
    """Nettoyage léger des espaces sans modifier le contenu lexical."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def included(row):
    value = clean_text(row.get("Inclure", "")).casefold()
    return value in TRUTHY


def build_entry(row):
    word = clean_text(row.get("entrée", ""))
    nature = clean_text(row.get("nature", ""))

    # Le CSV ne contient pas de prononciation :
    # argument 2 laissé volontairement vide.
    pronunciation = ""

    definition = clean_text(row.get("définition", ""))
    excerpt = clean_text(row.get("extrait", ""))
    source = clean_text(row.get("source", ""))

    # Si la définition est absente mais qu'une expression/image est renseignée,
    # on ne l'invente pas : elle est simplement conservée dans l'extrait.
    if not definition:
        definition = clean_text(row.get("expression_ou_image", ""))

    values = [
        word,
        pronunciation,
        nature,
        definition,
        excerpt,
        source,
    ]

    return r"\entry{" + "}{".join(latex_escape(v) for v in values) + "}"


def main():
    parser = argparse.ArgumentParser(
        description="Génère le contenu LaTeX du dictionnaire depuis un CSV."
    )
    parser.add_argument(
        "csv",
        help="CSV d'entrée, séparateur ';'"
    )
    parser.add_argument(
        "-o", "--output",
        default="../dictionnaire_entries.tex",
        help="Fichier LaTeX de sortie"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Inclut toutes les lignes, quelle que soit la colonne Inclure"
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    output_path = Path(args.output)

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")

        required = {"Inclure", "entrée", "nature", "définition", "extrait", "source"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(
                "Colonnes manquantes dans le CSV : "
                + ", ".join(sorted(missing))
            )

        rows = list(reader)

    if args.all:
        selected = rows
    else:
        selected = [row for row in rows if included(row)]

    # Élimination des entrées sans mot.
    selected = [
        row for row in selected
        if clean_text(row.get("entrée", ""))
    ]

    selected.sort(key=lambda row: french_sort_key(row["entrée"]))

    # Lettres réellement présentes.
    letters = sorted({
        first_letter(row["entrée"])
        for row in selected
        if first_letter(row["entrée"])
    })

    lines = []
    lines.append("% ============================================================")
    lines.append("% Généré automatiquement depuis : " + csv_path.name)
    lines.append("% Ne pas modifier manuellement.")
    lines.append("% ============================================================")
    lines.append("")

    lines.append("% Lettres présentes dans le dictionnaire")
    for letter in letters:
        lines.append(rf"\letter{letter}true")
    lines.append("")

    lines.append("% Entrées du dictionnaire")
    lines.append("")

    for row in selected:
        letter = first_letter(row["entrée"])
        lines.append(build_entry(row))
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"CSV lu              : {csv_path}")
    print(f"Lignes du CSV       : {len(rows)}")
    print(f"Entrées exportées   : {len(selected)}")
    print(f"Lettres présentes   : {', '.join(letters) if letters else '(aucune)'}")
    print(f"Fichier LaTeX       : {output_path}")


if __name__ == "__main__":
    main()
