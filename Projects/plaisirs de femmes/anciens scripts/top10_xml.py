#!/usr/bin/env python3
"""
top10_xml.py — Sélection Top N bestsellers par catégorie depuis XML Matterhorn v2
=================================================================================
Lit directement le flux XML v2, score chaque produit, sélectionne les meilleurs
par catégorie, et génère un CSV PrestaShop 8 prêt à importer via Simple Import.

Score bestseller (proxy Matterhorn) :
  - nb de tailles en stock (+ de tailles dispo = + populaire)
  - +5 pts si produit créé < 365 jours (récent)
  - +3 pts si 4 images (fiche complète)
  - +2 pts si description > 200 car (fiche riche)

Usage :
  python top10_xml.py <fichier.xml> [--top 10] [--coef 2.2] [--taxe 1] [--colors-csv catalogue.csv]

  --colors-csv  CSV Matterhorn contenant le champ `other_colors` pour
                regrouper les variantes couleur en un seul produit PS.

Filtres appliqués automatiquement :
  - Uniquement FEMME (exclut HOMME, ENFANT)
  - Exclut Garçon/Pyjamas
  - Lingerie Érotique → univers "Audace" (lingerie seulement, pas accessoires/jouets)
"""

import xml.etree.ElementTree as ET
import csv
import sys
import os
import re
import unicodedata
from datetime import datetime, timedelta
from collections import defaultdict


# ── Paramètres ────────────────────────────────────────────────────────────────
DEFAULT_TOP    = 10
DEFAULT_COEF   = 2.2
DEFAULT_TAX_ID = 1
SHORT_DESC_LEN = 500
REF_PREFIX     = "PDF"
RECENCE_JOURS  = 365
BONUS_RECENT   = 5
BONUS_4_IMAGES = 3
BONUS_DESC     = 2
DESC_MIN_LEN   = 200

# Catégories érotiques à exclure (accessoires/jouets, pas lingerie)
EROTIQUE_EXCLUES = [
    "Accessoires Érotiques",
    "Costumes Érotiques Et Deguisements",
]

