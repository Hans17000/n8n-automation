"""
generer_catalogue.py — Pipeline catalogue unifié Matterhorn → Simple Import Product
=====================================================================================
Un seul script, une seule passe :
  1. Lecture CSV source (_net ou _net_enrichi)
  2. Sélection Top N bestsellers par catégorie (score stock + récence)
  3. Nettoyage : EAN propres (1 par déclinaison, 13 car. max), refs courtes
  4. Génération CSV prêt pour le module Simple Import Product

Usage :
  python generer_catalogue.py <source.csv> [--top 10] [--coef 2.5] [--out catalogue.csv]

Exemples :
  python generer_catalogue.py lingerie_net_enrichi.csv
  python generer_catalogue.py vetements_net.csv --top 15 --coef 2.3
  python generer_catalogue.py sac_net.csv --out sacs_catalogue.csv
"""

import sys
import csv
import os
import re
import unicodedata
from datetime import datetime, timedelta


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_TOP        = 10
DEFAULT_COEF       = 2.2     # coefficient prix : wholesale × coef = prix HT affiché
TVA                = 20      # taux TVA France (%)
PRICE_ENDING       = 0.90    # arrondi psychologique ,90
RECENCE_JOURS      = 365
BONUS_RECENT       = 5
BONUS_4_IMAGES     = 3
SEP                = ';'     # séparateur CSV sortie
MAX_REF_LEN        = 32      # longueur max référence produit
MAX_EAN_LEN        = 13      # EAN-13 standard
SHORT_DESC_LEN     = 500

NOM_BOUTIQUE = 'Plaisirs de Femmes'

# Catégories à exclure (sexshop, maternité si non souhaité, etc.)
CATS_EXCLUES = set()


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS GÉNÉRAUX
# ══════════════════════════════════════════════════════════════════════════════

# ── Traduction des types produit Matterhorn → nom boutique chic ───────────

TRADUCTION_TYPES = {
    # Lingerie — soutiens-gorge
    'push up':                      'Soutien-Gorge Push-Up',
    'soft':                         'Soutien-Gorge Souple',
    'semi-soft':                    'Soutien-Gorge Semi-Souple',
    'soutien-gorge demi-bonnet':    'Soutien-Gorge Demi-Bonnet',
    'soutien-gorge nageur':         'Soutien-Gorge Dos Nageur',
    'soutien-gorge rembourré':      'Soutien-Gorge Rembourré',
    'cupless bra':                  'Soutien-Gorge Ouvert',
    'bra':                          'Soutien-Gorge',
    # Lingerie — bas
    'strings':                      'String',
    't-backs':                      'String Ficelle',
    'thong':                        'String',
    'culottes':                     'Culotte',
    'panties':                      'Culotte',
    'briefs':                       'Culotte Gainante',
    'boxer':                        'Shorty',
    'garter belt':                  'Porte-Jarretelles',
    'ceinture':                     'Porte-Jarretelles',
    'bas':                          'Bas',
    'stockings':                    'Bas',
    'tights':                       'Collants',
    # Ensembles & pièces
    "l`ensemble sexy":              'Ensemble de Lingerie',
    'ensemble sexy':                'Ensemble de Lingerie',
    'set':                          'Ensemble de Lingerie',
    'bodysuit':                     'Body',
    'body':                         'Body',
    'corset':                       'Corset',
    'bustier':                      'Bustier',
    'babydoll':                     'Nuisette',
    'chemise':                      'Chemise de Nuit',
    'nightgown':                    'Nuisette',
    'peignoir':                     'Déshabillé',
    'robe':                         'Peignoir',
    'bathrobe':                     'Peignoir',
    'catsuit':                      'Combinaison',
    # Vêtements
    'robe sexy':                    'Robe',
    'dress':                        'Robe',
    'jupe sexy':                    'Jupe',
    'skirt':                        'Jupe',
    'blouse':                       'Blouse',
    'top':                          'Haut',
    'legging':                      'Legging',
    'leggings':                     'Leggings',
    'pants':                        'Pantalon',
    'trousers':                     'Pantalon',
    'jacket':                       'Veste',
    'coat':                         'Manteau',
    'cardigan':                     'Cardigan',
    'sweater':                      'Pull',
    'hoodie':                       'Sweat à Capuche',
    'jumpsuit':                     'Combinaison',
    'shorts':                       'Short',
    # Chaussures
    'ballerine':                    'Ballerines',
    'heels':                        'Escarpins',
    'boots':                        'Bottines',
    'sandals':                      'Sandales',
    'sneakers':                     'Baskets',
    'slippers':                     'Mules',
    'loafers':                      'Mocassins',
    # Accessoires
    'bonnet':                       'Bonnet',
    'châle':                        'Châle',
    'balaklava':                    'Cagoule',
    'infinity écharpe':             'Écharpe Tubulaire',
    'scarf':                        'Écharpe',
    'bag':                          'Sac',
    'handbag':                      'Sac à Main',
    'clutch':                       'Pochette',
    'belt':                         'Ceinture',
    'gloves':                       'Gants',
    'jewelry':                      'Bijoux',
    'accessoires érotiques':        'Accessoire Coquin',
    'accessories':                  'Accessoire',
}


