#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import unicodedata
from pathlib import Path


# ============================================================
# FICHIERS
# ============================================================

CSV_ENTREE = Path("../lexique_v3_450_propre.csv")
TEX_SORTIE = Path("../lexique.tex")


# ============================================================
# CONFIGURATION
# ============================================================

# Seules les entrées marquées OUI sont exportées.
VALEUR_INCLURE = "OUI"
col_n = 2   # Column number

# ============================================================
# OUTILS
# ============================================================

def enlever_accents(texte):
    """Supprime les accents pour le classement."""

    texte = unicodedata.normalize("NFD", texte)

    return "".join(
        c for c in texte
        if unicodedata.category(c) != "Mn"
    )


def cle_alphabetique(texte):
    """
    Clé de classement alphabétique.

    Les accents sont ignorés pour le tri :
        à -> a
        é -> e
        è -> e
        ê -> e
        ç -> c
    """

    texte = texte.strip().lower()
    texte = texte.replace("’", "'")

    return enlever_accents(texte)


def premiere_lettre(texte):
    """Détermine la lettre de l'intercalaire."""

    texte = texte.strip()

    if not texte:
        return ""

    return enlever_accents(texte[0]).upper()


def majuscule_initiale(texte):
    """
    Met la première lettre en majuscule,
    en conservant son accent éventuel.
    """

    texte = texte.strip()

    if not texte:
        return ""

    return texte[0].upper() + texte[1:]


def echapper_latex(texte):

    if texte is None:
        return ""

    texte = str(texte)

    texte = texte.replace("&", r"\&")
    texte = texte.replace("%", r"\%")
    texte = texte.replace("$", r"\$")
    texte = texte.replace("#", r"\#")
    texte = texte.replace("_", r"\_")
    texte = texte.replace("{", r"\{")
    texte = texte.replace("}", r"\}")
    texte = texte.replace("~", r"\textasciitilde{}")
    texte = texte.replace("^", r"\textasciicircum{}")

    return texte


# ============================================================
# TYPE
# ============================================================

def convertir_type(nature, type_entree):

    nature = (nature or "").strip().lower()
    type_entree = (type_entree or "").strip().lower()

    if "nom" in nature:
        return "Noun"

    if "adj" in nature:
        return "Adjective"

    if "verbe" in nature:
        return "Verb"

    if "adv" in nature:
        return "Adverb"

    if "locution" in nature:
        return "Expression"

    if type_entree == "expression":
        return "Expression"

    return ""


# ============================================================
# LECTURE DU CSV
# ============================================================

def lire_csv():

    with CSV_ENTREE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as fichier:

        lecteur = csv.DictReader(
            fichier,
            delimiter=";"
        )

        entrees = []

        for ligne in lecteur:

            # Ne conserver que les entrées sélectionnées
            if ligne["Inclure"].strip().upper() != VALEUR_INCLURE:
                continue

            entree = ligne["entrée"].strip()

            if not entree:
                continue

            entrees.append(ligne)

    return entrees


# ============================================================
# GÉNÉRATION DE \entry
# ============================================================

def generer_entry(ligne):

    entree = majuscule_initiale(ligne.get("entrée", ""))
    prononciation = ligne.get("prononciation", "")
    nature = ligne.get("nature", "")
    definition = ligne.get("définition", "")
    expression = ligne.get("expression_ou_image", "")
    extrait = ligne.get("extrait", "")

    champs = [
        entree,
        prononciation,
        nature,
        definition,
        expression,
        extrait,
    ]

    champs = [
        echapper_latex(champ)
        for champ in champs
    ]

    return "\\entry{" + "}{".join(champs) + "}"


# ============================================================
# GÉNÉRATION DE L'ALPHABET LATERAL
# ============================================================

def generer_liste_lettres(entrees):
    """
    Retourne les lettres de l'alphabet qui possèdent
    au moins une entrée sélectionnée.
    """

    lettres = set()

    for ligne in entrees:
        lettre = premiere_lettre(ligne["entrée"])

        if lettre:
            lettres.add(lettre)

    return "".join(
        lettre
        for lettre in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if lettre in lettres
    )

# ============================================================
# GÉNÉRATION INDICATEURS LETTRES
# ============================================================

def generer_indicateurs_lettres(entrees):
    lettres = set()

    for ligne in entrees:
        lettre = premiere_lettre(ligne["entrée"])

        if lettre:
            lettres.add(lettre.upper())

    presentes = "".join(
        lettre
        for lettre in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if lettre in lettres
    )

    return f"\\def\\lettersWithEntries{{{presentes}}}"

# ============================================================
# INTERCALAIRE
# ============================================================

def debut_section(lettre):

    return f"""%----------------------------------------------------------------------------------------
%	SECTION {lettre}
%----------------------------------------------------------------------------------------

\\section*{{{lettre}}}

\\begin{{multicols}}{{{col_n}}}

"""


def fin_section():

    return """\\end{multicols}

"""


# ============================================================
# GÉNÉRATION DU LATEX
# ============================================================

def generer_latex(entrees):

    # --------------------------------------------------------
    # Tri alphabétique
    # --------------------------------------------------------

    entrees.sort(
        key=lambda ligne:
            cle_alphabetique(ligne["entrée"])
    )

    lignes = []

    # Informations pour la réglette alphabétique
    lignes.append(
        generer_indicateurs_lettres(entrees)
    )

    lignes.append("")

    lettres_presentes = generer_liste_lettres(entrees)

    lignes = []


    # Informations destinées à LaTeX
    lignes.append(
        f"\\def\\lettersWithEntries{{{lettres_presentes}}}\n"
    )

    lignes.append(
        "% ==================================================\n"
    )

    lettre_actuelle = None

    for ligne in entrees:

        lettre = premiere_lettre(
            ligne["entrée"]
        )

        # ----------------------------------------------------
        # Changement de lettre
        # ----------------------------------------------------

        if lettre != lettre_actuelle:

            if lettre_actuelle is not None:
                lignes.append(fin_section())

            lignes.append(debut_section(lettre))

            # Marque utilisée par la réglette alphabétique
            lignes.append(
                f"\\extramarks{{{lettre}}}{{{lettre}}}\n"
            )

            lettre_actuelle = lettre

        # ----------------------------------------------------
        # Entrée
        # ----------------------------------------------------

        lignes.append(
            generer_entry(ligne)
        )

        # Espace vertical entre les entrées
        lignes.append("\n")
        lignes.append("\n")

    # --------------------------------------------------------
    # Fermer la dernière section
    # --------------------------------------------------------

    if lettre_actuelle is not None:
        lignes.append(
            fin_section()
        )

    return "".join(lignes)


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    entrees = lire_csv()

    print(
        f"{len(entrees)} entrée(s) sélectionnée(s)."
    )

    texte_latex = generer_latex(entrees)

    TEX_SORTIE.write_text(
        texte_latex,
        encoding="utf-8"
    )

    print(
        f"Fichier généré : {TEX_SORTIE}"
    )


if __name__ == "__main__":
    main()
