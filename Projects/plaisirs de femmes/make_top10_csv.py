#!/usr/bin/env python3
"""
make_top10_csv.py — Génère top10_import.csv à partir du CSV Matterhorn complet
Usage :
    python3 make_top10_csv.py \
        --src prestashop_products_sizesFR.csv \
        --dst top10_import.csv

Le CSV produit est directement lisible par plaisirs_sync.py :
    python3 plaisirs_sync.py --source top10_import.csv --output db --top 0 ...
"""

import csv
import argparse
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
#  TOP 10 — IDs Matterhorn → clé CATEGORY_MAP texte
#  La clé doit correspondre exactement à une entrée du CATEGORY_MAP du script
# ═══════════════════════════════════════════════════════════════════════════════
TOP10 = {
    # Cat 1 — Strings & Tangas → Lingerie Intime → Corps & Désirs
    '227532': 'Strings', '217428': 'Strings', '219480': 'Strings',
    '221476': 'Strings', '219481': 'Strings', '225187': 'Strings',
    '222578': 'Strings', '226371': 'Strings', '226377': 'Strings',
    '179216': 'Strings',
    # Cat 2 — Soutiens-Gorge → Lingerie Intime → Soutiens-Gorge & Parures
    '203243': 'Soutiens-Gorge Push Up', '227481': 'Soutiens-Gorge Push Up',
    '227504': 'Soutiens-Gorge Push Up', '227960': 'Soutiens-Gorge Push Up',
    '198762': 'Soutiens-Gorge Balconnet', '206638': 'Soutiens-Gorge Balconnet',
    '206639': 'Soutiens-Gorge Balconnet', '201074': 'Soutiens-Gorge Balconnet',
    '213658': 'Soutiens-Gorge Soft et Semi-Soft', '208965': 'Soutiens-Gorge Soft et Semi-Soft',
    # Cat 3 — Bodies & Bustiers → Lingerie Intime → Corsets & Architecture
    '149949': 'Corsets et Bodys Femme', '144174': 'Corsets et Bodys Femme',
    '182304': 'Corsets et Bodys Femme', '188964': 'Corsets et Bodys Femme',
    '188965': 'Corsets et Bodys Femme', '169973': 'Corsets et Bodys Femme',
    '184827': 'Corsets et Bodys Femme', '172363': 'Corsets et Bodys Femme',
    '145215': 'Corsets et Bodys Femme', '200807': 'Corsets et Bodys Femme',
    # Cat 4 — Corsets & Ensembles Sexy → Lingerie Intime → Corsets & Architecture
    '161758': 'Ensembles Sexy', '158920': 'Ensembles Sexy',
    '195250': 'Guêpières, Bustiers, Nuisettes et Babydolls',
    '195251': 'Guêpières, Bustiers, Nuisettes et Babydolls',
    '195252': 'Guêpières, Bustiers, Nuisettes et Babydolls',
    '206259': 'Ensembles Sexy', '206207': 'Ensembles Sexy',
    '206273': 'Ensembles Sexy', '206218': 'Ensembles Sexy',
    '145572': 'Guêpières, Bustiers, Nuisettes et Babydolls',
    # Cat 5 — Nuisettes & Déshabillés → Nuits & Désirs → Nuisettes & Déshabillés
    '152079': 'Nuisettes, Chemises de Nuit', '199374': 'Nuisettes, Chemises de Nuit',
    '154833': 'Nuisettes, Chemises de Nuit', '182944': 'Nuisettes, Chemises de Nuit',
    '183055': 'Nuisettes, Chemises de Nuit', '182945': 'Nuisettes, Chemises de Nuit',
    '157931': 'Peignoirs, Robes de Chambre et Kimonos',
    '228498': 'Peignoirs, Robes de Chambre et Kimonos',
    '219070': 'Peignoirs, Robes de Chambre et Kimonos',
    '206258': 'Peignoirs, Robes de Chambre et Kimonos',
    # Cat 6 — Pyjamas & Loungewear → Nuits & Désirs → Pyjamas & Loungewear
    '223027': 'Pyjamas, Ensembles de Nuit', '187096': 'Pyjamas, Ensembles de Nuit',
    '196109': 'Pyjamas, Ensembles de Nuit', '196111': 'Pyjamas, Ensembles de Nuit',
    '196112': 'Pyjamas, Ensembles de Nuit', '187521': 'Pyjamas, Ensembles de Nuit',
    '213326': 'Pyjamas, Ensembles de Nuit', '184831': 'Pyjamas, Ensembles de Nuit',
    '221470': 'Pyjamas, Ensembles de Nuit', '169495': 'Pyjamas, Ensembles de Nuit',
    # Cat 7 — Culottes & Shortys → Lingerie Intime → Corps & Désirs
    '174575': 'Culottes', '222340': 'Culottes', '222341': 'Culottes',
    '216104': 'Culottes', '198253': 'Culottes', '206641': 'Culottes',
    '212647': 'Culottes', '228908': 'Shortys, Boxers Femme',
    '226738': 'Shortys, Boxers Femme', '174576': 'Culottes',
    # Cat 8 — Bas & Collants → Style & Silhouette → Bas & Collants
    '34375': 'Collants, Bas', '112522': 'Collants, Bas', '206162': 'Collants, Bas',
    '220367': 'Collants, Bas', '150285': 'Collants, Bas', '162774': 'Collants, Bas',
    '140510': 'Collants, Bas', '150276': 'Collants, Bas',
    '206324': 'Collants, Bas', '143715': 'Collants, Bas',
    # Cat 9 — Robes & Tenues → Style & Silhouette → Robes & Tenues
    '184600': 'Robes de Jour', '187964': 'Robes de Jour',
    '184598': 'Robes de Jour', '184599': 'Robes de Jour',
    '177888': 'Robes de Soirée', '179047': 'Robes de Soirée',
    '190992': 'Robes de Soirée', '152837': 'Robes de cocktail, Robes formelles',
    '179048': 'Robes de Soirée', '190993': 'Robes de Soirée',
}