# ── Dictionnaires pour enrichissement du nom ──────────────────────────────

MATIERES = [
    'dentelle', 'soie', 'satin', 'tulle', 'velours', 'cuir', 'daim',
    'coton', 'mesh', 'microfibre', 'broderie', 'guipure', 'mousseline',
    'jersey', 'lycra', 'vinyle', 'résille', 'organza', 'crêpe',
    'imitation daim', 'cuir écologique', 'faux cuir', 'simili cuir',
]

STYLES = [
    'élégant', 'élégante', 'sensuel', 'sensuelle', 'raffiné', 'raffinée',
    'séduisant', 'séduisante', 'glamour', 'romantique', 'audacieux',
    'audacieuse', 'délicat', 'délicate', 'provocant', 'provocante',
    'chic', 'bohème', 'rétro', 'vintage', 'classique', 'moderne',
    'intemporel', 'intemporelle', 'floral', 'florale', 'ajouré', 'ajourée',
    'transparent', 'transparente', 'ouvert', 'ouverte',
]

COULEURS = [
    'noir', 'noire', 'blanc', 'blanche', 'rouge', 'rose', 'bordeaux',
    'bleu', 'bleue', 'marine', 'beige', 'nude', 'ivoire', 'champagne',
    'doré', 'dorée', 'argenté', 'argentée', 'violet', 'violette',
    'vert', 'verte', 'émeraude', 'corail', 'fuchsia', 'turquoise',
    'crème', 'taupe', 'caramel', 'chocolat', 'gris', 'grise',
]