# Mapping catégories Matterhorn → PrestaShop (séparateur -> pour Simple Import)
CATEGORY_MAP = {
    # ─── Corps & Désirs (ID 3) — Lingerie classique ──────────────────────
    "Soutiens-Gorge Push Up":       "Corps & Désirs->Soutiens-Gorge Galbe",
    "Soutiens-Gorge Balconnet":     "Corps & Désirs->Soutiens-Gorge Décolleté",
    "Soutiens-Gorge Soft et Semi-Soft": "Corps & Désirs->Soutiens-Gorge Douceur",
    "Corsets et Bodys Femme":       "Corps & Désirs->Bodys de Soie",
    "Culottes":                     "Corps & Désirs->Dessous Précieux",
    "Strings":                      "Corps & Désirs->Dentelles Effilées",
    "Shortys, Boxers Femme":        "Corps & Désirs->Shortys de Charme",
    "les bretelles":                "Corps & Désirs->Corps & Velours",

    # ─── Fils de Soie (ID 51) — Bas, collants, gants ────────────────────
    "Collants, Bas":                "Fils de Soie->Bas & Collants de Soie",
    "Gants":                        "Fils de Soie->Gants d'Élégance",

    # ─── L'Heure Bleue (ID 13) — Nuit & Détente ─────────────────────────
    "Nuisettes, Chemises de Nuit":  "L'Heure Bleue->Nuits de Dentelle",
    "Pyjamas, Ensembles de Nuit":   "L'Heure Bleue->Nuits Sereines",
    "Peignoirs, Robes de Chambre et Kimonos": "L'Heure Bleue->Matins de Soie",

    # ─── Architecture Intime (ID 19) — Modelant ─────────────────────────
    "Culottes, Shortys et Strings Amincissants": "Architecture Intime->Affinements Secrets",
    "Corsets, Body Femme, Ceintures Modelantes et Gainantes": "Architecture Intime->Silhouettes Architecturées",

    # ─── L'Impudence (ID 54) — Érotique lingerie seulement ──────────────
    "Ensembles Sexy":               "L'Impudence->Objets du Désir",
    "Bodys, Caracos, Porte-Jarreteles, Corsets, Cullotes Sexy Et Leggins": "L'Impudence->Objets du Désir",
    "Guêpières, Bustiers, Nuisettes et Babydolls": "L'Impudence->Objets du Désir",

    # ─── La Garde-Robe (ID 24) — Vêtements & Balnéaire ──────────────────
    "Maillots de Bain 1 Pièce":     "La Garde-Robe->Balnéaire Une Pièce",
    "Maillots de Bain 2 Pièces":    "La Garde-Robe->Balnéaire Deux Pièces",
    "Robes de Plage, Paréos":       "La Garde-Robe->Échappées Balnéaires",
    "Bonnets et chapeaux":          "La Garde-Robe->Coiffures d'Été",
    "Foulards et Écharpes":         "La Garde-Robe->Soieries & Foulards",
    "Robes de Jour":                "La Garde-Robe->Robes du Jour",
    "Robes de Soirée":              "La Garde-Robe->Robes du Soir",
    "Robes de cocktail, Robes formelles": "La Garde-Robe->Robes de Cérémonie",
    "Combinaisons Femme":           "La Garde-Robe->Combinaisons d'Allure",
    "Jupes":                        "La Garde-Robe->Jupes de Caractère",
    "Blouses Femme, Tuniques":      "La Garde-Robe->Blouses & Tuniques",
    "Chemises Femme":               "La Garde-Robe->Chemises d'Auteur",
    "Tops Femme, T-shirts, Débardeurs Femme": "La Garde-Robe->Tops & Essentiels",
    "Maillots de Corps / Tops":     "La Garde-Robe->Hauts Décontractés",
    "Bodys Femme":                  "La Garde-Robe->Tops & Essentiels",
    "Leggings Femme":               "La Garde-Robe->Leggings de Caractère",
    "Pantalons femme, Shorts femme": "La Garde-Robe->Pantalons & Shorts",
    "Pantalons longs":              "La Garde-Robe->Pantalons de Coupe",
    "Pantalons élégants":           "La Garde-Robe->Pantalons d'Apparat",
    "Shorts Femme, Pantacourts, Corsaires Femme": "La Garde-Robe->Shorts & Pantacourts",
    "Blazers femme, Gilets femme":  "La Garde-Robe->Blazers & Gilets",
    "Vestes femme, Manteaux femme": "La Garde-Robe->Vestes & Manteaux",
    "Sweats et sweat-shirts femme": "La Garde-Robe->Sweats & Molletons",
    "Pulls, Chandails, Pullovers, PULLS a COL ROULÉ FEMME ET BOLEROS FEMME": "La Garde-Robe->Tricots & Cols Roulés",
    "Cardigans Femme, Ponchos":     "La Garde-Robe->Cardigans & Ponchos",
    "L`ensemble grandes tailles":   "La Garde-Robe->Mises en Scène",

    # ─── Toutes les Grâces (ID 56) — Maternité & Grandes tailles ────────
    "Soutiens-Gorge Allaitement, Grossesse et Maternité": "Toutes les Grâces->Soutiens-Gorge Maternité",
    "Robes de grossesse":           "Toutes les Grâces->Robes de la Belle Attente",
    "Pantalon grossesse":           "Toutes les Grâces->Pantalons de la Belle Attente",
    "Blouses de maternité":         "Toutes les Grâces->Blouses de Maternité",
    "Legging grossesse":            "Toutes les Grâces->Leggings de Maternité",
    "Tunique grossesse":            "Toutes les Grâces->Tuniques de Maternité",
    "Robes taille plus":            "Toutes les Grâces->Robes de Grâce",
    "Chemises, Chemisiers, Tuniques grande taille": "Toutes les Grâces->Chemises & Tuniques Grande Taille",
    "Pulls, Cardigans Femme Grandes Tailles": "Toutes les Grâces->Tricots Grande Taille",
    "T-shrits grandes tailles":     "Toutes les Grâces->Hauts Essentiels Grande Taille",
    "Sweatshirts taille plus":      "Toutes les Grâces->Molletons Grande Taille",

    # ─── Chaussures (nouvel univers — à créer dans PS) ───────────────────
    "Bottes et boots":              "Chaussures->Bottes & Boots",
    "Bottes, Cuissardes":           "Chaussures->Cuissardes",
    "Sandales et mules":            "Chaussures->Sandales & Mules",
    "Chausseres de sport":          "Chaussures->Sneakers",
    "Mocassins, Lords":             "Chaussures->Mocassins & Lords",
    "Ballerines":                   "Chaussures->Ballerines",
    "Chaussons":                    "Chaussures->Chaussons",
    "Escarpins":                    "Chaussures->Escarpins",
    "Talons aiguilles":             "Chaussures->Talons Aiguilles",
    "Escarpins à talons bloc":      "Chaussures->Talons Bloc",

    # ─── Variantes de nommage (catégories réelles du XML 85 Mo) ─────────
    "Escarpins à talons bloc":      "Chaussures->Talons Bloc",
    "Guêpières, Bustiers, Nuisettes et Babydolls": "L'Impudence->Objets du Désir",
    "Maillots de Bain 1 Pièce":     "La Garde-Robe->Balnéaire Une Pièce",
    "Maillots de Bain 2 Pièces":    "La Garde-Robe->Balnéaire Deux Pièces",
    "Pantalons de survêtement femme": "La Garde-Robe->Pantalons de Détente",
    "Vêtements et Lingerie de Nuit": "L'Heure Bleue->Voiles de Nuit",
    "Chemises Femme, Blouses Femme": "La Garde-Robe->Blouses & Tuniques",
    "Cullotes ew.cullotes et bas":  "Corps & Désirs->Dessous Précieux",
    "Lingerie":                     "Corps & Désirs->Parures d'Exception",
    "Lingerie Sexy, Lingerie Érotique": "L'Impudence->Objets du Désir",
    "Tenues Maternite":             "Toutes les Grâces->Robes de la Belle Attente",
    "Tops":                         "La Garde-Robe->Tops & Essentiels",
}

NOM_BOUTIQUE = 'Plaisirs de Femmes'

# ── Traduction types Matterhorn → nom boutique chic ──────────────────────────

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

# ── Descripteurs pour enrichissement du nom ───────────────────────────────────

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

# ── Mots-clés SEO par type (termes réellement recherchés) ─────────────────────

