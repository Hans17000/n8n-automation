"""
to_prestashop.py — Convertisseur CSV Matterhorn → PrestaShop 8 import
Usage:
    python to_prestashop.py <fichier_source.csv> [fichier_sortie.csv] [--coef 2.0] [--taxe 1]

Arguments:
    fichier_source  : CSV _net ou _net_enrichi (séparateur ;)
    fichier_sortie  : optionnel, défaut = <source>_prestashop_import.csv
    --coef          : coefficient multiplicateur prix (défaut 2.0 = marge 50%)
    --taxe          : Tax rules ID PrestaShop (défaut 1 = TVA 20% France)

Colonnes source attendues (format Matterhorn _net) :
    id, name, color, description, category, boutique_category (optionnel),
    wholesale_price, sizes_stock, sizes_sku_codes, image_1..4, brand

Colonnes PS8 générées :
    ID; Active (0/1); Name *[fr-FR]; Categories (x,y,z,...); Price tax excl.;
    Tax rules ID; Wholesale price; Reference #; Short description[fr-FR];
    Description[fr-FR]; URL rewritten[fr-FR]; Image URLs (x,y,z,...);
    Attribute (Name:Type:Position)*; Value (Value:Position)*;
    Combination Reference; Quantity; Supplier reference
"""

import sys
import re
import unicodedata
import csv
import os


# ── Paramètres par défaut ──────────────────────────────────────────────────────
DEFAULT_COEF   = 2.0   # wholesale × coef = prix catalogue HT
DEFAULT_TAX_ID = 1     # ID règle TVA PS (1 = TVA normale France 20%)
SHORT_DESC_LEN = 500   # longueur max description courte


# ── Helpers ───────────────────────────────────────────────────────────────────

def slugify(text):
    """Transforme un titre en slug URL (minuscules, tirets, sans accents)."""
    text = str(text).lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:120]


def short_desc(text, length=SHORT_DESC_LEN):
    """Extrait une description courte propre (sans HTML, tronquée)."""
    if not isinstance(text, str):
        return ''
    t = re.sub(r'<[^>]+>', ' ', text)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > length:
        t = t[:length].rsplit(' ', 1)[0] + '…'
    return t


def parse_sizes_stock(sizes_stock_str):
    """
    Parse 'EU 36 | FR 38:1,EU 38 | FR 40:2' →
    [{'label': 'EU 36 | FR 38', 'qty': 1}, ...]
    """
    sizes = []
    if not isinstance(sizes_stock_str, str) or not sizes_stock_str.strip():
        return sizes
    for entry in sizes_stock_str.split(','):
        entry = entry.strip()
        if ':' not in entry:
            continue
        label, qty_str = entry.rsplit(':', 1)
        try:
            qty = int(qty_str.strip())
        except ValueError:
            qty = 0
        sizes.append({'label': label.strip(), 'qty': qty})
    return sizes


def parse_sizes_sku(sizes_sku_str):
    """
    Parse 'EU 36 | FR 38:M123,EU 38 | FR 40:M124' →
    {'EU 36 | FR 38': 'M123', 'EU 38 | FR 40': 'M124'}
    """
    skus = {}
    if not isinstance(sizes_sku_str, str) or not sizes_sku_str.strip():
        return skus
    for entry in sizes_sku_str.split(','):
        entry = entry.strip()
        if ':' not in entry:
            continue
        label, sku = entry.rsplit(':', 1)
        skus[label.strip()] = sku.strip()
    return skus


def build_image_urls(row):
    """Concatène image_1 à image_4 en liste séparée par virgules."""
    imgs = []
    for col in ['image_1', 'image_2', 'image_3', 'image_4']:
        v = row.get(col, '').strip()
        if v:
            imgs.append(v)
    return ','.join(imgs)


def get_category(row):
    """Utilise boutique_category si disponible et mappé, sinon category fournisseur."""
    bc = row.get('boutique_category', '').strip()
    if bc and bc not in ('', '❌ non mappé', '⚠️ à vérifier', '—'):
        return bc
    return row.get('category', '').strip()


def compute_price(wholesale_str, coef):
    """Calcule le prix catalogue HT arrondi à 2 décimales."""
    try:
        w = float(wholesale_str.replace(',', '.'))
        return round(w * coef, 2)
    except (ValueError, AttributeError):
        return ''