def nom_commercial(name_brut, brand, description, couleur=''):
    """
    Transforme « Push up model 32314 Axami » en « Push-Up en Microfibre Noir »
    en retirant la référence et la marque, puis en enrichissant avec des
    descripteurs tirés de la description.
    """
    nom = str(name_brut).strip()
    brand_clean = str(brand).strip()

    # 1. Extraire le type produit (partie avant « model XXXXX »)
    match_type = re.match(r'^(.+?)\s+model\s+\d+', nom, flags=re.IGNORECASE)
    type_brut = match_type.group(1).strip() if match_type else ''

    # 2. Traduire le type via le dictionnaire chic
    type_traduit = ''
    if type_brut:
        cle = type_brut.lower()
        type_traduit = TRADUCTION_TYPES.get(cle, '')

    # 3. Retirer « model XXXXX » et la marque
    nom = re.sub(r'\s+model\s+\d+', '', nom, flags=re.IGNORECASE)
    if brand_clean:
        nom = re.sub(re.escape(brand_clean), '', nom, flags=re.IGNORECASE)
    nom = re.sub(r'\s+', ' ', nom).strip()

    # 4. Utiliser la traduction si trouvée, sinon le type brut nettoyé
    if type_traduit:
        nom = type_traduit
    elif not nom:
        nom = 'Article'
    else:
        nom = nom[0].upper() + nom[1:] if len(nom) > 1 else nom.upper()

    # 6. Extraire descripteurs de la description
    desc_lower = str(description).lower() if description else ''
    couleur_s   = str(couleur).lower().strip() if couleur else ''

    # Matière (prendre la première trouvée, en privilégiant les composées)
    matiere_trouvee = ''
    for m in sorted(MATIERES, key=len, reverse=True):
        if m in desc_lower:
            matiere_trouvee = m
            break

    # Couleur (priorité au champ couleur explicite, sinon description)
    couleur_trouvee = ''
    if couleur_s:
        for c in COULEURS:
            if c in couleur_s:
                couleur_trouvee = c
                break
    if not couleur_trouvee:
        for c in COULEURS:
            if c in desc_lower:
                couleur_trouvee = c
                break

    # Style (prendre le premier trouvé)
    style_trouve = ''
    for s in STYLES:
        if s in desc_lower:
            style_trouve = s
            break

    # 7. Composer le nom final
    #    Pattern : « [Type] [Style] en [Matière] [Couleur] »
    parties = [nom]
    if style_trouve:
        # Accorder au féminin si le nom finit par e/es
        parties.append(style_trouve.title())
    if matiere_trouvee:
        parties.append(f'en {matiere_trouvee.title()}')
    if couleur_trouvee:
        parties.append(couleur_trouvee.title())

    resultat = ' '.join(parties)

    # 8. Éviter les noms trop longs (max ~80 car.)
    if len(resultat) > 80:
        resultat = resultat[:77].rsplit(' ', 1)[0] + '…'

    return resultat


# ── Mots-clés SEO par type (termes réellement recherchés) ─────────────────

SEO_KEYWORDS = {
    # Soutiens-gorge
    'Soutien-Gorge Push-Up':        'soutien gorge push up femme',
    'Soutien-Gorge Souple':         'soutien gorge sans armature femme',
    'Soutien-Gorge Semi-Souple':    'soutien gorge confort femme',
    'Soutien-Gorge Demi-Bonnet':    'soutien gorge balconnet femme',
    'Soutien-Gorge Dos Nageur':     'soutien gorge dos nu femme',
    'Soutien-Gorge Rembourré':      'soutien gorge rembourré femme',
    'Soutien-Gorge Ouvert':         'soutien gorge ouvert sexy',
    'Soutien-Gorge':                'soutien gorge femme',
    # Bas
    'String':                       'string femme dentelle',
    'String Ficelle':               'string ficelle femme sexy',
    'Culotte':                      'culotte femme dentelle',
    'Culotte Gainante':             'culotte gainante femme',
    'Shorty':                       'shorty femme dentelle',
    'Porte-Jarretelles':            'porte jarretelles femme sexy',
    'Bas':                          'bas femme sexy',
    'Collants':                     'collants femme fantaisie',
    # Ensembles & pièces
    'Ensemble de Lingerie':         'ensemble lingerie femme sexy',
    'Body':                         'body dentelle femme',
    'Corset':                       'corset femme sexy',
    'Bustier':                      'bustier femme dentelle',
    'Nuisette':                     'nuisette femme sexy',
    'Chemise de Nuit':              'chemise de nuit femme',
    'Déshabillé':                   'déshabillé femme sexy',
    'Peignoir':                     'peignoir femme satin',
    'Combinaison':                  'combinaison femme sexy',
    # Vêtements
    'Robe':                         'robe femme élégante',
    'Jupe':                         'jupe femme sexy',
    'Blouse':                       'blouse femme élégante',
    'Haut':                         'haut femme chic',
    'Legging':                      'legging femme',
    'Leggings':                     'legging femme',
    'Pantalon':                     'pantalon femme',
    'Veste':                        'veste femme',
    'Manteau':                      'manteau femme',
    'Cardigan':                     'cardigan femme',
    'Pull':                         'pull femme',
    'Short':                        'short femme',
    # Chaussures
    'Ballerines':                   'ballerines femme cuir',
    'Escarpins':                    'escarpins femme',
    'Bottines':                     'bottines femme',
    'Sandales':                     'sandales femme',
    'Baskets':                      'baskets femme',
    'Mules':                        'mules femme',
    'Mocassins':                    'mocassins femme',
    # Accessoires
    'Bonnet':                       'bonnet femme hiver',
    'Châle':                        'châle femme',
    'Cagoule':                      'cagoule femme',
    'Écharpe Tubulaire':            'écharpe snood femme',
    'Écharpe':                      'écharpe femme',
    'Sac à Main':                   'sac à main femme',
    'Pochette':                     'pochette femme',
    'Ceinture':                     'ceinture femme',
    'Gants':                        'gants femme',
    'Accessoire Coquin':            'accessoire lingerie sexy',
}