SEO_KEYWORDS = {
    'Soutien-Gorge Push-Up':        'soutien gorge push up femme',
    'Soutien-Gorge Souple':         'soutien gorge sans armature femme',
    'Soutien-Gorge Semi-Souple':    'soutien gorge confort femme',
    'Soutien-Gorge Demi-Bonnet':    'soutien gorge balconnet femme',
    'Soutien-Gorge Dos Nageur':     'soutien gorge dos nu femme',
    'Soutien-Gorge Rembourré':      'soutien gorge rembourré femme',
    'Soutien-Gorge Ouvert':         'soutien gorge ouvert sexy',
    'Soutien-Gorge':                'soutien gorge femme',
    'String':                       'string femme dentelle',
    'String Ficelle':               'string ficelle femme sexy',
    'Culotte':                      'culotte femme dentelle',
    'Culotte Gainante':             'culotte gainante femme',
    'Shorty':                       'shorty femme dentelle',
    'Porte-Jarretelles':            'porte jarretelles femme sexy',
    'Bas':                          'bas femme sexy',
    'Collants':                     'collants femme fantaisie',
    'Ensemble de Lingerie':         'ensemble lingerie femme sexy',
    'Body':                         'body dentelle femme',
    'Corset':                       'corset femme sexy',
    'Bustier':                      'bustier femme dentelle',
    'Nuisette':                     'nuisette femme sexy',
    'Chemise de Nuit':              'chemise de nuit femme',
    'Déshabillé':                   'déshabillé femme sexy',
    'Peignoir':                     'peignoir femme satin',
    'Combinaison':                  'combinaison femme sexy',
    'Robe':                         'robe femme élégante',
    'Jupe':                         'jupe femme sexy',
    'Blouse':                       'blouse femme élégante',
    'Haut':                         'haut femme chic',
    'Legging':                      'legging femme',
    'Pantalon':                     'pantalon femme',
    'Veste':                        'veste femme',
    'Manteau':                      'manteau femme',
    'Cardigan':                     'cardigan femme',
    'Pull':                         'pull femme',
    'Short':                        'short femme',
    'Ballerines':                   'ballerines femme cuir',
    'Escarpins':                    'escarpins femme',
    'Bottines':                     'bottines femme',
    'Sandales':                     'sandales femme',
    'Baskets':                      'baskets femme',
    'Mules':                        'mules femme',
    'Mocassins':                    'mocassins femme',
    'Bonnet':                       'bonnet femme hiver',
    'Châle':                        'châle femme',
    'Cagoule':                      'cagoule femme',
    'Écharpe Tubulaire':            'écharpe snood femme',
    'Écharpe':                      'écharpe femme',
    'Sac à Main':                   'sac à main femme',
    'Pochette':                     'pochette femme',
    'Gants':                        'gants femme',
    'Accessoire Coquin':            'accessoire lingerie sexy',
}


# ── Genre et nombre des types produit (pour accord adjectifs) ─────────────────
# Détection par le PREMIER MOT du type — gère les modifieurs (Blazer femme, etc.)

# Mots masculins (premier mot du type)
MOTS_MASCULINS = {
    'soutien-gorge', 'string', 'shorty', 'porte-jarretelles',
    'body', 'corset', 'bustier', 'déshabillé', 'peignoir',
    'haut', 'legging', 'pantalon', 'manteau', 'cardigan', 'pull',
    'short', 'bonnet', 'châle', 'sac', 'chemisier', 'collant',
    'ensemble', 'sweat', 'blazer', 'gilet', 'jupon', 'foulard',
    'pyjama', 'caleçon', 'débardeur', 'maillot', 'bikini',
    'tanga', 'teddy', 'négligé', 'top', 'jean', 'jogging',
    'bas', 'accessoire', 'gants', 'chandail', 'tricot', 't-shirt',
    'sweatshirt', 'corsaire', 'moccasins', 'talons', 'pantalons',
}

# Mots pluriels (premier mot du type)
MOTS_PLURIELS = {
    'ballerines', 'escarpins', 'bottines', 'sandales', 'baskets',
    'mules', 'mocassins', 'collants', 'leggings', 'gants',
    'bottes', 'pantoufles', 'bas', 'chaussons', 'gants',
    'chaussures', 'talons', 'moccasins', 'pantalons',
}


def _detecter_genre_nombre(type_traduit):
    """Détecte genre et nombre à partir du premier mot du type."""
    if not type_traduit:
        return False, False  # féminin singulier par défaut

    # Cas spécial : "L'ensemble", "L`ensemble"
    type_clean = type_traduit.replace('`', "'")
    if type_clean.lower().startswith("l'ensemble") or type_clean.lower().startswith("l`ensemble"):
        return False, False  # masculin singulier → est_feminin=False

    premier_mot = type_traduit.split()[0].lower().strip()

    est_masculin = premier_mot in MOTS_MASCULINS
    est_pluriel = premier_mot in MOTS_PLURIELS

    # Féminin = tout ce qui n'est pas masculin
    est_feminin = not est_masculin

    return est_feminin, est_pluriel

