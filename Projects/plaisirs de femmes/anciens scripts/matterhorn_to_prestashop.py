#!/usr/bin/env python3
"""
matterhorn_to_prestashop.py — Import XML Matterhorn → CSV PrestaShop 8
=====================================================================
Remplace l'ancienne chaîne extract_xml.py → netoyage.py → to_prestashop.py
en un seul script qui lit directement le flux XML v2 de Matterhorn.

Usage:
    python matterhorn_to_prestashop.py <fichier.xml> [sortie.csv] [--coef 2.0] [--taxe 1]

Options:
    --coef   Coefficient multiplicateur sur le prix wholesale (défaut 2.0 = marge 50%)
    --taxe   Tax rules ID PrestaShop (défaut 1 = TVA 20% France)
    --filtre Filtre catégorie : ne garde que les produits dont category_path contient ce texte
             Ex: --filtre "Lingerie" ou --filtre "Sacs et Accessoires"

Flux XML attendu (format Matterhorn v2, juin 2026):
    <product id="...">
        <name>, <brand>, <category_path>, <category id="...">,
        <color>, <type>, <price>, <description>,
        <images>/<image_url>, <options>/<option> (option_name, STOCK, ean, avaible_in)
    </product>
"""

import xml.etree.ElementTree as ET
import csv
import sys
import os
import re
import unicodedata


# ── Paramètres par défaut ─────────────────────────────────────────────────────
DEFAULT_COEF   = 2.2
DEFAULT_TAX_ID = 1
SHORT_DESC_LEN = 500
REF_PREFIX     = "PDF"  # Plaisirs De Femmes


# ── Mapping catégories Matterhorn → PrestaShop ────────────────────────────────
# Clé = fragment du category_path Matterhorn
# Valeur = chemin catégorie PrestaShop (séparateur > pour import PS)
# À compléter au fur et à mesure avec les catégories du fichier 86 Mo