def balise_titre_seo(nom_clean, couleur, matiere, brand):
    """
    Génère une balise <title> SEO hybride :
    « Soutien Gorge Push Up Dentelle Noir | Plaisirs de Femmes »
    Mot-clé recherché + attributs + nom boutique. Max ~60 car.
    """
    # Récupérer le mot-clé SEO du type
    kw = SEO_KEYWORDS.get(nom_clean.split(' en ')[0].split(' Élégant')[0].split(' Sensuel')[0].strip(), '')

    if not kw:
        # Fallback : utiliser le nom commercial tel quel
        base = nom_clean
    else:
        # Enrichir avec matière/couleur si pas déjà dans le mot-clé
        parties_kw = [kw]
        if matiere and matiere.lower() not in kw.lower():
            parties_kw.append(matiere.lower())
        if couleur and couleur.lower() not in kw.lower():
            parties_kw.append(couleur.lower())
        base = ' '.join(parties_kw)

    # Capitaliser chaque mot
    base = base.title()

    # Ajouter le nom de la boutique
    titre = f'{base} | {NOM_BOUTIQUE}'

    # Tronquer à ~60 car. (Google coupe à ~60)
    if len(titre) > 60:
        max_base = 60 - len(f' | {NOM_BOUTIQUE}') - 1
        base = base[:max_base].rsplit(' ', 1)[0]
        titre = f'{base} | {NOM_BOUTIQUE}'

    return titre


def meta_description_seo(nom_clean, couleur, matiere, brand, desc_courte):
    """
    Génère une meta description SEO orientée conversion.
    « Découvrez notre soutien-gorge push-up en dentelle noir.
    Livraison rapide. Qualité premium. Plaisirs de Femmes. »
    Max ~155 car.
    """
    # Construire une phrase naturelle avec le nom commercial
    parties = [nom_clean.lower()]
    if matiere and matiere.lower() not in nom_clean.lower():
        parties_desc = f'en {matiere.lower()}'
        parties.append(parties_desc)
    if couleur and couleur.lower() not in nom_clean.lower():
        parties.append(couleur.lower())

    produit = ' '.join(parties)

    meta = f'Découvrez notre {produit}. '

    # Ajouter un extrait de la description courte si disponible
    if desc_courte:
        # Prendre la première phrase
        premiere_phrase = desc_courte.split('.')[0].strip()
        if premiere_phrase and len(premiere_phrase) > 20:
            espace_restant = 155 - len(meta) - len(f' {NOM_BOUTIQUE}.')
            if len(premiere_phrase) > espace_restant:
                premiere_phrase = premiere_phrase[:espace_restant-1].rsplit(' ', 1)[0]
            meta += premiere_phrase + '. '

    # Toujours finir par le nom de la boutique
    suffixe = f'{NOM_BOUTIQUE}.'
    if len(meta) + len(suffixe) <= 160:
        meta += suffixe

    # Tronquer à 160 max
    if len(meta) > 160:
        meta = meta[:157].rsplit(' ', 1)[0] + '…'

    return meta