# ── Convertisseur principal ───────────────────────────────────────────────────

PS_HEADER = [
    'ID',
    'Active (0/1)',
    'Name *[fr-FR]',
    'Categories (x,y,z,...)',
    'Price tax excl.',
    'Tax rules ID',
    'Wholesale price',
    'Reference #',
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


def convert(source_path, output_path, coef=DEFAULT_COEF, tax_id=DEFAULT_TAX_ID):
    print(f"\n📂 Source  : {source_path}")
    print(f"📄 Sortie  : {output_path}")
    print(f"💰 Coef prix : ×{coef}  |  Tax ID : {tax_id}\n")

    rows_in  = 0
    rows_out = 0
    skipped  = 0

    with open(source_path, 'r', encoding='utf-8-sig') as fin, \
         open(output_path, 'w', encoding='utf-8-sig', newline='') as fout:

        reader = csv.DictReader(fin, delimiter=';')
        writer = csv.writer(fout, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(PS_HEADER)

        for row in reader:
            rows_in += 1

            product_id   = row.get('id', '').strip()
            name         = row.get('name', '').strip()
            description  = row.get('description', '').strip()
            wholesale    = row.get('wholesale_price', '').strip()
            sizes_stock  = row.get('sizes_stock', '').strip()
            sizes_sku    = row.get('sizes_sku_codes', '').strip()

            if not product_id or not name:
                skipped += 1
                continue

            category  = get_category(row)
            price     = compute_price(wholesale, coef)
            url       = slugify(name) + '-' + product_id
            images    = build_image_urls(row)
            reference = f"PDF-{product_id}"
            sdesc     = short_desc(description)

            sizes = parse_sizes_stock(sizes_stock)
            skus  = parse_sizes_sku(sizes_sku)

            if not sizes:
                # Produit sans taille (ex: accessoire taille unique)
                sizes = [{'label': 'Taille unique', 'qty': 1}]

            for i, size in enumerate(sizes):
                label    = size['label']
                qty      = size['qty']
                sku      = skus.get(label, reference + f'-{i}')
                position = i

                if i == 0:
                    # Ligne produit principale
                    writer.writerow([
                        '',            # ID (vide = nouveau produit)
                        1,             # Active
                        name,
                        category,
                        price,
                        tax_id,
                        wholesale,
                        reference,
                        sdesc,
                        description,
                        url,
                        images,
                        'Taille:select:0',
                        f'{label}:{position}',
                        sku,
                        qty,
                        sku,
                    ])
                else:
                    # Ligne déclinaison (la plupart des colonnes vides)
                    writer.writerow([
                        '',            # ID
                        '',            # Active
                        name,          # Nom répété (requis PS)
                        '',            # Category vide
                        '',            # Price vide
                        '',            # Tax vide
                        '',            # Wholesale vide
                        reference,     # Reference # (même)
                        '',            # Short desc vide
                        '',            # Description vide
                        '',            # URL vide
                        '',            # Images vides
                        'Taille:select:0',
                        f'{label}:{position}',
                        sku,
                        qty,
                        sku,
                    ])
                rows_out += 1

    print(f"✅ Produits lus    : {rows_in}")
    print(f"⚠️  Lignes ignorées : {skipped}")
    print(f"📝 Lignes générées : {rows_out}")
    print(f"\n→ Fichier prêt : {output_path}")


# ── Entrée CLI ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    source = args[0]
    coef   = DEFAULT_COEF
    tax_id = DEFAULT_TAX_ID

    # Parsing options simples
    filtered = []
    i = 0
    while i < len(args):
        if args[i] == '--coef' and i + 1 < len(args):
            coef = float(args[i + 1])
            i += 2
        elif args[i] == '--taxe' and i + 1 < len(args):
            tax_id = int(args[i + 1])
            i += 2
        else:
            filtered.append(args[i])
            i += 1

    source = filtered[0]
    if len(filtered) > 1:
        output = filtered[1]
    else:
        base, _ = os.path.splitext(source)
        # Remplace suffixe _net_enrichi ou _net par _prestashop_import
        base = re.sub(r'(_net_enrichi|_net|_nettoyes)$', '', base)
        output = base + '_prestashop_import.csv'

    if not os.path.exists(source):
        print(f"ERREUR : fichier introuvable → {source}")
        sys.exit(1)

    convert(source, output, coef=coef, tax_id=tax_id)