# Accord : forme de base (masc. sing.) → {fém. sing., masc. plur., fém. plur.}
ACCORDS = {
    'noir':        {'fs': 'noire',       'mp': 'noirs',       'fp': 'noires'},
    'blanc':       {'fs': 'blanche',     'mp': 'blancs',      'fp': 'blanches'},
    'bleu':        {'fs': 'bleue',       'mp': 'bleus',       'fp': 'bleues'},
    'gris':        {'fs': 'grise',       'mp': 'gris',        'fp': 'grises'},
    'vert':        {'fs': 'verte',       'mp': 'verts',       'fp': 'vertes'},
    'violet':      {'fs': 'violette',    'mp': 'violets',     'fp': 'violettes'},
    'doré':        {'fs': 'dorée',       'mp': 'dorés',       'fp': 'dorées'},
    'argenté':     {'fs': 'argentée',    'mp': 'argentés',    'fp': 'argentées'},
    'rouge':       {'fs': 'rouge',       'mp': 'rouges',      'fp': 'rouges'},
    'rose':        {'fs': 'rose',        'mp': 'roses',       'fp': 'roses'},
    'beige':       {'fs': 'beige',       'mp': 'beiges',      'fp': 'beiges'},
    'élégant':     {'fs': 'élégante',    'mp': 'élégants',    'fp': 'élégantes'},
    'raffiné':     {'fs': 'raffinée',    'mp': 'raffinés',    'fp': 'raffinées'},
    'sensuel':     {'fs': 'sensuelle',   'mp': 'sensuels',    'fp': 'sensuelles'},
    'séduisant':   {'fs': 'séduisante',  'mp': 'séduisants',  'fp': 'séduisantes'},
    'audacieux':   {'fs': 'audacieuse',  'mp': 'audacieux',   'fp': 'audacieuses'},
    'délicat':     {'fs': 'délicate',    'mp': 'délicats',    'fp': 'délicates'},
    'provocant':   {'fs': 'provocante',  'mp': 'provocants',  'fp': 'provocantes'},
    'intemporel':  {'fs': 'intemporelle','mp': 'intemporels',  'fp': 'intemporelles'},
    'floral':      {'fs': 'florale',     'mp': 'floraux',     'fp': 'florales'},
    'ajouré':      {'fs': 'ajourée',     'mp': 'ajourés',     'fp': 'ajourées'},
    'transparent': {'fs': 'transparente','mp': 'transparents', 'fp': 'transparentes'},
    'ouvert':      {'fs': 'ouverte',     'mp': 'ouverts',     'fp': 'ouvertes'},
    'romantique':  {'fs': 'romantique',  'mp': 'romantiques',  'fp': 'romantiques'},
    'classique':   {'fs': 'classique',   'mp': 'classiques',   'fp': 'classiques'},
    'chic':        {'fs': 'chic',        'mp': 'chics',        'fp': 'chics'},
}

# Table inverse : toute forme fléchie → base masculine singulière
_INVERSE = {}
for base, formes in ACCORDS.items():
    _INVERSE[base] = base
    for forme in formes.values():
        _INVERSE[forme] = base


def _accorder(mot, est_feminin, est_pluriel=False):
    """Accorde un adjectif/couleur au genre et nombre voulus."""
    mot_lower = mot.lower()
    base = _INVERSE.get(mot_lower, None)
    if base is None:
        return mot
    if est_pluriel:
        cle = 'fp' if est_feminin else 'mp'
    elif est_feminin:
        cle = 'fs'
    else:
        return base  # masculin singulier = forme de base
    return ACCORDS[base][cle]


# ── Fonctions nom commercial + SEO ───────────────────────────────────────────

def _extract_descripteurs(description, couleur):
    """Extrait matière, couleur et style de la description."""
    desc_lower = description.lower() if description else ''
    couleur_s = couleur.lower().strip() if couleur else ''

    matiere = ''
    for m in sorted(MATIERES, key=len, reverse=True):
        if m in desc_lower:
            matiere = m
            break

    coul = ''
    if couleur_s:
        for c in COULEURS:
            if c in couleur_s:
                coul = c
                break
    if not coul:
        for c in COULEURS:
            if c in desc_lower:
                coul = c
                break

    style = ''
    for s in STYLES:
        if s in desc_lower:
            style = s
            break

    return matiere, coul, style


def nom_commercial(name_brut, brand, prod_type, description, couleur='', inclure_couleur=True):
    """
    Transforme « Push up model 32314 Axami » en « Soutien-Gorge Push-Up en Dentelle Noir »
    en utilisant le champ <type> du XML + enrichissement description.
    Si inclure_couleur=False, la couleur n'est PAS ajoutée au nom (utile quand
    la couleur est gérée comme déclinaison).
    """
    # 1. Traduire le type via le dictionnaire chic
    cle = prod_type.lower().strip() if prod_type else ''
    type_traduit = TRADUCTION_TYPES.get(cle, '')

    if not type_traduit:
        # Fallback : essayer depuis le nom brut (retirer model XXXXX + marque)
        nom = str(name_brut).strip()
        match_type = re.match(r'^(.+?)\s+model\s+\d+', nom, flags=re.IGNORECASE)
        if match_type:
            cle2 = match_type.group(1).strip().lower()
            type_traduit = TRADUCTION_TYPES.get(cle2, '')
        if not type_traduit:
            # Dernier recours : nettoyer le nom
            nom = re.sub(r'\s+model\s+\d+', '', nom, flags=re.IGNORECASE)
            brand_clean = str(brand).strip()
            if brand_clean:
                nom = re.sub(re.escape(brand_clean), '', nom, flags=re.IGNORECASE)
            nom = re.sub(r'\s+', ' ', nom).strip()
            type_traduit = nom if nom else 'Article'

    # 2. Enrichir avec descripteurs + accord genre/nombre
    matiere, coul, style = _extract_descripteurs(description, couleur)
    feminin, pluriel = _detecter_genre_nombre(type_traduit)

    parties = [type_traduit]
    if style:
        parties.append(_accorder(style, feminin, pluriel).title())
    if matiere:
        parties.append(f'en {matiere.title()}')
    if coul and inclure_couleur:
        parties.append(_accorder(coul, feminin, pluriel).title())

    resultat = ' '.join(parties)
    if len(resultat) > 80:
        resultat = resultat[:77].rsplit(' ', 1)[0] + '…'

    return resultat