def url_seo(nom_clean, couleur, pid):
    """
    Génère une URL simplifiée SEO-friendly.
    « soutien-gorge-push-up-dentelle-noir-206154 »
    """
    # Utiliser le nom commercial (sans les enrichissements trop longs)
    base = nom_clean.split(' en ')[0].strip()  # type seul
    parties = [slugify(base)]

    # Ajouter couleur si présente
    if couleur:
        parties.append(slugify(couleur))

    parties.append(str(pid))
    return '-'.join(p for p in parties if p)


def slugify(text):
    text = str(text).lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:100]


def short_desc(text, length=SHORT_DESC_LEN):
    if not isinstance(text, str):
        return ''
    t = re.sub(r'<[^>]+>', ' ', text)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > length:
        t = t[:length].rsplit(' ', 1)[0] + '…'
    return t


def prix_psychologique(wholesale, coef):
    """wholesale × coef → prix HT avec arrondi ,90 en TTC."""
    try:
        w = float(str(wholesale).replace(',', '.'))
        ttc = w * coef * (1 + TVA / 100)
        base = int(ttc)
        cand = base + PRICE_ENDING
        if cand < ttc:
            cand += 1.0
        ttc_final = round(cand, 2)
        ht_final  = round(ttc_final / (1 + TVA / 100), 2)
        return ht_final
    except (ValueError, TypeError):
        return ''


def nettoyer_ref(ref, max_len=MAX_REF_LEN):
    """Garantit une référence courte et propre."""
    ref = re.sub(r'[^\w\-]', '', str(ref))
    return ref[:max_len]


# ══════════════════════════════════════════════════════════════════════════════
#  PARSERS MATTERHORN
# ══════════════════════════════════════════════════════════════════════════════

def parse_sizes_stock(s):
    """'EU 36 | FR 38:2,EU 38 | FR 40:5' → [{'label':..., 'qty':...}]"""
    result = []
    if not isinstance(s, str) or not s.strip():
        return result
    for entry in s.split(','):
        entry = entry.strip()
        if ':' not in entry:
            continue
        label, qty_s = entry.rsplit(':', 1)
        try:
            result.append({'label': label.strip(), 'qty': int(qty_s.strip())})
        except ValueError:
            pass
    return result


def parse_sizes_sku(s):
    """'EU 36 | FR 38:M123,EU 38 | FR 40:M124' → {'EU 36 | FR 38': 'M123'}"""
    d = {}
    if not isinstance(s, str) or not s.strip():
        return d
    for entry in s.split(','):
        entry = entry.strip()
        if ':' not in entry:
            continue
        label, sku = entry.rsplit(':', 1)
        d[label.strip()] = sku.strip()
    return d


def parse_ean_par_taille(s):
    """'EU 36 | FR 38:1234567890123,...' → {'EU 36 | FR 38': '1234567890123'}"""
    d = {}
    if not isinstance(s, str) or not s.strip():
        return d
    for entry in s.split(','):
        entry = entry.strip()
        if ':' not in entry:
            continue
        label, ean = entry.rsplit(':', 1)
        ean = re.sub(r'\D', '', ean.strip())  # chiffres seulement
        if ean and len(ean) <= MAX_EAN_LEN:
            d[label.strip()] = ean
    return d


def get_category(row):
    bc = row.get('boutique_category', '').strip()
    if bc and bc not in ('', '❌ non mappé', '⚠️ à vérifier', '—'):
        return bc
    return row.get('category', '').strip()


def build_images(row):
    imgs = [row.get(c, '').strip() for c in ['image_1', 'image_2', 'image_3', 'image_4']]
    return ','.join(i for i in imgs if i)


# ══════════════════════════════════════════════════════════════════════════════
#  SCORING BESTSELLER
# ══════════════════════════════════════════════════════════════════════════════

def score_produit(row):
    sizes  = parse_sizes_stock(row.get('sizes_stock', ''))
    en_stock = sum(1 for s in sizes if s['qty'] > 0)

    recent = 0
    try:
        d = datetime.strptime(row.get('date_add', '')[:10], '%Y-%m-%d')
        if d >= datetime.now() - timedelta(days=RECENCE_JOURS):
            recent = BONUS_RECENT
    except ValueError:
        pass

    imgs = sum(1 for c in ['image_1','image_2','image_3','image_4']
               if row.get(c,'').strip())
    bonus_img = BONUS_4_IMAGES if imgs == 4 else 0

    stock_tot = sum(s['qty'] for s in sizes)
    return en_stock + recent + bonus_img, stock_tot