CATEGORY_MAP = {
    # ─── Corps & Désirs (ID 3) — Lingerie classique ──────────────────────
    "Soutiens-Gorge Push Up":       "Accueil->Corps & Désirs->Soutiens-Gorge Galbe",
    "Soutiens-Gorge Balconnet":     "Accueil->Corps & Désirs->Soutiens-Gorge Décolleté",
    "Soutiens-Gorge Soft et Semi-Soft": "Accueil->Corps & Désirs->Soutiens-Gorge Douceur",
    "Corsets et Bodys Femme":       "Accueil->Corps & Désirs->Bodys de Soie",
    "Culottes":                     "Accueil->Corps & Désirs->Dessous Précieux",
    "Strings":                      "Accueil->Corps & Désirs->Dentelles Effilées",
    "Shortys, Boxers Femme":        "Accueil->Corps & Désirs->Shortys de Charme",
    "les bretelles":                "Accueil->Corps & Désirs->Corps & Velours",
    # ─── Fils de Soie (ID 51) ────────────────────────────────────────────
    "Collants, Bas":                "Accueil->Fils de Soie->Bas & Collants de Soie",
    "Gants":                        "Accueil->Fils de Soie->Gants d'Élégance",
    # ─── L'Heure Bleue (ID 13) ──────────────────────────────────────────
    "Nuisettes, Chemises de Nuit":  "Accueil->L'Heure Bleue->Nuits de Dentelle",
    "Pyjamas, Ensembles de Nuit":   "Accueil->L'Heure Bleue->Nuits Sereines",
    "Peignoirs, Robes de Chambre et Kimonos": "Accueil->L'Heure Bleue->Matins de Soie",
    # ─── Architecture Intime (ID 19) ────────────────────────────────────
    "Culottes, Shortys et Strings Amincissants": "Accueil->Architecture Intime->Affinements Secrets",
    "Corsets, Body Femme, Ceintures Modelantes et Gainantes": "Accueil->Architecture Intime->Silhouettes Architecturées",
    # ─── L'Impudence (ID 54) ────────────────────────────────────────────
    "Ensembles Sexy":               "Accueil->L'Impudence->Objets du Désir",
    "Bodys, Caracos, Porte-Jarreteles, Corsets, Cullotes Sexy Et Leggins": "Accueil->L'Impudence->Objets du Désir",
    "Guêpières, Bustiers, Nuisettes et Babydolls": "Accueil->L'Impudence->Objets du Désir",
    # ─── La Garde-Robe (ID 24) ──────────────────────────────────────────
    "Maillots de Bain 1 Pièce":     "Accueil->La Garde-Robe->Balnéaire Une Pièce",
    "Maillots de Bain 2 Pièces":    "Accueil->La Garde-Robe->Balnéaire Deux Pièces",
    "Robes de Plage, Paréos":       "Accueil->La Garde-Robe->Échappées Balnéaires",
    "Bonnets et chapeaux":          "Accueil->La Garde-Robe->Coiffures d'Été",
    "Foulards et Écharpes":         "Accueil->La Garde-Robe->Soieries & Foulards",
    "Robes de Jour":                "Accueil->La Garde-Robe->Robes du Jour",
    "Robes de Soirée":              "Accueil->La Garde-Robe->Robes du Soir",
    "Robes de cocktail, Robes formelles": "Accueil->La Garde-Robe->Robes de Cérémonie",
    "Combinaisons Femme":           "Accueil->La Garde-Robe->Combinaisons d'Allure",
    "Jupes":                        "Accueil->La Garde-Robe->Jupes de Caractère",
    "Blouses Femme, Tuniques":      "Accueil->La Garde-Robe->Blouses & Tuniques",
    "Chemises Femme":               "Accueil->La Garde-Robe->Chemises d'Auteur",
    "Tops Femme, T-shirts, Débardeurs Femme": "Accueil->La Garde-Robe->Tops & Essentiels",
    "Maillots de Corps / Tops":     "Accueil->La Garde-Robe->Hauts Décontractés",
    "Bodys Femme":                  "Accueil->La Garde-Robe->Tops & Essentiels",
    "Leggings Femme":               "Accueil->La Garde-Robe->Leggings de Caractère",
    "Pantalons femme, Shorts femme": "Accueil->La Garde-Robe->Pantalons & Shorts",
    "Pantalons longs":              "Accueil->La Garde-Robe->Pantalons de Coupe",
    "Pantalons élégants":           "Accueil->La Garde-Robe->Pantalons d'Apparat",
    "Shorts Femme, Pantacourts, Corsaires Femme": "Accueil->La Garde-Robe->Shorts & Pantacourts",
    "Blazers femme, Gilets femme":  "Accueil->La Garde-Robe->Blazers & Gilets",
    "Vestes femme, Manteaux femme": "Accueil->La Garde-Robe->Vestes & Manteaux",
    "Sweats et sweat-shirts femme": "Accueil->La Garde-Robe->Sweats & Molletons",
    "Pulls, Chandails, Pullovers, PULLS a COL ROULÉ FEMME ET BOLEROS FEMME": "Accueil->La Garde-Robe->Tricots & Cols Roulés",
    "Cardigans Femme, Ponchos":     "Accueil->La Garde-Robe->Cardigans & Ponchos",
    "L`ensemble grandes tailles":   "Accueil->La Garde-Robe->Mises en Scène",
    # ─── Toutes les Grâces (ID 56) ──────────────────────────────────────
    "Soutiens-Gorge Allaitement, Grossesse et Maternité": "Accueil->Toutes les Grâces->Soutiens-Gorge Maternité",
    "Robes de grossesse":           "Accueil->Toutes les Grâces->Robes de la Belle Attente",
    "Pantalon grossesse":           "Accueil->Toutes les Grâces->Pantalons de la Belle Attente",
    "Blouses de maternité":         "Accueil->Toutes les Grâces->Blouses de Maternité",
    "Legging grossesse":            "Accueil->Toutes les Grâces->Leggings de Maternité",
    "Tunique grossesse":            "Accueil->Toutes les Grâces->Tuniques de Maternité",
    "Robes taille plus":            "Accueil->Toutes les Grâces->Robes de Grâce",
    "Chemises, Chemisiers, Tuniques grande taille": "Accueil->Toutes les Grâces->Chemises & Tuniques Grande Taille",
    "Pulls, Cardigans Femme Grandes Tailles": "Accueil->Toutes les Grâces->Tricots Grande Taille",
    "T-shrits grandes tailles":     "Accueil->Toutes les Grâces->Hauts Essentiels Grande Taille",
    "Sweatshirts taille plus":      "Accueil->Toutes les Grâces->Molletons Grande Taille",
    # ─── Chaussures (nouvel univers) ─────────────────────────────────────
    "Bottes et boots":              "Accueil->Chaussures->Bottes & Boots",
    "Bottes, Cuissardes":           "Accueil->Chaussures->Cuissardes",
    "Sandales et mules":            "Accueil->Chaussures->Sandales & Mules",
    "Chausseres de sport":          "Accueil->Chaussures->Sneakers",
    "Mocassins, Lords":             "Accueil->Chaussures->Mocassins & Lords",
    "Ballerines":                   "Accueil->Chaussures->Ballerines",
    "Chaussons":                    "Accueil->Chaussures->Chaussons",
    "Escarpins":                    "Accueil->Chaussures->Escarpins",
    "Talons aiguilles":             "Accueil->Chaussures->Talons Aiguilles",
    "Escarpins à talons bloc":      "Accueil->Chaussures->Talons Bloc",
    # ─── Variantes encodage/nommage (accents corrompus dans le XML) ──────
    "Escarpins à talons bloc":      "Accueil->Chaussures->Talons Bloc",
    "Guêpières, Bustiers, Nuisettes et Babydolls": "Accueil->L'Impudence->Objets du Désir",
    "Maillots de Bain 1 Pièce":     "Accueil->La Garde-Robe->Balnéaire Une Pièce",
    "Maillots de Bain 2 Pièces":    "Accueil->La Garde-Robe->Balnéaire Deux Pièces",
    "Pantalons de survêtement femme": "Accueil->La Garde-Robe->Pantalons de Détente",
    "Vêtements et Lingerie de Nuit": "Accueil->L'Heure Bleue->Voiles de Nuit",
    "Chemises Femme, Blouses Femme": "Accueil->La Garde-Robe->Blouses & Tuniques",
    "Cullotes ew.cullotes et bas":  "Accueil->Corps & Désirs->Dessous Précieux",
    "Lingerie":                     "Accueil->Corps & Désirs->Parures d'Exception",
    "Lingerie Sexy, Lingerie Érotique": "Accueil->L'Impudence->Objets du Désir",
    "Tenues Maternite":             "Accueil->Toutes les Grâces->Robes de la Belle Attente",
    "Tops":                         "Accueil->La Garde-Robe->Tops & Essentiels",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def slugify(text):
    """Titre → slug URL (minuscules, tirets, sans accents)."""
    text = str(text).lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:120]