FIELDNAMES = [
    'id', 'name', 'brand', 'category_path',
    'wholesale_price', 'description',
    'image_1', 'image_2', 'image_3', 'image_4',
]


def build(src: str, dst: str) -> int:
    found: dict = {}
    with open(src, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f, delimiter=';'):
            pid = row.get('ID', '').strip()
            if pid in TOP10:
                found[pid] = row

    missing = set(TOP10) - set(found)
    if missing:
        print(f"[WARN] {len(missing)} IDs introuvables : {sorted(missing)}")

    rows_out = []
    for pid, row in found.items():
        imgs = [u.strip() for u in row.get('Image URLs (x,y,z...)', '').split(',') if u.strip()]
        imgs += ['', '', '', '']
        rows_out.append({
            'id':              pid,
            'name':            (row.get('Name *') or '').strip(),
            'brand':           (row.get('Manufacturer') or '').strip(),
            'category_path':   TOP10[pid],
            'wholesale_price': (row.get('Price netto') or '').strip(),
            'description':     (row.get('size_table_and_fabric_content_html') or '').strip(),
            'image_1':         imgs[0],
            'image_2':         imgs[1],
            'image_3':         imgs[2],
            'image_4':         imgs[3],
        })

    with open(dst, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter=';')
        w.writeheader()
        w.writerows(rows_out)

    return len(rows_out)


def main():
    p = argparse.ArgumentParser(description='Génère top10_import.csv depuis le CSV Matterhorn complet')
    p.add_argument('--src', default='prestashop_products_sizesFR.csv',
                   help='CSV source Matterhorn (défaut : prestashop_products_sizesFR.csv)')
    p.add_argument('--dst', default='top10_import.csv',
                   help='CSV de sortie (défaut : top10_import.csv)')
    args = p.parse_args()

    n = build(args.src, args.dst)
    print(f'[OK] {n} produits exportés → {args.dst}')
    print()
    print('Prochaine étape :')
    print(f'  python3 plaisirs_sync.py \\')
    print(f'    --source {args.dst} \\')
    print(f'    --output db \\')
    print(f'    --db-host localhost \\')
    print(f'    --db-name prestanew \\')
    print(f'    --db-user [user] \\')
    print(f'    --db-pass [pass] \\')
    print(f'    --ref-prefix PDF \\')
    print(f'    --top 0')


if __name__ == '__main__':
    main()