def balise_titre_seo(type_traduit, couleur, matiere):
    """Title SEO hybride : mot-clé recherché + attributs + nom boutique. Max ~65 car."""
    kw = SEO_KEYWORDS.get(type_traduit, '')
    if not kw:
        base = type_traduit
    else:
        parties_kw = [kw]
        if matiere and matiere.lower() not in kw.lower():
            parties_kw.append(matiere.lower())
        if couleur and couleur.lower() not in kw.lower():
            parties_kw.append(couleur.lower())
        base = ' '.join(parties_kw)

    base = base.title()
    titre = f'{base} | {NOM_BOUTIQUE}'

    if len(titre) > 65:
        max_base = 65 - len(f' | {NOM_BOUTIQUE}') - 1
        base = base[:max_base].rsplit(' ', 1)[0]
        titre = f'{base} | {NOM_BOUTIQUE}'

    return titre


def meta_description_seo(nom_clean, couleur, matiere, sdesc):
    """Meta description orientée conversion. Max ~155 car."""
    parties = [nom_clean.lower()]
    if matiere and matiere.lower() not in nom_clean.lower():
        parties.append(f'en {matiere.lower()}')
    if couleur and couleur.lower() not in nom_clean.lower():
        parties.append(couleur.lower())

    produit = ' '.join(parties)
    meta = f'Découvrez notre {produit}. '

    if sdesc:
        premiere_phrase = sdesc.split('.')[0].strip()
        if premiere_phrase and len(premiere_phrase) > 20:
            espace = 155 - len(meta) - len(f' {NOM_BOUTIQUE}.')
            if len(premiere_phrase) > espace:
                premiere_phrase = premiere_phrase[:espace - 1].rsplit(' ', 1)[0]
            meta += premiere_phrase + '. '

    suffixe = f'{NOM_BOUTIQUE}.'
    if len(meta) + len(suffixe) <= 160:
        meta += suffixe

    if len(meta) > 160:
        meta = meta[:157].rsplit(' ', 1)[0] + '…'

    return meta


# ── Helpers ───────────────────────────────────────────────────────────────────

def slugify(text):
    text = str(text).lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:120]


def extract_prose(html):
    if not html:
        return ''
    html = re.split(r"<div class=['\"]prod_data", html, 1)[0]
    html = re.split(r"<table", html, 1)[0]
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_composition(html):
    if not html:
        return ''
    match = re.search(r"<div class=['\"]prod_data['\"]>(.*?)</div>", html, re.DOTALL)
    if not match:
        return ''
    bloc = match.group(1)
    pairs = re.findall(r'<strong>(.*?)</strong>\s*([\d]+\s*%)', bloc)
    if pairs:
        return ', '.join(f"{mat.strip()} {pct.strip()}" for mat, pct in pairs)
    return ''


def short_desc(text, length=SHORT_DESC_LEN):
    if not text:
        return ''
    if len(text) > length:
        text = text[:length].rsplit(' ', 1)[0] + '…'
    return text


def _normalize(text):
    """Supprime les accents pour comparaison floue."""
    text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn').lower().strip()

# Index normalisé pour fallback sans accents
_CATEGORY_MAP_NORM = {_normalize(k): v for k, v in CATEGORY_MAP.items()}

_CATEGORIES_NON_MAPPEES = set()  # Pour diagnostic

def map_category(category_path):
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
    # Fallback partiel : essayer chaque segment du chemin (du plus profond au moins profond)
    parts = [p.strip() for p in category_path.strip('/').split('/') if p.strip()]
    for seg in reversed(parts):
        if seg in CATEGORY_MAP:
            return CATEGORY_MAP[seg]
        seg_norm = _normalize(seg)
        if seg_norm in _CATEGORY_MAP_NORM:
            return _CATEGORY_MAP_NORM[seg_norm]
    # Dernier recours : chemin sans FEMME
    parts_clean = [p for p in parts if p.upper() != 'FEMME']
    if parts_clean:
        _CATEGORIES_NON_MAPPEES.add(leaf)
        return '->'.join(parts_clean)
    return ''


def compute_price(price_str, coef):
    try:
        return round(float(price_str.replace(',', '.')) * coef, 2)
    except (ValueError, AttributeError):
        return ''


def est_recent(date_str, jours=RECENCE_JOURS):
    if not date_str:
        return False
    try:
        d = datetime.strptime(date_str.strip()[:10], '%Y-%m-%d')
        return d >= datetime.now() - timedelta(days=jours)
    except ValueError:
        return False


def doit_exclure(category_path):
    """Vérifie si le produit doit être exclu."""
    if not category_path:
        return True
    parts = [p.strip() for p in category_path.strip('/').split('/') if p.strip()]
    # Exclure tout ce qui n'est pas FEMME
    if not parts or parts[0] != 'FEMME':
        return True
    # Exclure les accessoires/costumes érotiques (pas la lingerie érotique)
    leaf = parts[-1] if parts else ''
    if leaf in EROTIQUE_EXCLUES:
        return True
    return False


# ── Score ─────────────────────────────────────────────────────────────────────