def extract_prose(html):
    """Extrait la description texte, sans le bloc composition matières."""
    if not html:
        return ''
    # Coupe avant le div prod_data (composition)
    html = re.split(r"<div class=['\"]prod_data", html, 1)[0]
    html = re.split(r"<table", html, 1)[0]
    # Nettoie le HTML résiduel
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_composition(html):
    """Extrait la composition matières du bloc prod_data."""
    if not html:
        return ''
    match = re.search(r"<div class=['\"]prod_data['\"]>(.*?)</div>", html, re.DOTALL)
    if not match:
        return ''
    bloc = match.group(1)
    # Parse les paires matière/pourcentage
    pairs = re.findall(r'<strong>(.*?)</strong>\s*([\d]+\s*%)', bloc)
    if pairs:
        return ', '.join(f"{mat.strip()} {pct.strip()}" for mat, pct in pairs)
    return ''


def short_desc(text, length=SHORT_DESC_LEN):
    """Tronque proprement une description."""
    if not text:
        return ''
    if len(text) > length:
        text = text[:length].rsplit(' ', 1)[0] + '…'
    return text


def _normalize(text):
    """Supprime les accents pour comparaison floue."""
    text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn').lower().strip()

_CATEGORY_MAP_NORM = {_normalize(k): v for k, v in CATEGORY_MAP.items()}