# ══════════════════════════════════════════════════════════════════════════════
#  SÉLECTION TOP N
# ══════════════════════════════════════════════════════════════════════════════

def selectionner_top(produits, top_n):
    par_cat = {}
    for p in produits:
        cat = get_category(p)
        if not cat or cat in CATS_EXCLUES:
            continue
        sc, stk = score_produit(p)
        p['_score'] = sc
        p['_stock'] = stk
        par_cat.setdefault(cat, []).append(p)

    selection = []
    rapport   = []
    for cat in sorted(par_cat):
        groupe = sorted(par_cat[cat],
                        key=lambda r: (r['_score'], r['_stock']),
                        reverse=True)
        top = groupe[:top_n]
        selection.extend(top)
        rapport.append((cat, len(groupe), len(top),
                        top[-1]['_score'] if top else 0,
                        top[0]['_score']  if top else 0))
    return selection, rapport


# ══════════════════════════════════════════════════════════════════════════════
#  COLONNES CSV SORTIE (Simple Import Product)
# ══════════════════════════════════════════════════════════════════════════════

COLS = [
    # Informations
    'Référence',
    'Nom',
    'Actif',
    'Visibilité',
    'Résumé',
    'Description',
    'URL simplifiée',
    # SEO
    'Balise titre',
    'Meta description',
    # Prix
    "Prix d'achat HT",
    'Prix de vente HT',
    'Taux de la TVA',
    # Associations
    'Nom de marque',
    'Catégorie par défaut',
    'Catégories associées',
    # Images
    "Liens vers les images",
    # Déclinaisons
    'Attribut',
    'Valeur',
    'Référence combinaison',
    'EAN combinaison',
    'Quantité',
    'Référence fournisseur',
]


# ══════════════════════════════════════════════════════════════════════════════
#  GÉNÉRATION CSV
# ══════════════════════════════════════════════════════════════════════════════

