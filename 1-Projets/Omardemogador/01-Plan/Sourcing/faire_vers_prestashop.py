#!/usr/bin/env python3
"""
Faire → PrestaShop : convertit l'export « Product info (.csv) » de Faire
en CSV d'import produits PrestaShop (Paramètres avancés → Import → Produits).

Usage :  python faire_vers_prestashop.py export_faire.csv [sortie.csv]
Sans dépendance externe (bibliothèque standard uniquement).

Réglages d'import côté PrestaShop : séparateur de champs « ; »,
séparateur multi-valeurs « , », encodage UTF-8.
"""

import csv
import re
import sys
import unicodedata
from pathlib import Path

# Colonnes attendues dans l'export Faire → clés internes.
# La détection est tolérante (casse, espaces, variantes EN/FR).
ALIASES = {
    "brand name": "marque", "marque": "marque", "nom de la marque": "marque",
    "product name": "nom", "nom du produit": "nom",
    "product description": "description", "description du produit": "description",
    "description": "description",
    "image url": "image", "url de l'image": "image",
    "option name": "variante", "nom de l'option": "variante",
    "sku": "sku", "gtin": "gtin",
    "quantity": "quantite", "quantite": "quantite", "quantité": "quantite",
    "wholesale price": "prix_gros", "prix de gros": "prix_gros",
    "retail price": "prix_vente", "prix de detail": "prix_vente",
    "prix de détail": "prix_vente", "prix de vente conseille": "prix_vente",
    "weight": "poids", "poids": "poids",
}

PS_HEADER = [
    "Name", "Reference", "EAN13", "Active", "Price tax excluded",
    "Wholesale price", "Tax rules ID", "Quantity", "Weight",
    "Manufacturer", "Description", "Image URLs",
]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def _prix(s: str) -> str:
    """'€12,50', '12.50 EUR' → '12.50' ; vide si illisible."""
    if not s:
        return ""
    s = s.replace(" ", " ")
    m = re.search(r"(\d+(?:[.,]\d{1,2})?)", s.replace(" ", ""))
    return m.group(1).replace(",", ".") if m else ""


def _poids(s: str) -> str:
    """'0,5 kg', '500 g' → kilogrammes en décimal."""
    if not s:
        return ""
    m = re.search(r"(\d+(?:[.,]\d+)?)", s)
    if not m:
        return ""
    val = float(m.group(1).replace(",", "."))
    if re.search(r"\bg\b|gram", s, re.I) and not re.search(r"kg", s, re.I):
        val /= 1000.0
    return f"{val:g}"


def _ean(s: str) -> str:
    chiffres = re.sub(r"\D", "", s or "")
    return chiffres if len(chiffres) in (8, 12, 13, 14) else ""


def convertir(src: Path, dst: Path) -> None:
    with src.open(newline="", encoding="utf-8-sig") as f:
        echantillon = f.read(4096)
        f.seek(0)
        try:
            dialecte = csv.Sniffer().sniff(echantillon, delimiters=",;\t")
        except csv.Error:
            dialecte = csv.excel
        lecteur = csv.DictReader(f, dialect=dialecte)
        colonnes = {c: ALIASES[_norm(c)] for c in (lecteur.fieldnames or [])
                    if _norm(c) in ALIASES}
        if "nom" not in colonnes.values():
            sys.exit("Colonne « Product name » introuvable — est-ce bien "
                     "l'export Product info (.csv) de Faire ?")

        produits: dict[str, dict] = {}
        for ligne in lecteur:
            d = {v: (ligne.get(k) or "").strip() for k, v in colonnes.items()}
            nom = d.get("nom", "")
            if not nom:
                continue
            if d.get("variante") and _norm(d["variante"]) not in ("", "default"):
                nom = f"{nom} — {d['variante']}"
            cle = d.get("sku") or nom
            if cle in produits:  # même réf. sur plusieurs commandes → cumul qté
                try:
                    produits[cle]["Quantity"] = str(
                        int(produits[cle]["Quantity"] or 0) + int(d.get("quantite") or 0))
                except ValueError:
                    pass
                continue
            produits[cle] = {
                "Name": nom,
                "Reference": d.get("sku", ""),
                "EAN13": _ean(d.get("gtin", "")),
                "Active": "0",  # créé désactivé : relecture Voix de Mogador d'abord
                "Price tax excluded": _prix(d.get("prix_vente", "")),
                "Wholesale price": _prix(d.get("prix_gros", "")),
                "Tax rules ID": "0",  # TVA non applicable, art. 293 B du CGI
                "Quantity": d.get("quantite") or "0",
                "Weight": _poids(d.get("poids", "")),
                "Manufacturer": d.get("marque", ""),
                "Description": d.get("description", ""),
                "Image URLs": d.get("image", ""),
            }

    with dst.open("w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=PS_HEADER, delimiter=";")
        ecrivain.writeheader()
        ecrivain.writerows(produits.values())
    print(f"{len(produits)} produit(s) → {dst}")
    print("Import PrestaShop : Paramètres avancés → Import → Produits, "
          "séparateur « ; ». Produits créés inactifs, prix à relire.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    source = Path(sys.argv[1])
    sortie = Path(sys.argv[2]) if len(sys.argv) > 2 else source.with_name(
        source.stem + "_prestashop.csv")
    convertir(source, sortie)