def score_product(options, creation_date, images_count, desc_len):
    """Calcule le score bestseller d'un produit."""
    # Nombre de tailles en stock
    tailles_ok = sum(1 for o in options if o['qty'] > 0)
    # Bonus récence
    recent = BONUS_RECENT if est_recent(creation_date) else 0
    # Bonus images complètes
    imgs = BONUS_4_IMAGES if images_count >= 4 else 0
    # Bonus description riche
    desc = BONUS_DESC if desc_len >= DESC_MIN_LEN else 0
    return tailles_ok + recent + imgs + desc


# ── En-tête CSV ───────────────────────────────────────────────────────────────

PS_HEADER = [
    'ID', 'Active (0/1)', 'Name *[fr-FR]', 'Categories (x,y,z,...)',
    'Price tax excl.', 'Tax rules ID', 'Wholesale price', 'Reference #',
    'EAN13', 'Brand', 'Short description[fr-FR]', 'Description[fr-FR]',
    'Meta title[fr-FR]', 'Meta description[fr-FR]',
    'URL rewritten[fr-FR]', 'Image URLs (x,y,z,...)',
    'Attribute (Name:Type:Position)*', 'Value (Value:Position)*',
    'Combination Reference', 'Quantity', 'Supplier reference',
]


# ── Pipeline principal ────────────────────────────────────────────────────────

def _traduire_couleur(color_raw):
    """Traduit les couleurs Matterhorn (souvent en anglais/mixte) en français propre."""
    TRAD_COULEURS = {
        'black': 'Noir', 'white': 'Blanc', 'red': 'Rouge', 'blue': 'Bleu',
        'green': 'Vert', 'pink': 'Rose', 'beige': 'Beige', 'grey': 'Gris',
        'gray': 'Gris', 'brown': 'Marron', 'navy': 'Marine', 'cream': 'Crème',
        'purple': 'Violet', 'yellow': 'Jaune', 'orange': 'Orange',
        'gold': 'Doré', 'silver': 'Argenté', 'ivory': 'Ivoire',
        'burgundy': 'Bordeaux', 'coral': 'Corail', 'nude': 'Nude',
        'khaki': 'Kaki', 'turquoise': 'Turquoise', 'ecru': 'Écru',
        'bordeaux': 'Bordeaux', 'salmon': 'Saumon', 'mint': 'Menthe',
        'lavender': 'Lavande', 'lilac': 'Lilas', 'fuchsia': 'Fuchsia',
        'peach': 'Pêche', 'taupe': 'Taupe', 'charcoal': 'Anthracite',
        'multicolor': 'Multicolore', 'multicolore': 'Multicolore',
        'noir': 'Noir', 'blanc': 'Blanc', 'rouge': 'Rouge', 'bleu': 'Bleu',
        'vert': 'Vert', 'rose': 'Rose', 'gris': 'Gris', 'marron': 'Marron',
        'violet': 'Violet', 'jaune': 'Jaune', 'crème': 'Crème',
    }
    if not color_raw:
        return 'Défaut'
    c = color_raw.strip()
    return TRAD_COULEURS.get(c.lower(), c.title())