def map_category(category_path):
    """Mappe un category_path Matterhorn vers la catégorie PrestaShop."""
    if not category_path:
        return ''
    leaf = category_path.rstrip('/').split('/')[-1].strip()
    # Match exact
    if leaf in CATEGORY_MAP:
        return CATEGORY_MAP[leaf]
    # Fallback sans accents
    norm = _normalize(leaf)
    if norm in _CATEGORY_MAP_NORM:
        return _CATEGORY_MAP_NORM[norm]
    # Dernier recours : chemin brut
    parts = [p.strip() for p in category_path.strip('/').split('/') if p.strip()]
    return 'Accueil->' + '->'.join(parts)


def compute_price(price_str, coef):
    """Prix wholesale × coef = prix catalogue HT."""
    try:
        return round(float(price_str.replace(',', '.')) * coef, 2)
    except (ValueError, AttributeError):
        return ''


# ── En-tête CSV PrestaShop 8 ─────────────────────────────────────────────────

PS_HEADER = [
    'ID',
    'Active (0/1)',
    'Name *[fr-FR]',
    'Categories (x,y,z,...)',
    'Price tax excl.',
    'Tax rules ID',
    'Wholesale price',
    'Reference #',
    'EAN13',
    'Brand',
    'Short description[fr-FR]',
    'Description[fr-FR]',
    'URL rewritten[fr-FR]',
    'Image URLs (x,y,z,...)',
    'Attribute (Name:Type:Position)*',
    'Value (Value:Position)*',
    'Combination Reference',
    'Quantity',
    'Supplier reference',
]


# ── Convertisseur principal ──────────────────────────────────────────────────

