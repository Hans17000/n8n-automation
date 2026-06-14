"""
top10_par_categorie.py — Sélection Top 10 bestsellers par catégorie boutique
=============================================================================
Logique bestseller (proxy Matterhorn) :
  score = nb de tailles en stock  +  5 pts si produit < 365 jours  +  3 pts si 4 images

Usage :
  python top10_par_categorie.py <fichier.csv> [--top 10] [--out selection.csv]

  Fichiers acceptés : lingerie_net_enrichi.csv, vetements_net.csv, sac_net.csv
  (tout CSV avec colonnes : id, boutique_category ou category, sizes_stock, date_add)

Sortie :
  - <nom>_top10.csv  : produits sélectionnés au format source (prêt pour to_prestashop.py)
  - Rapport console  : classement par catégorie avec score
"""

import sys
import csv
import os
import re
from datetime import datetime, timedelta

# ── Paramètres ────────────────────────────────────────────────────────────────

DEFAULT_TOP    = 10
RECENCE_JOURS  = 365    # bonus si produit ajouté dans cette fenêtre
BONUS_RECENT   = 5      # points bonus produit récent
BONUS_4_IMAGES = 3      # points bonus si 4 images présentes
SEPARATEUR     = ';'


# ── Helpers ───────────────────────────────────────────────────────────────────

def count_tailles_en_stock(sizes_stock_str):
    """Compte le nombre de tailles avec stock > 0."""
    if not isinstance(sizes_stock_str, str) or not sizes_stock_str.strip():
        return 0
    count = 0
    for entry in sizes_stock_str.split(','):
        entry = entry.strip()
        if ':' not in entry:
            continue
        _, qty_str = entry.rsplit(':', 1)
        try:
            if int(qty_str.strip()) > 0:
                count += 1
        except ValueError:
            pass
    return count


def stock_total(sizes_stock_str):
    """Somme totale des stocks sur toutes les tailles."""
    if not isinstance(sizes_stock_str, str):
        return 0
    total = 0
    for entry in sizes_stock_str.split(','):
        if ':' not in entry:
            continue
        _, qty_str = entry.rsplit(':', 1)
        try:
            total += int(qty_str.strip())
        except ValueError:
            pass
    return total


def est_recent(date_str, jours=RECENCE_JOURS):
    """Retourne True si date_add est dans la fenêtre de récence."""
    if not isinstance(date_str, str) or not date_str.strip():
        return False
    try:
        d = datetime.strptime(date_str.strip()[:10], '%Y-%m-%d')
        return d >= datetime.now() - timedelta(days=jours)
    except ValueError:
        return False


def count_images(row):
    """Compte le nombre d'images renseignées."""
    return sum(1 for col in ['image_1', 'image_2', 'image_3', 'image_4']
               if row.get(col, '').strip())


def get_category(row):
    """Utilise boutique_category si disponible et valide, sinon category fournisseur."""
    bc = row.get('boutique_category', '').strip()
    if bc and bc not in ('', '❌ non mappé', '⚠️ à vérifier', '—'):
        return bc
    return row.get('category', '').strip()


def score(row):
    """Calcule le score bestseller d'un produit."""
    tailles_ok  = count_tailles_en_stock(row.get('sizes_stock', ''))
    recent      = BONUS_RECENT   if est_recent(row.get('date_add', '')) else 0
    imgs        = BONUS_4_IMAGES if count_images(row) == 4               else 0
    return tailles_ok + recent + imgs


# ── Sélection principale ──────────────────────────────────────────────────────

def selectionner(source_path, top_n=DEFAULT_TOP, output_path=None):
    print(f"\n📂 Source : {source_path}")
    print(f"🏆 Top {top_n} par catégorie\n")

    if output_path is None:
        base = re.sub(r'(_net_enrichi|_net|_nettoyes)$', '',
                      os.path.splitext(source_path)[0])
        output_path = base + f'_top{top_n}.csv'

    # Lecture
    produits = []
    with open(source_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=SEPARATEUR)
        fieldnames = reader.fieldnames
        for row in reader:
            if not row.get('id', '').strip():
                continue
            cat = get_category(row)
            if not cat:
                continue
            row['_categorie']   = cat
            row['_score']       = score(row)
            row['_stock_total'] = stock_total(row.get('sizes_stock', ''))
            produits.append(row)

    print(f"✅ {len(produits)} produits chargés")

    # Groupement par catégorie
    par_cat = {}
    for p in produits:
        cat = p['_categorie']
        par_cat.setdefault(cat, []).append(p)

    # Sélection top N par catégorie (tri : score DESC, stock_total DESC)
    selection = []
    stats = []

    for cat in sorted(par_cat.keys()):
        groupe = sorted(par_cat[cat],
                        key=lambda r: (r['_score'], r['_stock_total']),
                        reverse=True)
        top = groupe[:top_n]
        selection.extend(top)
        stats.append({
            'categorie':   cat,
            'dispo':       len(groupe),
            'selectionnes': len(top),
            'score_max':   top[0]['_score'] if top else 0,
            'score_min':   top[-1]['_score'] if top else 0,
        })

    # Rapport console
    print(f"\n{'Catégorie':<45} {'Dispo':>6} {'Sélect':>7} {'Score min-max':>14}")
    print('─' * 78)
    for s in stats:
        print(f"{s['categorie']:<45} {s['dispo']:>6} {s['selectionnes']:>7} "
              f"  {s['score_min']} – {s['score_max']}")

    total_sel = len(selection)
    print(f"\n{'─' * 78}")
    print(f"  Total sélectionné : {total_sel} produits  "
          f"({len(par_cat)} catégories × ~{top_n} max)")

    # Écriture CSV (mêmes colonnes que la source, sans les colonnes _internes)
    cols_out = [c for c in (fieldnames or []) if not c.startswith('_')]

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cols_out, delimiter=SEPARATEUR,
                                extrasaction='ignore')
        writer.writeheader()
        writer.writerows(selection)

    print(f"\n→ Fichier sélection : {output_path}\n")
    return output_path


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    source  = args[0]
    top_n   = DEFAULT_TOP
    output  = None

    i = 1
    while i < len(args):
        if args[i] == '--top' and i + 1 < len(args):
            top_n = int(args[i + 1]); i += 2
        elif args[i] == '--out' and i + 1 < len(args):
            output = args[i + 1]; i += 2
        else:
            i += 1

    if not os.path.exists(source):
        print(f"ERREUR : fichier introuvable → {source}")
        sys.exit(1)

    selectionner(source, top_n=top_n, output_path=output)