def generer_csv(selection, output_path, coef):
    lignes_produit = 0
    lignes_declin  = 0

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=COLS, delimiter=SEP,
                                extrasaction='ignore')
        writer.writeheader()

        for row in selection:
            pid       = row.get('id', '').strip()
            nom       = row.get('name', '').strip()
            cat       = get_category(row)
            wholesale = row.get('wholesale_price', '').strip()
            brand     = row.get('brand', '').strip()
            desc      = row.get('description', '').strip()

            couleur   = row.get('color', row.get('couleur', '')).strip()
            nom_clean = nom_commercial(nom, brand, desc, couleur)

            # Extraire matière/couleur pour les balises SEO
            desc_lower = desc.lower() if desc else ''
            matiere_seo = ''
            for m in sorted(MATIERES, key=len, reverse=True):
                if m in desc_lower:
                    matiere_seo = m
                    break
            couleur_seo = ''
            couleur_s = couleur.lower() if couleur else ''
            for c in COULEURS:
                if couleur_s and c in couleur_s:
                    couleur_seo = c
                    break
            if not couleur_seo:
                for c in COULEURS:
                    if c in desc_lower:
                        couleur_seo = c
                        break

            ref       = nettoyer_ref(f'PDF-{pid}')
            prix_ht   = prix_psychologique(wholesale, coef)
            url       = url_seo(nom_clean, couleur_seo, pid)
            images    = build_images(row)
            sdesc     = short_desc(desc)
            titre_seo = balise_titre_seo(nom_clean, couleur_seo, matiere_seo, brand)
            meta_seo  = meta_description_seo(nom_clean, couleur_seo, matiere_seo, brand, sdesc)

            sizes = parse_sizes_stock(row.get('sizes_stock', ''))
            skus  = parse_sizes_sku(row.get('sizes_sku_codes', ''))
            eans  = parse_ean_par_taille(row.get('ean_codes', ''))

            if not sizes:
                sizes = [{'label': 'Unique', 'qty': 1}]

            for i, size in enumerate(sizes):
                label = size['label']
                qty   = size['qty']
                sku   = nettoyer_ref(skus.get(label, f'{pid}-{i}'))
                ean   = eans.get(label, '')

                if i == 0:
                    # ── Ligne produit principale ──────────────────────────────
                    writer.writerow({
                        'Référence':           ref,
                        'Nom':                 nom_clean,
                        'Actif':               1,
                        'Visibilité':          'both',
                        'Résumé':              '',        # Phase 1 : vide
                        'Description':         '',        # Phase 1 : vide
                        'URL simplifiée':      url,
                        'Balise titre':        titre_seo,
                        'Meta description':    meta_seo,
                        "Prix d'achat HT":     wholesale,
                        'Prix de vente HT':    prix_ht,
                        'Taux de la TVA':      TVA,
                        'Nom de marque':       brand,
                        'Catégorie par défaut': cat,
                        'Catégories associées': cat,
                        'Liens vers les images': images,
                        'Attribut':            'Taille',
                        'Valeur':              label,
                        'Référence combinaison': sku,
                        'EAN combinaison':     ean,
                        'Quantité':            qty,
                        'Référence fournisseur': sku,
                    })
                    lignes_produit += 1
                else:
                    # ── Ligne déclinaison ─────────────────────────────────────
                    writer.writerow({
                        'Référence':             ref,
                        'Nom':                   nom_clean,
                        'Attribut':              'Taille',
                        'Valeur':                label,
                        'Référence combinaison': sku,
                        'EAN combinaison':       ean,
                        'Quantité':              qty,
                        'Référence fournisseur': sku,
                    })
                    lignes_declin += 1

    return lignes_produit, lignes_declin


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    source  = args[0]
    top_n   = DEFAULT_TOP
    coef    = DEFAULT_COEF
    output  = None

    i = 1
    while i < len(args):
        if args[i] == '--top' and i + 1 < len(args):
            top_n = int(args[i+1]);   i += 2
        elif args[i] == '--coef' and i + 1 < len(args):
            coef  = float(args[i+1]); i += 2
        elif args[i] == '--out' and i + 1 < len(args):
            output = args[i+1];       i += 2
        else:
            i += 1

    if not os.path.exists(source):
        print(f"ERREUR : fichier introuvable → {source}")
        sys.exit(1)

    if output is None:
        base   = re.sub(r'(_net_enrichi|_net|_nettoyes)$', '',
                        os.path.splitext(source)[0])
        output = base + f'_catalogue.csv'

    print(f"\n{'═'*60}")
    print(f"  Pipeline catalogue — {os.path.basename(source)}")
    print(f"  Top {top_n} / catégorie  |  Coef prix ×{coef}  |  TVA {TVA}%")
    print(f"{'═'*60}")

    # 1. Lecture
    produits = []
    with open(source, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=SEP)
        for row in reader:
            if row.get('id', '').strip():
                produits.append(row)
    print(f"\n  ✅ {len(produits)} produits chargés")

    # 2. Sélection top N
    selection, rapport = selectionner_top(produits, top_n)
    print(f"\n  {'Catégorie':<44} {'Dispo':>6} {'Top':>4} {'Score':>10}")
    print(f"  {'─'*68}")
    for cat, dispo, sel, smin, smax in rapport:
        print(f"  {cat:<44} {dispo:>6} {sel:>4}   {smin} – {smax}")
    print(f"  {'─'*68}")
    print(f"  Total sélectionné : {len(selection)} produits ({len(rapport)} catégories)\n")

    # 3. Génération CSV
    lp, ld = generer_csv(selection, output, coef)
    print(f"  📝 Lignes produit     : {lp}")
    print(f"  📝 Lignes déclinaison : {ld}")
    print(f"  📝 Total lignes CSV   : {lp + ld + 1} (+ header)")
    print(f"\n  → {output}")
    print(f"{'═'*60}\n")


if __name__ == '__main__':
    main()