def convert(xml_path, csv_path, coef=DEFAULT_COEF, tax_id=DEFAULT_TAX_ID, filtre=None):
    print(f"\n📂 Source XML : {xml_path}")
    print(f"📄 Sortie CSV : {csv_path}")
    print(f"💰 Coef prix  : ×{coef}  |  Tax ID : {tax_id}")
    if filtre:
        print(f"🔍 Filtre     : {filtre}")

    stats = {'total': 0, 'exportes': 0, 'filtres': 0, 'sans_desc': 0, 'lignes': 0}
    categories_vues = set()

    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as fout:
        writer = csv.writer(fout, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(PS_HEADER)

        for _, elem in ET.iterparse(xml_path, events=('end',)):
            if elem.tag != 'product':
                continue

            stats['total'] += 1
            pid = elem.get('id', '').strip()
            if not pid:
                elem.clear()
                continue

            # Extraction des champs
            name          = (elem.findtext('name') or '').strip()
            brand         = (elem.findtext('brand') or '').strip()
            category_path = (elem.findtext('category_path') or '').strip()
            color         = (elem.findtext('color') or '').strip()
            prod_type     = (elem.findtext('type') or '').strip()
            price_raw     = (elem.findtext('price') or '').strip()
            desc_raw      = (elem.findtext('description') or '').strip()

            # Filtre catégorie si demandé
            if filtre and filtre.lower() not in category_path.lower():
                stats['filtres'] += 1
                elem.clear()
                continue

            categories_vues.add(category_path)

            # Traitement
            description  = extract_prose(desc_raw)
            composition  = extract_composition(desc_raw)
            if composition:
                description += f"\n\nComposition : {composition}"

            sdesc        = short_desc(extract_prose(desc_raw))
            price        = compute_price(price_raw, coef)
            category     = map_category(category_path)
            reference    = f"{REF_PREFIX}-{pid}"
            url          = slugify(f"{prod_type} {brand} {color} {pid}")

            if not description:
                stats['sans_desc'] += 1

            # Images
            images = []
            for img in elem.findall('.//image_url'):
                u = (img.text or '').strip()
                if u:
                    images.append(u)
            images_str = ','.join(images)

            # Options (tailles / stock / EAN)
            options = elem.findall('.//option')
            if not options:
                # Produit sans option = taille unique
                options_data = [{'label': 'Taille unique', 'qty': 0, 'ean': '', 'sku': reference}]
            else:
                options_data = []
                for opt in options:
                    opt_id    = opt.get('id', '')
                    opt_label = (opt.findtext('option_name') or 'Taille unique').strip()
                    opt_stock = int(opt.findtext('STOCK') or '0')
                    opt_ean   = (opt.findtext('ean') or '').strip()
                    options_data.append({
                        'label': opt_label,
                        'qty':   opt_stock,
                        'ean':   opt_ean,
                        'sku':   opt_id or f"{reference}-{len(options_data)}",
                    })

            # Écriture des lignes CSV
            for i, opt in enumerate(options_data):
                if i == 0:
                    # Ligne produit principale
                    writer.writerow([
                        '',                          # ID (vide = nouveau)
                        1,                           # Active
                        name,                        # Name
                        category,                    # Categories
                        price,                       # Price tax excl.
                        tax_id,                      # Tax rules ID
                        price_raw,                   # Wholesale price
                        reference,                   # Reference #
                        opt['ean'],                  # EAN13
                        brand,                       # Brand
                        sdesc,                       # Short description
                        description,                 # Description
                        url,                         # URL rewritten
                        images_str,                  # Image URLs
                        'Taille',           # Attribute
                        f"{opt['label']}:{i}",       # Value
                        opt['sku'],                  # Combination Reference
                        opt['qty'],                  # Quantity
                        opt['sku'],                  # Supplier reference
                    ])
                else:
                    # Ligne déclinaison
                    writer.writerow([
                        '',                          # ID
                        '',                          # Active
                        name,                        # Name (requis PS)
                        '',                          # Categories
                        '',                          # Price
                        '',                          # Tax
                        '',                          # Wholesale
                        reference,                   # Reference #
                        opt['ean'],                  # EAN13
                        '',                          # Brand
                        '',                          # Short desc
                        '',                          # Description
                        '',                          # URL
                        '',                          # Images
                        'Taille',           # Attribute
                        f"{opt['label']}:{i}",       # Value
                        opt['sku'],                  # Combination Reference
                        opt['qty'],                  # Quantity
                        opt['sku'],                  # Supplier reference
                    ])
                stats['lignes'] += 1

            stats['exportes'] += 1
            elem.clear()

    # Rapport
    print(f"\n{'='*50}")
    print(f"✅ Produits traités  : {stats['total']}")
    if filtre:
        print(f"🔍 Filtrés (exclus)  : {stats['filtres']}")
    print(f"📦 Produits exportés : {stats['exportes']}")
    print(f"📝 Lignes CSV        : {stats['lignes']}")
    print(f"⚠️  Sans description  : {stats['sans_desc']}")
    print(f"\n📂 Catégories trouvées :")
    for c in sorted(categories_vues):
        print(f"   {c}")
    print(f"\n→ Fichier prêt : {csv_path}")

    return stats


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    coef    = DEFAULT_COEF
    tax_id  = DEFAULT_TAX_ID
    filtre  = None
    positional = []

    i = 0
    while i < len(args):
        if args[i] == '--coef' and i + 1 < len(args):
            coef = float(args[i + 1]); i += 2
        elif args[i] == '--taxe' and i + 1 < len(args):
            tax_id = int(args[i + 1]); i += 2
        elif args[i] == '--filtre' and i + 1 < len(args):
            filtre = args[i + 1]; i += 2
        else:
            positional.append(args[i]); i += 1

    source = positional[0]
    if len(positional) > 1:
        output = positional[1]
    else:
        base, _ = os.path.splitext(source)
        output = base + '_prestashop_import.csv'

    if not os.path.exists(source):
        print(f"ERREUR : fichier introuvable → {source}")
        sys.exit(1)

    convert(source, output, coef=coef, tax_id=tax_id, filtre=filtre)