def run(xml_path, top_n=DEFAULT_TOP, coef=DEFAULT_COEF, tax_id=DEFAULT_TAX_ID, colors_csv=None):
    print(f"\n📂 Source XML  : {xml_path}")
    print(f"🏆 Top {top_n} par catégorie")
    print(f"💰 Coef prix   : ×{coef}")

    # ── Phase 1 : charger, scorer, et collecter les liens couleur ────────
    all_prods = {}           # pid → données produit
    cat_pids = defaultdict(list)  # cat_leaf → [pids]
    total = 0
    exclus = 0

    for _, elem in ET.iterparse(xml_path, events=('end',)):
        if elem.tag != 'product':
            continue
        total += 1

        pid = elem.get('id', '').strip()
        category_path = (elem.findtext('category_path') or '').strip()

        if not pid or doit_exclure(category_path):
            exclus += 1
            elem.clear()
            continue

        name          = (elem.findtext('name') or '').strip()
        brand         = (elem.findtext('brand') or '').strip()
        color         = (elem.findtext('color') or '').strip()
        prod_type     = (elem.findtext('type') or '').strip()
        price_raw     = (elem.findtext('price') or '').strip()
        desc_raw      = (elem.findtext('description') or '').strip()
        creation_date = (elem.findtext('creation_date') or '').strip()

        # Liens vers les autres couleurs du même modèle
        other_colors_raw = (elem.findtext('other_colors') or '').strip()
        other_color_ids = []
        if other_colors_raw:
            # Format attendu : IDs séparés par virgule ou point-virgule
            for oc in re.split(r'[,;|]+', other_colors_raw):
                oc = oc.strip()
                if oc and oc != pid:
                    other_color_ids.append(oc)

        description = extract_prose(desc_raw)
        composition = extract_composition(desc_raw)
        if composition:
            description += f"\n\nComposition : {composition}"

        images = []
        for img in elem.findall('.//image_url'):
            u = (img.text or '').strip()
            if u:
                images.append(u)

        options_data = []
        for opt in elem.findall('.//option'):
            options_data.append({
                'label': (opt.findtext('option_name') or 'Taille unique').strip(),
                'qty':   int(opt.findtext('STOCK') or '0'),
                'ean':   (opt.findtext('ean') or '').strip(),
                'sku':   opt.get('id', f"PDF-{pid}"),
            })
        if not options_data:
            options_data = [{'label': 'Taille unique', 'qty': 0, 'ean': '', 'sku': f"PDF-{pid}"}]

        sc = score_product(options_data, creation_date, len(images), len(description))

        cat_leaf = category_path.rstrip('/').split('/')[-1].strip()
        if not cat_leaf:
            cat_leaf = category_path

        all_prods[pid] = {
            'pid': pid, 'name': name, 'brand': brand, 'color': color,
            'prod_type': prod_type, 'price_raw': price_raw,
            'description': description, 'sdesc': short_desc(extract_prose(desc_raw)),
            'category_path': category_path, 'cat_leaf': cat_leaf,
            'images': images, 'options': options_data, 'score': sc,
            'stock_total': sum(o['qty'] for o in options_data),
            'other_colors': other_color_ids,
        }
        cat_pids[cat_leaf].append(pid)

        elem.clear()

    print(f"\n✅ Total lu : {total}  |  Exclus : {exclus}  |  Retenus : {len(all_prods)}")
    print(f"📂 Catégories : {len(cat_pids)}")

    # ── Phase 1b : Regrouper les variantes couleur via CSV fournisseur ─────
    # Le CSV Matterhorn contient un champ `other_colors` (IDs séparés par virgule)
    # qui relie les variantes couleur d'un même modèle.

    # Union-Find pour construire les groupes
    _uf_parent = {}

    def _uf_find(x):
        while _uf_parent.get(x, x) != x:
            _uf_parent[x] = _uf_parent.get(_uf_parent[x], _uf_parent[x])
            x = _uf_parent[x]
        return x

    def _uf_union(a, b):
        ra, rb = _uf_find(a), _uf_find(b)
        if ra != rb:
            if ra < rb:
                _uf_parent[rb] = ra
            else:
                _uf_parent[ra] = rb

    if colors_csv:
        liens = 0
        with open(colors_csv, 'r', encoding='utf-8-sig') as fc:
            reader = csv.DictReader(fc, delimiter=';')
            for row in reader:
                pid_csv = str(row.get('id', '')).strip()
                if pid_csv not in all_prods:
                    continue
                oc = (row.get('other_colors', '') or '').strip()
                if not oc:
                    continue
                for other_id in re.split(r'[,;|]+', oc):
                    other_id = other_id.strip()
                    if other_id and other_id in all_prods and other_id != pid_csv:
                        _uf_union(pid_csv, other_id)
                        liens += 1
        print(f"🔗 CSV couleurs : {liens} liens trouvés dans {colors_csv}")
    else:
        print(f"⚠️  Pas de --colors-csv → chaque couleur = un produit séparé")

    # Construire les groupes
    color_groups = defaultdict(list)
    pid_to_root = {}
    for pid in all_prods:
        root = _uf_find(pid)
        color_groups[root].append(pid)

    # Trier chaque groupe : meilleur score en premier, puis réindexer root
    final_groups = {}
    pid_to_root = {}
    for root, pids in color_groups.items():
        pids.sort(
            key=lambda p: (all_prods[p]['score'], all_prods[p]['stock_total']),
            reverse=True
        )
        new_root = pids[0]
        final_groups[new_root] = pids
        for p in pids:
            pid_to_root[p] = new_root
    color_groups = final_groups

    nb_groupes = len(color_groups)
    nb_multi = sum(1 for g in color_groups.values() if len(g) > 1)
    print(f"🎨 Groupes couleur : {nb_groupes} ({nb_multi} avec variantes, "
          f"{nb_groupes - nb_multi} produit unique)")

    # ── Phase 2 : sélection top N groupes par catégorie ──────────────────
    # Chaque groupe est représenté par sa racine UF.
    # Score du groupe = score du meilleur membre.
    # Catégorie du groupe = catégorie du meilleur membre.

    cat_group_roots = defaultdict(set)
    for cat_leaf, pids in cat_pids.items():
        for pid in pids:
            cat_group_roots[cat_leaf].add(pid_to_root[pid])

    selected_roots = []
    print(f"\n{'Catégorie':<55} {'Groupes':>7} {'Top':>4} {'Score':>10}")
    print('─' * 82)

    for cat in sorted(cat_group_roots.keys()):
        roots_in_cat = list(cat_group_roots[cat])
        # Scorer chaque groupe
        scored = []
        for root in roots_in_cat:
            best_pid = color_groups[root][0]  # déjà trié
            best = all_prods[best_pid]
            group_stock = sum(all_prods[p]['stock_total'] for p in color_groups[root])
            scored.append((root, best['score'], group_stock))
        scored.sort(key=lambda x: (x[1], x[2]), reverse=True)
        top = scored[:top_n]
        selected_roots.extend([s[0] for s in top])
        smin = top[-1][1] if top else 0
        smax = top[0][1] if top else 0
        print(f"  {cat:<53} {len(scored):>7} {len(top):>4}   {smin:>3} – {smax:<3}")

    # Dédoublonner (un groupe peut apparaître dans plusieurs catégories)
    seen_roots = set()
    unique_roots = []
    for root in selected_roots:
        if root not in seen_roots:
            seen_roots.add(root)
            unique_roots.append(root)
    selected_roots = unique_roots

    total_produits = sum(len(color_groups[r]) for r in selected_roots)
    print(f"\n{'─' * 82}")
    print(f"  🏆 Total : {len(selected_roots)} groupes ({total_produits} produits individuels)")

    # ── Phase 3 : générer le CSV PrestaShop avec Couleur × Taille ────────
    base = os.path.splitext(xml_path)[0]
    csv_path = base + f'_top{top_n}_import.csv'

    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as fout:
        writer = csv.writer(fout, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(PS_HEADER)
        lignes = 0

        for root in selected_roots:
            members = color_groups[root]
            main = all_prods[members[0]]  # meilleur score = produit principal
            has_colors = len(members) > 1

            price     = compute_price(main['price_raw'], coef)
            category  = map_category(main['category_path'])
            reference = f"{REF_PREFIX}-{main['pid']}"

            # Images de TOUTES les variantes couleur
            all_images = []
            for m_pid in members:
                all_images.extend(all_prods[m_pid]['images'])
            images_str = ','.join(all_images)

            # Nom commercial SANS couleur (couleur = déclinaison)
            nom_clean = nom_commercial(
                main['name'], main['brand'], main['prod_type'],
                main['description'], main['color'],
                inclure_couleur=not has_colors,
            )
            matiere, coul, _ = _extract_descripteurs(main['description'], main['color'])

            cle_type = main['prod_type'].lower().strip() if main['prod_type'] else ''
            type_pour_seo = TRADUCTION_TYPES.get(
                cle_type,
                nom_clean.split(' en ')[0].split(' Élégant')[0].split(' Sensuel')[0].strip()
            )

            url = slugify(f"{nom_clean} {main['pid']}")
            titre_seo = balise_titre_seo(type_pour_seo, coul, matiere)
            meta_seo  = meta_description_seo(nom_clean, coul, matiere, main['sdesc'])

            # ── Générer les lignes de combinaisons ──
            combo_i = 0
            for m_pid in members:
                m = all_prods[m_pid]
                couleur_label = _traduire_couleur(m['color'])

                for opt in m['options']:
                    if has_colors:
                        attr_col = 'Couleur:select:0,Taille:select:1'
                        val_col  = f"{couleur_label}:0,{opt['label']}:0"
                    else:
                        attr_col = 'Taille:select:0'
                        val_col  = f"{opt['label']}:{combo_i}"

                    writer.writerow([
                        '', 1, nom_clean, category, price, tax_id,
                        main['price_raw'], reference, opt['ean'], main['brand'],
                        main['sdesc'], main['description'],
                        titre_seo, meta_seo,
                        url, images_str if combo_i == 0 else '',
                        attr_col, val_col,
                        opt['sku'], opt['qty'], opt['sku'],
                    ])
                    combo_i += 1
                    lignes += 1

    print(f"\n  📝 Lignes CSV : {lignes}")
    print(f"→ Fichier import : {csv_path}")

    # ── Phase 4 : CSV descriptions (1 ligne par produit principal) ────────
    desc_path = base + f'_top{top_n}_descriptions.csv'
    DESC_HEADER = [
        'Reference', 'Nom commercial', 'Type', 'Couleur', 'Marque',
        'Composition', 'Description fournisseur',
    ]

    with open(desc_path, 'w', encoding='utf-8-sig', newline='') as fdesc:
        dw = csv.writer(fdesc, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        dw.writerow(DESC_HEADER)

        for root in selected_roots:
            main = all_prods[color_groups[root][0]]
            nom_clean = nom_commercial(
                main['name'], main['brand'], main['prod_type'],
                main['description'], main['color'], inclure_couleur=False,
            )
            comp = ''
            if 'Composition :' in main['description']:
                comp = main['description'].split('Composition :')[-1].strip()

            couleurs = ', '.join(
                _traduire_couleur(all_prods[p]['color']) for p in color_groups[root]
            )

            dw.writerow([
                f"{REF_PREFIX}-{main['pid']}",
                nom_clean,
                main['prod_type'],
                couleurs,
                main['brand'],
                comp,
                main['sdesc'],
            ])

    print(f"→ Fichier descriptions : {desc_path} ({len(selected_roots)} produits)")

    # ── Diagnostic catégories non mappées ─────────────────────────────────
    if _CATEGORIES_NON_MAPPEES:
        print(f"\n⚠️  CATÉGORIES NON MAPPÉES ({len(_CATEGORIES_NON_MAPPEES)}) :")
        for c in sorted(_CATEGORIES_NON_MAPPEES):
            print(f"    → '{c}' (norm: '{_normalize(c)}')")
        print(f"  💡 Ajouter ces entrées dans CATEGORY_MAP pour éviter des catégories parasites")
    else:
        print(f"\n✅ Toutes les catégories sont mappées")

    return csv_path


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    top_n  = DEFAULT_TOP
    coef   = DEFAULT_COEF
    tax_id = DEFAULT_TAX_ID
    colors_csv = None
    positional = []

    i = 0
    while i < len(args):
        if args[i] == '--top' and i + 1 < len(args):
            top_n = int(args[i + 1]); i += 2
        elif args[i] == '--coef' and i + 1 < len(args):
            coef = float(args[i + 1]); i += 2
        elif args[i] == '--taxe' and i + 1 < len(args):
            tax_id = int(args[i + 1]); i += 2
        elif args[i] == '--colors-csv' and i + 1 < len(args):
            colors_csv = args[i + 1]; i += 2
        else:
            positional.append(args[i]); i += 1

    source = positional[0]
    if not os.path.exists(source):
        print(f"ERREUR : fichier introuvable → {source}")
        sys.exit(1)

    run(source, top_n=top_n, coef=coef, tax_id=tax_id, colors_csv=colors_csv)
