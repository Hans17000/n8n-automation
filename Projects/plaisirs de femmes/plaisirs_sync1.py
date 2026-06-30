#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plaisirs_sync.py — Orchestrateur catalogue Plaisirs de Femmes
=============================================================
Version 2.0  |  juin 2026

Unifie tous les scripts du dossier 02-Scripts :
  extract_xml · netoyage · top10_par_categorie · to_prestashop
  matterhorn_to_prestashop · generer_descriptions · mistral

MODES
-----
  python plaisirs_sync.py --server              Dashboard web → http://localhost:8765
  python plaisirs_sync.py --source data.xml     Mode CLI, sortie CSV par défaut
  python plaisirs_sync.py --help                Ce message

OPTIONS CLI (compatibles cron)
-------------------------------
  --source FILE         Fichier XML ou CSV fournisseur Matterhorn (requis hors --server)
  --output MODE         csv | api | db  (défaut : csv)
  --categories CATS     Catégories Matterhorn séparées par virgule  (vide = toutes)
  --top N               Top N produits par catégorie (défaut 10, 0 = tout)
  --coef FLOAT          Coefficient prix wholesale (défaut 2.2)
  --taxe INT            Tax rules ID PrestaShop (défaut 1 = TVA 20 %)
  --ref-prefix STR      Préfixe référence PS (défaut PDF)
  --out FILE            Fichier CSV de sortie (mode csv uniquement)
  --ai                  Active génération descriptions via LM Studio
  --cron                Mode silencieux : pas de stdout, log fichier seulement
  --port INT            Port du dashboard web (défaut 8765)
  --config FILE         Fichier de configuration JSON (défaut config.json)

EXEMPLES CRON
-------------
  # Mise à jour stock chaque nuit à 2h
  0 2 * * *  cd /srv/scripts && python plaisirs_sync.py --source /data/matterhorn.xml --output csv --cron >> logs/nuit.log 2>&1

  # Mise à jour fiches lingerie chaque lundi à 6h
  0 6 * * 1  python plaisirs_sync.py --source /data/matterhorn.xml --output api \\
             --categories "Soutiens-Gorge Push Up,Strings,Culottes" --top 20 --cron

INSTALLATION
------------
  pip install flask requests mysql-connector-python
"""

import argparse
import csv
import json
import logging
import os
import queue
import re
import sys
import threading
import time
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# ── Dépendances optionnelles ─────────────────────────────────────────────────
try:
    from flask import Flask, Response, jsonify, request, send_file, stream_with_context
    FLASK_OK = True
except ImportError:
    FLASK_OK = False

try:
    import mysql.connector
    MYSQL_OK = True
except ImportError:
    MYSQL_OK = False

try:
    import requests as _requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False


# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION PAR DÉFAUT
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG = {
    "prestashop": {
        "url": "https://plaisirs-de-femmes.fr",
        "api_key": "",
        "language_id": 1
    },
    "database": {
        "host": "localhost",
        "port": 3306,
        "name": "prestashop_db",
        "user": "ps_user",
        "password": ""
    },
    "defaults": {
        "coef": 2.2,
        "tax_id": 1,
        "top_per_category": 10,
        "ref_prefix": "PDF",
        "ai_port": 1234,
        "ai_delay": 0.5
    },
    "paths": {
        "output_dir": "./output",
        "log_dir": "./logs"
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
#  MAPPING CATÉGORIES  Matterhorn → PrestaShop
# ═══════════════════════════════════════════════════════════════════════════════

CATEGORY_MAP = {
    # ── Lingerie Intime → Soutiens-Gorge & Parures ───────────────────────────
    # SG de toutes coupes + parures (SG + culotte assortie)
    "Soutiens-Gorge Push Up":               "Accueil->Lingerie Intime->Soutiens-Gorge & Parures",
    "Soutiens-Gorge Balconnet":             "Accueil->Lingerie Intime->Soutiens-Gorge & Parures",
    "Soutiens-Gorge Soft et Semi-Soft":     "Accueil->Lingerie Intime->Soutiens-Gorge & Parures",
    "Lingerie":                             "Accueil->Lingerie Intime->Soutiens-Gorge & Parures",
    # ── Lingerie Intime → Corps & Désirs ─────────────────────────────────────
    # Strings, culottes, shortys, bodies, gaine légère
    "Culottes":                             "Accueil->Lingerie Intime->Corps & Désirs",
    "Strings":                              "Accueil->Lingerie Intime->Corps & Désirs",
    "Shortys, Boxers Femme":                "Accueil->Lingerie Intime->Corps & Désirs",
    "les bretelles":                        "Accueil->Lingerie Intime->Corps & Désirs",
    "Cullotes ew.cullotes et bas":          "Accueil->Lingerie Intime->Corps & Désirs",
    "Culottes, Shortys et Strings Amincissants": "Accueil->Lingerie Intime->Corps & Désirs",
    # ── Lingerie Intime → Corsets & Architecture ─────────────────────────────
    # Corsets, guêpières, bustiers, ensembles sexy, lingerie érotique
    "Corsets et Bodys Femme":               "Accueil->Lingerie Intime->Corsets & Architecture",
    "Corsets, Body Femme, Ceintures Modelantes et Gainantes": "Accueil->Lingerie Intime->Corsets & Architecture",
    "Ensembles Sexy":                       "Accueil->Lingerie Intime->Corsets & Architecture",
    "Bodys, Caracos, Porte-Jarreteles, Corsets, Cullotes Sexy Et Leggins": "Accueil->Lingerie Intime->Corsets & Architecture",
    "Guêpières, Bustiers, Nuisettes et Babydolls": "Accueil->Lingerie Intime->Corsets & Architecture",
    "Lingerie Sexy, Lingerie Érotique":     "Accueil->Lingerie Intime->Corsets & Architecture",
    # ── Nuits & Désirs → Nuisettes & Déshabillés ─────────────────────────────
    # Nuisettes, peignoirs, kimonos, babydolls nuit
    "Nuisettes, Chemises de Nuit":          "Accueil->Nuits & Désirs->Nuisettes & Déshabillés",
    "Peignoirs, Robes de Chambre et Kimonos": "Accueil->Nuits & Désirs->Nuisettes & Déshabillés",
    "Vêtements et Lingerie de Nuit":        "Accueil->Nuits & Désirs->Nuisettes & Déshabillés",
    # ── Nuits & Désirs → Pyjamas & Loungewear ────────────────────────────────
    # Pyjamas premium, ensembles détente de nuit
    "Pyjamas, Ensembles de Nuit":           "Accueil->Nuits & Désirs->Pyjamas & Loungewear",
    # ── Style & Silhouette → Robes & Tenues ──────────────────────────────────
    # Robes, combinaisons, jupes, hauts, pantalons, blazers, maillots de bain
    "Maillots de Bain 1 Pièce":             "Accueil->Style & Silhouette->Robes & Tenues",
    "Maillots de Bain 2 Pièces":            "Accueil->Style & Silhouette->Robes & Tenues",
    "Robes de Plage, Paréos":               "Accueil->Style & Silhouette->Robes & Tenues",
    "Bonnets et chapeaux":                  "Accueil->Style & Silhouette->Robes & Tenues",
    "Foulards et Écharpes":                 "Accueil->Style & Silhouette->Robes & Tenues",
    "Robes de Jour":                        "Accueil->Style & Silhouette->Robes & Tenues",
    "Robes de Soirée":                      "Accueil->Style & Silhouette->Robes & Tenues",
    "Robes de cocktail, Robes formelles":   "Accueil->Style & Silhouette->Robes & Tenues",
    "Combinaisons Femme":                   "Accueil->Style & Silhouette->Robes & Tenues",
    "Jupes":                                "Accueil->Style & Silhouette->Robes & Tenues",
    "Blouses Femme, Tuniques":              "Accueil->Style & Silhouette->Robes & Tenues",
    "Chemises Femme, Blouses Femme":        "Accueil->Style & Silhouette->Robes & Tenues",
    "Chemises Femme":                       "Accueil->Style & Silhouette->Robes & Tenues",
    "Tops Femme, T-shirts, Débardeurs Femme": "Accueil->Style & Silhouette->Robes & Tenues",
    "Maillots de Corps / Tops":             "Accueil->Style & Silhouette->Robes & Tenues",
    "Bodys Femme":                          "Accueil->Style & Silhouette->Robes & Tenues",
    "Tops":                                 "Accueil->Style & Silhouette->Robes & Tenues",
    "Leggings Femme":                       "Accueil->Style & Silhouette->Robes & Tenues",
    "Pantalons femme, Shorts femme":        "Accueil->Style & Silhouette->Robes & Tenues",
    "Pantalons longs":                      "Accueil->Style & Silhouette->Robes & Tenues",
    "Pantalons élégants":                   "Accueil->Style & Silhouette->Robes & Tenues",
    "Pantalons de survêtement femme":       "Accueil->Style & Silhouette->Robes & Tenues",
    "Shorts Femme, Pantacourts, Corsaires Femme": "Accueil->Style & Silhouette->Robes & Tenues",
    "Blazers femme, Gilets femme":          "Accueil->Style & Silhouette->Robes & Tenues",
    "Vestes femme, Manteaux femme":         "Accueil->Style & Silhouette->Robes & Tenues",
    "Sweats et sweat-shirts femme":         "Accueil->Style & Silhouette->Robes & Tenues",
    "Pulls, Chandails, Pullovers, PULLS a COL ROULÉ FEMME ET BOLEROS FEMME": "Accueil->Style & Silhouette->Robes & Tenues",
    "Cardigans Femme, Ponchos":             "Accueil->Style & Silhouette->Robes & Tenues",
    # ── Style & Silhouette → Bas & Collants ──────────────────────────────────
    # Bas, collants, porte-jarretelles, accessoires textiles
    "Collants, Bas":                        "Accueil->Style & Silhouette->Bas & Collants",
    "Gants":                                "Accueil->Style & Silhouette->Bas & Collants",
    # ── Grandes Grâces ────────────────────────────────────────────────────────
    # Grande taille (4XL), maternité
    "Soutiens-Gorge Allaitement, Grossesse et Maternité": "Accueil->Grandes Grâces",
    "Robes de grossesse":                   "Accueil->Grandes Grâces",
    "Tenues Maternite":                     "Accueil->Grandes Grâces",
    "Pantalon grossesse":                   "Accueil->Grandes Grâces",
    "Blouses de maternité":                 "Accueil->Grandes Grâces",
    "Legging grossesse":                    "Accueil->Grandes Grâces",
    "Tunique grossesse":                    "Accueil->Grandes Grâces",
    "Robes taille plus":                    "Accueil->Grandes Grâces",
    "Chemises, Chemisiers, Tuniques grande taille": "Accueil->Grandes Grâces",
    "Pulls, Cardigans Femme Grandes Tailles": "Accueil->Grandes Grâces",
    "T-shrits grandes tailles":             "Accueil->Grandes Grâces",
    "Sweatshirts taille plus":              "Accueil->Grandes Grâces",
    "L`ensemble grandes tailles":           "Accueil->Grandes Grâces",
    # ── Chaussures → Style & Silhouette (import secondaire, non prioritaire) ──
    "Bottes et boots":                      "Accueil->Style & Silhouette->Robes & Tenues",
    "Bottes, Cuissardes":                   "Accueil->Style & Silhouette->Robes & Tenues",
    "Sandales et mules":                    "Accueil->Style & Silhouette->Robes & Tenues",
    "Chausseres de sport":                  "Accueil->Style & Silhouette->Robes & Tenues",
    "Mocassins, Lords":                     "Accueil->Style & Silhouette->Robes & Tenues",
    "Ballerines":                           "Accueil->Style & Silhouette->Robes & Tenues",
    "Chaussons":                            "Accueil->Style & Silhouette->Robes & Tenues",
    "Escarpins":                            "Accueil->Style & Silhouette->Robes & Tenues",
    "Talons aiguilles":                     "Accueil->Style & Silhouette->Robes & Tenues",
    "Escarpins à talons bloc":              "Accueil->Style & Silhouette->Robes & Tenues",
}

# ═══════════════════════════════════════════════════════════════════════════════
#  MAPPING IDs NUMÉRIQUES MATTERHORN → clés CATEGORY_MAP
#  Source : colonne "Categories (x,y,z...)" du CSV prestashop_products_sizesFR.csv
# ═══════════════════════════════════════════════════════════════════════════════
MATTERHORN_CAT_ID = {
    '1001': 'Soutiens-Gorge Push Up',        # Push Up + Balconnet + Semi-Soft
    '1002': 'Strings',
    '1003': 'Shortys, Boxers Femme',
    '1012': 'Nuisettes, Chemises de Nuit',   # couvre aussi Peignoirs & Kimonos
    '1023': 'Pyjamas, Ensembles de Nuit',
    '1038': 'Ensembles Sexy',                # couvre aussi Guêpières & Bustiers
    '1042': 'Robes de Jour',
    '1121': 'Robes de Soirée',
    '1136': 'Strings',                       # ID alternatif Matterhorn
    '1152': 'Culottes',
    '1160': 'Corsets et Bodys Femme',
    '1187': 'Collants, Bas',
}

# Univers regroupés pour le dashboard
UNIVERS = {}
for _k, _v in CATEGORY_MAP.items():
    parts = _v.split('->')
    univers = parts[1] if len(parts) > 1 else 'Autres'
    UNIVERS.setdefault(univers, [])
    if _k not in UNIVERS[univers]:
        UNIVERS[univers].append(_k)


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def slugify(text):
    text = str(text).lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return re.sub(r'-+', '-', text).strip('-')[:120]


def extract_prose(html):
    if not html:
        return ''
    html = re.split(r"<div class=['\"]prod_data", html, 1)[0]
    html = re.split(r"<table", html, 1)[0]
    text = re.sub(r'<br\s*/?>', '\n', html)
    text = re.sub(r'<[^>]+>', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def extract_composition(html):
    if not html:
        return ''
    m = re.search(r"<div class=['\"]prod_data['\"]>(.*?)</div>", html, re.DOTALL)
    if not m:
        return ''
    pairs = re.findall(r'<strong>(.*?)</strong>\s*([\d]+\s*%)', m.group(1))
    return ', '.join(f"{mat.strip()} {pct.strip()}" for mat, pct in pairs)


def short_desc(text, length=500):
    if not text:
        return ''
    t = re.sub(r'<[^>]+>', ' ', str(text))
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > length:
        t = t[:length].rsplit(' ', 1)[0] + '…'
    return t


def _norm(text):
    t = unicodedata.normalize('NFD', str(text))
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower().strip()


_CAT_NORM  = {_norm(k): v for k, v in CATEGORY_MAP.items()}

def _ultra_norm(s):
    import re as _re
    return _re.sub(r'[^a-z0-9 ]', '', s.lower())

_CAT_ULTRA = {_ultra_norm(k): v for k, v in CATEGORY_MAP.items()}


def map_category(category_path):
    if not category_path:
        return "Accueil->Corps & Désirs->Parures d'Exception"
    leaf = category_path.rstrip('/').split('/')[-1].strip()
    if leaf in CATEGORY_MAP:
        return CATEGORY_MAP[leaf]
    n = _norm(leaf)
    if n in _CAT_NORM:
        return _CAT_NORM[n]
    # correspondance partielle
    for k, v in CATEGORY_MAP.items():
        if _norm(k) in n or n in _norm(k):
            return v
    # Fallback ultra : ignore accents/? (encoding cassé ex: Gu?pi?res)
    ul = _ultra_norm(leaf)
    if ul and ul in _CAT_ULTRA:
        return _CAT_ULTRA[ul]
    parts = [p.strip() for p in category_path.strip('/').split('/') if p.strip()]
    return 'Accueil->' + '->'.join(parts)


def compute_price(price_str, coef):
    try:
        return round(float(str(price_str).replace(',', '.')) * coef, 2)
    except Exception:
        return 0.0


def clean_product_name(name, brand='', ptype=''):
    """Transforme 'Chemise manche longue model 44286 Figl' → 'Chemise manche longue Figl'.

    Si on a type + brand séparément, construit directement depuis ces champs.
    Sinon retire le segment 'model XXXXX' du nom brut Matterhorn.
    """
    import re as _re
    # Priorité : construire depuis type + brand si les deux sont renseignés
    if ptype and brand:
        return f"{ptype.strip()} {brand.strip()}"
    # Sinon : nettoyer le nom brut
    if name:
        # Retire "model 12345" ou "model_12345" (insensible à la casse)
        cleaned = _re.sub(r'\s*\bmodel\b\s*\d+\s*', ' ', name, flags=_re.IGNORECASE)
        # Normalise les espaces multiples
        cleaned = _re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    return name or ''


def detect_encoding(path):
    for enc in ('utf-8-sig', 'utf-8', 'latin-1', 'cp1252'):
        try:
            with open(path, 'r', encoding=enc) as f:
                f.read(2048)
            return enc
        except UnicodeDecodeError:
            continue
    return 'utf-8'


# ═══════════════════════════════════════════════════════════════════════════════
#  LOGGER  (console + fichier + queue SSE)
# ═══════════════════════════════════════════════════════════════════════════════

class TaskLogger:
    LEVELS = {'INFO': '\033[0m', 'WARN': '\033[33m', 'ERROR': '\033[31m', 'OK': '\033[32m'}

    def __init__(self, log_dir='./logs', task_id=None, cron=False):
        self.cron  = cron
        self.q     = queue.Queue()
        self.tid   = task_id or datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = os.path.join(log_dir, f"{self.tid}.log")
        handlers = [logging.FileHandler(self.log_path, encoding='utf-8')]
        if not cron:
            handlers.append(logging.StreamHandler(sys.stdout))
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s',
                            handlers=handlers, force=True)
        self._log = logging.getLogger(self.tid)

    def _emit(self, level, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        self.q.put({'ts': ts, 'level': level, 'msg': str(msg)})
        getattr(self._log, level.lower() if level != 'OK' else 'info')(msg)

    def info(self, msg):  self._emit('INFO',  msg)
    def warn(self, msg):  self._emit('WARN',  msg)
    def error(self, msg): self._emit('ERROR', msg)
    def ok(self, msg):    self._emit('OK',    msg)


# ═══════════════════════════════════════════════════════════════════════════════
#  ÉTAT PARTAGÉ  (thread pipeline ↔ Flask)
# ═══════════════════════════════════════════════════════════════════════════════

class TaskState:
    def __init__(self):
        self._lk = threading.Lock()
        self.running = False; self.done = False; self.error = None
        self.progress = 0.0;  self.total = 0;    self.processed = 0
        self.exported = 0;    self.phase = '';   self.output_file = ''
        self.started_at = None; self.finished_at = None

    def update(self, **kw):
        with self._lk:
            for k, v in kw.items():
                setattr(self, k, v)

    def snap(self):
        with self._lk:
            return dict(
                running=self.running, done=self.done, error=self.error,
                progress=round(self.progress * 100, 1),
                total=self.total, processed=self.processed, exported=self.exported,
                phase=self.phase, output_file=self.output_file,
                started_at=self.started_at, finished_at=self.finished_at,
            )


# ═══════════════════════════════════════════════════════════════════════════════
#  PARSEURS
# ═══════════════════════════════════════════════════════════════════════════════

def parse_xml(path, cat_filter=None, log=None):
    """Générateur streaming iterparse XML Matterhorn."""
    if log: log.info(f"Lecture XML : {path}")
    count = 0
    for _, el in ET.iterparse(path, events=('end',)):
        if el.tag != 'product':
            continue
        pid = el.get('id', '').strip()
        if not pid:
            el.clear(); continue

        cat_path = (el.findtext('category_path') or '').strip()
        if cat_filter and not any(f.lower() in cat_path.lower() for f in cat_filter):
            el.clear(); continue

        images = [(i.text or '').strip() for i in el.findall('.//image_url') if (i.text or '').strip()]
        opts = []
        for opt in el.findall('.//option'):
            opts.append({
                'label': (opt.findtext('option_name') or 'Taille unique').strip(),
                'qty':   int(opt.findtext('STOCK') or 0),
                'ean':   (opt.findtext('ean') or '').strip(),
                'sku':   opt.get('id', ''),
            })

        dr = (el.findtext('description') or '').strip()
        p = {
            'id': pid, 'name': (el.findtext('name') or '').strip(),
            'brand': (el.findtext('brand') or '').strip(),
            'category_path': cat_path,
            'color': (el.findtext('color') or '').strip(),
            'type':  (el.findtext('type') or '').strip(),
            'price_raw': (el.findtext('price') or '').strip(),
            'description': extract_prose(dr),
            'composition': extract_composition(dr),
            'images': images, 'options': opts,
        }
        el.clear(); count += 1; yield p

    if log: log.info(f"XML parsé : {count} produits")


def _safe_price(val):
    """Retourne val si c'est un nombre valide, sinon '' (garde contre décalage CSV)."""
    s = str(val).strip().replace(',', '.')
    try:
        float(s)
        return s
    except (ValueError, TypeError):
        return ''


def parse_csv(path, cat_filter=None, log=None):
    """Générateur CSV fournisseur (_net / _net_enrichi / product_feed)."""
    if log: log.info(f"Lecture CSV : {path}")
    enc = detect_encoding(path)
    count = 0
    with open(path, 'r', encoding=enc, errors='replace') as f:
        sample = f.read(4096); f.seek(0)
        # Détecter sur la 1re ligne seulement (les descriptions HTML ont des tabs)
        first_line = sample.split('\n')[0]
        if first_line.count(';') >= first_line.count('\t') and first_line.count(';') >= first_line.count(','):
            sep = ';'
        elif first_line.count('\t') >= first_line.count(','):
            sep = '\t'
        else:
            sep = ','
        reader = csv.DictReader(f, delimiter=sep)
        _first_row = True
        seen_ids = set()          # dédupliquer : les `;` dans les descriptions créent des faux doublons
        for row in reader:
            # ── Diagnostic première ligne : colonnes + valeur sizes ────────────
            if _first_row:
                _first_row = False
                cols = list(reader.fieldnames or [])
                if log:
                    log.info(f"Séparateur détecté : {repr(sep)}")
                    log.info(f"Colonnes CSV ({len(cols)}) : {cols}")
                    log.info(f"sizes_sku_codes 1re ligne : {repr(row.get('sizes_sku_codes'))}")
            # ─────────────────────────────────────────────────────────────────
            pid = (row.get('id') or row.get('ID') or '').strip()
            if not pid: continue
            if pid in seen_ids: continue   # doublon CSV (description avec ';' → décalage colonnes)
            seen_ids.add(pid)

            # ── Filtre actif Matterhorn (colonne 'Active' : 1=actif, 0=inactif) ──
            active_val = (row.get('Active') or row.get('active') or '1').strip()
            if active_val == '0':
                continue

            # ── Catégorie : format simplifié ou natif Matterhorn ─────────────
            cat_raw = (row.get('category_path') or row.get('path') or
                       row.get('boutique_category') or row.get('category') or
                       row.get('Categories (x,y,z...)') or
                       row.get('Categories') or row.get('categories') or '').strip()
            # IDs numériques Matterhorn (ex: "1002" ou "1002,1136") → texte
            if cat_raw and cat_raw[:1].isdigit():
                cat_ids = [c.strip() for c in cat_raw.split(',') if c.strip()]
                cat_path = next((MATTERHORN_CAT_ID[c] for c in cat_ids
                                 if c in MATTERHORN_CAT_ID), '')
            else:
                cat_path = cat_raw
            if cat_filter and not any(f.lower() in cat_path.lower() for f in cat_filter):
                continue

            # ── Images : format image_1..4 OU Matterhorn 'Image URLs (x,y,z...)' ──
            img_urls_raw = (row.get('Image URLs (x,y,z...)') or
                            row.get('images_urls') or row.get('image_urls') or '').strip()
            if img_urls_raw:
                # Filtrer : garder uniquement les URLs valides (http/https)
                images = [u.strip() for u in img_urls_raw.split(',')
                          if u.strip() and u.strip().lower().startswith('http')][:4]
            else:
                images = [row.get(c, '').strip()
                          for c in ('image_1', 'image_2', 'image_3', 'image_4')
                          if row.get(c, '').strip()]

            # ── Tailles + stock ──────────────────────────────────────────────
            # Format : "EU XL | FR 44:5,EU L | FR 42:2"  (label:quantité)
            # size_table_and_fabric_content = données tailles réelles Matterhorn
            sizes_str = (row.get('sizes_sku_codes') or row.get('sizes_stock') or
                         row.get('size_table_and_fabric_content') or
                         row.get('stock') or row.get('tailles_stock') or
                         row.get('sizes') or row.get('disponibilite') or '').strip()
            # Si HTML ou texte non parseable, vider (le format valide contient ':')
            if sizes_str and ':' not in sizes_str:
                sizes_str = ''
            opts = []
            for e in sizes_str.split(','):
                if ':' in e:
                    lbl, qs = e.rsplit(':', 1)
                    lbl = lbl.strip()
                    try: qty = int(qs.strip())
                    except: qty = 0
                    opts.append({'label': lbl, 'qty': qty, 'ean': '', 'sku': ''})

            dr = (row.get('description') or row.get('Description') or '').strip()
            p = {
                'id':       pid,
                'brand':    (row.get('brand') or row.get('Manufacturer') or '').strip(),
                'type':     (row.get('type') or row.get('Type') or '').strip(),
                'category_path': cat_path,
                'color':    (row.get('color') or '').strip(),
                'other_colors':   (row.get('other_colors') or '').strip(),
                'products_in_set': (row.get('products_in_set') or '').strip(),
                'price_raw': _safe_price(row.get('wholesale_price') or
                                         row.get('Price netto') or row.get('price') or ''),
                'description': extract_prose(dr),
                'composition': extract_composition(dr),
                'images': images, 'options': opts,
            }
            # Nom propre : retire "model XXXXX" ou construit depuis type+brand
            raw_name = (row.get('name') or row.get('Name *') or row.get('Name') or '').strip()
            p['name'] = clean_product_name(raw_name, p.get('brand',''), p.get('type',''))
            count += 1; yield p

    if log: log.info(f"CSV parsé : {count} produits")


def parse_stock_csv(path, log=None):
    """Parse Matterhorn prestashop_stock.csv → dict {matterhorn_id: [(label, qty), ...]}

    Format (séparateur ';') :
      "Product ID*";"Attribute (Name:Type:Position)*";"Value (Value:Position)*";Quantity;Index
      179165;Size:select:0;EU 65E | FR 80E:0;1;"Axami_Biustonosz_..."
    """
    if not path or not os.path.exists(str(path)):
        if log: log.warning(f"Stock CSV introuvable : {path}")
        return {}
    enc = detect_encoding(path)
    result = {}
    try:
        with open(path, 'r', encoding=enc, errors='replace') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                pid = (row.get('Product ID*') or '').strip()
                if not pid:
                    continue
                val_field = (row.get('Value (Value:Position)*') or '').strip()
                # "EU L | FR 42:0"  →  label = tout avant le dernier ':'
                label = val_field.rsplit(':', 1)[0].strip() if ':' in val_field else val_field
                try:
                    qty = int((row.get('Quantity') or '0').strip())
                except ValueError:
                    qty = 0
                result.setdefault(pid, []).append({'label': label, 'qty': qty})
    except Exception as e:
        if log: log.error(f"Erreur lecture stock CSV : {e}")
        return {}
    if log:
        log.info(f"Stock CSV chargé : {len(result)} produits Matterhorn avec déclinaisons")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  SCORING & SÉLECTION
# ═══════════════════════════════════════════════════════════════════════════════

def score_product(p):
    s  = sum(1 for o in p.get('options', []) if o.get('qty', 0) > 0)   # tailles en stock
    s += 3 if len(p.get('images', [])) >= 4 else 0                      # images
    s += 2 if len(p.get('description', '')) > 200 else 0                # desc riche
    return s


def select_top(products, top_n=10, log=None):
    if not top_n:
        return list(products)
    by_cat = {}
    for p in products:
        cat = map_category(p['category_path'])
        by_cat.setdefault(cat, []).append(p)
    sel = []
    for cat, prods in sorted(by_cat.items()):
        ranked = sorted(prods, key=score_product, reverse=True)
        top = ranked[:top_n]
        sel.extend(top)
        if log: log.info(f"  [{cat.split('->')[-1]}] {len(prods)} dispo → {len(top)} sélectionnés")
    return sel


# ═══════════════════════════════════════════════════════════════════════════════
#  FAMILLES COULEUR
# ═══════════════════════════════════════════════════════════════════════════════

def build_color_families(selected_products, all_by_id=None):
    """Regroupe les produits sélectionnés en familles couleur (Union-Find).

    Utilise un algorithme Union-Find pour garantir que chaque produit
    appartient à UNE SEULE famille, même si Matterhorn utilise des
    références croisées non symétriques dans other_colors.

    Retourne : liste de {'main': p, 'members': [p,…], 'multi_color': bool}
    """
    _by_id = all_by_id or {p['id']: p for p in selected_products}
    # Dédupliquer par ID (sécurité supplémentaire)
    _seen = set()
    selected_products = [p for p in selected_products
                         if not (p['id'] in _seen or _seen.add(p['id']))]
    sel_ids = {p['id'] for p in selected_products}

    # ── Union-Find ────────────────────────────────────────────────────────────
    parent = {pid: pid for pid in sel_ids}

    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], x)   # compression de chemin
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        # Racine = ID le plus petit (déterminisme)
        if ra < rb:
            parent[rb] = ra
        else:
            parent[ra] = rb

    # 1re passe : construire les unions via other_colors
    for p in selected_products:
        pid = p['id']
        other_raw = (p.get('other_colors') or '').strip()
        other_ids = [x.strip() for x in other_raw.split(',')
                     if x.strip() and x.strip() != pid] if other_raw else []
        for oid in other_ids:
            if oid in sel_ids:          # ne lier que les produits sélectionnés
                union(pid, oid)

    # 2e passe : regrouper par racine
    groups = {}                         # root_id → [p, …]
    for p in selected_products:
        root = find(p['id'])
        groups.setdefault(root, []).append(p)

    # Construire les familles — main = produit dont l'id == root
    families = []
    by_id_sel = {p['id']: p for p in selected_products}
    for root, members in groups.items():
        members.sort(key=lambda p: p['id'])   # ordre stable, root en 1er
        main = by_id_sel.get(root, members[0])
        families.append({
            'main': main,
            'members': members,
            'multi_color': len(members) > 1,
        })

    return families


# ═══════════════════════════════════════════════════════════════════════════════
#  EXPORT CSV Simple Import PrestaShop 8
# ═══════════════════════════════════════════════════════════════════════════════

PS_HEADER = [
    'ID','Active (0/1)','Name *[fr-FR]','Categories (x,y,z,...)',
    'Price tax excl.','Tax rules ID','Wholesale price','Reference #',
    'EAN13','Brand','Short description[fr-FR]','Description[fr-FR]',
    'URL rewritten[fr-FR]','Image URLs (x,y,z,...)',
    'Attribute (Name:Type:Position)*','Value (Value:Position)*',
    'Combination Reference','Quantity','Supplier reference',
]


def export_csv(products, out_path, coef=2.2, tax_id=1, prefix='PDF', log=None, state=None):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    total = len(products); rows = 0

    with open(out_path, 'w', encoding='utf-8-sig', newline='') as fout:
        w = csv.writer(fout, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        w.writerow(PS_HEADER)

        for i, p in enumerate(products):
            ref   = f"{prefix}-{p['id']}"
            price = compute_price(p['price_raw'], coef)
            cat   = map_category(p['category_path'])
            desc  = p.get('description', '')
            comp  = p.get('composition', '')
            if comp: desc += f"\n\nComposition : {comp}"
            sdesc = short_desc(desc)
            url   = slugify(f"{p.get('type','')} {p.get('brand','')} {p.get('color','')} {p['id']}")
            imgs  = ','.join(p.get('images', []))
            opts  = p.get('options', []) or [{'label':'Taille unique','qty':0,'ean':'','sku':ref}]

            for j, opt in enumerate(opts):
                sku = opt.get('sku') or f"{ref}-{j}"
                if j == 0:
                    w.writerow(['',1,p['name'],cat,price,tax_id,p['price_raw'],
                                ref,opt['ean'],p.get('brand',''),sdesc,desc,url,imgs,
                                'Taille',f"{opt['label']}:{j}",sku,opt['qty'],sku])
                else:
                    w.writerow(['','',p['name'],'','','','',ref,opt['ean'],'','','','','',
                                'Taille',f"{opt['label']}:{j}",sku,opt['qty'],sku])
                rows += 1

            if state:
                state.update(processed=i+1, exported=i+1,
                             progress=(i+1)/max(total,1),
                             phase=f"Export CSV ({i+1}/{total})")
            if log and (i+1) % 500 == 0:
                log.info(f"  CSV {i+1}/{total} produits ({rows} lignes)")

    if log: log.ok(f"CSV généré : {out_path}  [{rows} lignes / {total} produits]")
    return rows


# ═══════════════════════════════════════════════════════════════════════════════
#  EXPORT API PrestaShop WebService
# ═══════════════════════════════════════════════════════════════════════════════

def export_api(products, ps_url, api_key, lang_id=1, coef=2.2, tax_id=1,
               prefix='PDF', log=None, state=None):
    if not REQUESTS_OK:
        if log: log.error("pip install requests  (requis pour mode api)")
        return 0

    base = ps_url.rstrip('/') + '/api'
    auth = (api_key, '')
    created = updated = errors = 0; total = len(products)

    for i, p in enumerate(products):
        ref   = f"{prefix}-{p['id']}"
        price = compute_price(p['price_raw'], coef)
        desc  = p.get('description', '')
        sdesc = short_desc(desc)

        if log: log.info(f"  [{i+1}/{total}] {ref}  {p['name'][:45]}")

        try:
            r = _requests.get(f"{base}/products",
                              params={'filter[reference]': ref, 'output_format':'JSON'},
                              auth=auth, timeout=20)
            existing = r.json().get('products', [])

            xml_body = (
                f'<?xml version="1.0" encoding="UTF-8"?>'
                f'<prestashop xmlns:xlink="http://www.w3.org/1999/xlink"><product>'
                f'<active>1</active><reference>{ref}</reference>'
                f'<price>{price}</price>'
                f'<id_tax_rules_group>{tax_id}</id_tax_rules_group>'
                f'<wholesale_price>{p["price_raw"]}</wholesale_price>'
                f'<name><language id="{lang_id}"><![CDATA[{p["name"]}]]></language></name>'
                f'<description><language id="{lang_id}"><![CDATA[{desc}]]></language></description>'
                f'<description_short><language id="{lang_id}"><![CDATA[{sdesc}]]></language></description_short>'
                f'<link_rewrite><language id="{lang_id}">{slugify(p["name"])}-{p["id"]}</language></link_rewrite>'
                f'<manufacturer_name>{p.get("brand","")}</manufacturer_name>'
                f'</product></prestashop>'
            ).encode('utf-8')
            hdrs = {'Content-Type': 'application/xml'}

            if existing:
                ps_id = existing[0]['id']
                r = _requests.put(f"{base}/products/{ps_id}", data=xml_body, auth=auth, headers=hdrs, timeout=30)
                if r.ok: updated += 1
                else:
                    errors += 1
                    if log: log.error(f"  MàJ {ref} : HTTP {r.status_code}")
            else:
                r = _requests.post(f"{base}/products", data=xml_body, auth=auth, headers=hdrs, timeout=30)
                if r.ok: created += 1
                else:
                    errors += 1
                    if log: log.error(f"  Création {ref} : HTTP {r.status_code}")

        except Exception as exc:
            errors += 1
            if log: log.error(f"  {ref} : {exc}")

        if state:
            state.update(processed=i+1, exported=created+updated,
                         progress=(i+1)/max(total,1),
                         phase=f"API PS ({i+1}/{total})")
        time.sleep(0.2)

    if log: log.ok(f"API : {created} créés, {updated} mis à jour, {errors} erreurs")
    return created + updated


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS COMBINAISONS PrestaShop (attributs / déclinaisons)
# ═══════════════════════════════════════════════════════════════════════════════

_PS_HAS_PRODUCT_TYPE = None  # bool|None — cache vérifié une seule fois par session

def _get_ps_has_product_type(cur):
    """Détecte si ps_product a la colonne product_type (PS 8.1+).
    Résultat mis en cache pour éviter un SHOW COLUMNS par produit.
    """
    global _PS_HAS_PRODUCT_TYPE
    if _PS_HAS_PRODUCT_TYPE is None:
        cur.execute("SHOW COLUMNS FROM ps_product LIKE 'product_type'")
        _PS_HAS_PRODUCT_TYPE = cur.fetchone() is not None
    return _PS_HAS_PRODUCT_TYPE


def _ensure_attribute_group(cur, conn, name='Taille', id_shop=1):
    """Renvoie l'id_attribute_group existant pour 'name', ou en crée un."""
    cur.execute(
        "SELECT id_attribute_group FROM ps_attribute_group_lang "
        "WHERE name=%s AND id_lang=1", (name,))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute(
        "INSERT INTO ps_attribute_group(is_color_group,group_type,position) "
        "VALUES(0,'select',0)")
    gid = cur.lastrowid
    cur.execute(
        "INSERT INTO ps_attribute_group_lang(id_attribute_group,id_lang,name,public_name) "
        "VALUES(%s,1,%s,%s)", (gid, name, name))
    cur.execute(
        "INSERT IGNORE INTO ps_attribute_group_shop(id_attribute_group,id_shop) "
        "VALUES(%s,%s)", (gid, id_shop))
    conn.commit()
    return gid


def _ensure_attribute(cur, conn, gid, value, id_shop=1):
    """Renvoie l'id_attribute existant pour (gid, value), ou en crée un."""
    cur.execute(
        "SELECT a.id_attribute FROM ps_attribute a "
        "JOIN ps_attribute_lang al ON a.id_attribute=al.id_attribute "
        "WHERE al.name=%s AND a.id_attribute_group=%s AND al.id_lang=1",
        (value, gid))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute(
        "INSERT INTO ps_attribute(id_attribute_group,color,position) "
        "VALUES(%s,'',0)", (gid,))
    aid = cur.lastrowid
    cur.execute(
        "INSERT INTO ps_attribute_lang(id_attribute,id_lang,name) "
        "VALUES(%s,1,%s)", (aid, value))
    cur.execute(
        "INSERT IGNORE INTO ps_attribute_shop(id_attribute,id_shop) "
        "VALUES(%s,%s)", (aid, id_shop))
    conn.commit()
    return aid


def _upsert_combinations(cur, conn, ps_id, ref, combos, id_shop=1):
    """Crée ou recrée les déclinaisons couleur × taille d'un produit PS.

    combos : liste de dicts avec les clés :
        size  (str)  — libellé taille, ex. "EU 36 | FR 38"
        qty   (int)  — stock
        color (str)  — libellé couleur (vide si produit mono-couleur)
        sku   (str)  — référence déclinaison

    Si plusieurs couleurs distinctes → groupe Couleur + groupe Taille.
    Si une seule couleur (ou aucune) → groupe Taille uniquement.
    Purge systématique avant réinsertion propre.
    """
    if not combos:
        return

    # ── Déterminer si on a plusieurs couleurs distinctes ─────────────────────
    colors = list(dict.fromkeys(
        c.get('color', '').strip() for c in combos if c.get('color', '').strip()
    ))
    use_colors = len(colors) > 1

    gid_size  = _ensure_attribute_group(cur, conn, 'Taille',  id_shop=id_shop)
    gid_color = _ensure_attribute_group(cur, conn, 'Couleur', id_shop=id_shop) if use_colors else None

    # ── Purge des déclinaisons existantes ─────────────────────────────────────
    cur.execute(
        "SELECT id_product_attribute FROM ps_product_attribute WHERE id_product=%s",
        (ps_id,))
    old_pa_ids = [r[0] for r in cur.fetchall()]
    if old_pa_ids:
        fmt = ','.join(['%s'] * len(old_pa_ids))
        cur.execute(
            f"DELETE FROM ps_product_attribute_combination "
            f"WHERE id_product_attribute IN ({fmt})", old_pa_ids)
        cur.execute(
            f"DELETE FROM ps_product_attribute_shop "
            f"WHERE id_product_attribute IN ({fmt})", old_pa_ids)
        cur.execute(
            "DELETE FROM ps_stock_available "
            "WHERE id_product=%s AND id_product_attribute != 0", (ps_id,))
        cur.execute(
            "DELETE FROM ps_product_attribute WHERE id_product=%s", (ps_id,))
        conn.commit()

    # ── Insertion des nouvelles déclinaisons ──────────────────────────────────
    first_pa_id = None
    for j, combo in enumerate(combos):
        # Compatibilité ancienne clé 'label' (taille seule)
        size_label  = (combo.get('size') or combo.get('label') or 'Taille unique').strip()
        color_label = (combo.get('color') or '').strip()
        qty         = int(combo.get('qty') or 0)
        sku         = combo.get('sku') or f"{ref}-{j}"

        aid_size  = _ensure_attribute(cur, conn, gid_size, size_label, id_shop=id_shop)
        aid_color = (
            _ensure_attribute(cur, conn, gid_color, color_label, id_shop=id_shop)
            if use_colors and color_label else None
        )

        default_on = 1 if j == 0 else None

        cur.execute(
            "INSERT INTO ps_product_attribute"
            "(id_product,reference,price,weight,ecotax,"
            " unit_price_impact,minimal_quantity,default_on,"
            " available_date,low_stock_threshold,low_stock_alert) "
            "VALUES(%s,%s,0,0,0,0,1,%s,NULL,0,0)",
            (ps_id, sku, default_on))
        pa_id = cur.lastrowid
        if j == 0:
            first_pa_id = pa_id

        # Liaison boutique — obligatoire en PS8
        cur.execute(
            "INSERT IGNORE INTO ps_product_attribute_shop"
            "(id_product_attribute,id_product,id_shop,price,ecotax,weight,"
            " unit_price_impact,minimal_quantity,default_on,"
            " low_stock_threshold,low_stock_alert) "
            "VALUES(%s,%s,%s,0,0,0,0,1,%s,NULL,0)",
            (pa_id, ps_id, id_shop, default_on))

        # Liaison attribut taille (toujours)
        cur.execute(
            "INSERT IGNORE INTO ps_product_attribute_combination"
            "(id_attribute,id_product_attribute) VALUES(%s,%s)",
            (aid_size, pa_id))

        # Liaison attribut couleur (si multi-couleurs)
        if aid_color:
            cur.execute(
                "INSERT IGNORE INTO ps_product_attribute_combination"
                "(id_attribute,id_product_attribute) VALUES(%s,%s)",
                (aid_color, pa_id))

        # Stock de la déclinaison
        cur.execute(
            "INSERT INTO ps_stock_available"
            "(id_product,id_product_attribute,id_shop,id_shop_group,"
            " quantity,depends_on_stock,out_of_stock,location,reserved_quantity) "
            "VALUES(%s,%s,%s,0,%s,0,2,'',0) "
            "ON DUPLICATE KEY UPDATE quantity=%s",
            (ps_id, pa_id, id_shop, qty, qty))

    # ── Mettre à jour le produit parent ───────────────────────────────────────
    if _get_ps_has_product_type(cur):
        cur.execute(
            "UPDATE ps_product "
            "SET product_type='combinations', cache_default_attribute=%s "
            "WHERE id_product=%s",
            (first_pa_id, ps_id))
    else:
        cur.execute(
            "UPDATE ps_product SET cache_default_attribute=%s "
            "WHERE id_product=%s",
            (first_pa_id, ps_id))

    cur.execute(
        "UPDATE ps_product_shop SET cache_default_attribute=%s "
        "WHERE id_product=%s AND id_shop=%s",
        (first_pa_id, ps_id, id_shop))

    try:
        cur.execute(
            "UPDATE ps_product_shop SET cache_has_attributes=1 "
            "WHERE id_product=%s AND id_shop=%s", (ps_id, id_shop))
    except Exception:
        pass

    cur.execute(
        "INSERT INTO ps_stock_available"
        "(id_product,id_product_attribute,id_shop,id_shop_group,"
        " quantity,depends_on_stock,out_of_stock,location,reserved_quantity) "
        "VALUES(%s,0,%s,0,0,0,2,'',0) "
        "ON DUPLICATE KEY UPDATE quantity=0",
        (ps_id, id_shop))
    conn.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  EXPORT BDD MySQL directe
# ═══════════════════════════════════════════════════════════════════════════════

def _download_ps_image(cur, conn, ps_id, img_urls, ps_img_dir, log=None):
    """Télécharge les images Matterhorn dans img/p/…/ et insère ps_image, ps_image_lang, ps_image_shop."""
    if not REQUESTS_OK:
        if log: log.warn("requests non installé — images ignorées")
        return
    if not ps_img_dir or not img_urls:
        return
    img_root = Path(ps_img_dir)

    # Skip si images déjà présentes pour ce produit (re-run / couleurs multiples)
    cur.execute("SELECT COUNT(*) FROM ps_image WHERE id_product=%s", (ps_id,))
    if cur.fetchone()[0] > 0:
        return

    cover_done = False
    for rank, url in enumerate(img_urls[:4], start=1):
        if not url:
            continue
        try:
            r = _requests.get(url, timeout=6)
            if r.status_code != 200:
                continue
            if not cover_done:
                # Première image = cover
                cur.execute(
                    "INSERT IGNORE INTO ps_image (id_product, position, cover) VALUES (%s, %s, 1)",
                    (ps_id, rank))
                img_id = cur.lastrowid
                if not img_id:          # IGNORE a absorbé un doublon
                    cover_done = True
                    continue
                cur.execute(
                    "INSERT IGNORE INTO ps_image_shop (id_image, id_shop, cover) VALUES (%s, 1, 1)",
                    (img_id,))
                cover_done = True
            else:
                # Images suivantes : pas de colonne cover (évite 0 et NULL ambigus)
                cur.execute(
                    "INSERT IGNORE INTO ps_image (id_product, position) VALUES (%s, %s)",
                    (ps_id, rank))
                img_id = cur.lastrowid
                if not img_id:
                    continue
                cur.execute(
                    "INSERT IGNORE INTO ps_image_shop (id_image, id_shop, cover) VALUES (%s, 1, 0)",
                    (img_id,))
            cur.execute(
                "INSERT IGNORE INTO ps_image_lang (id_image, id_lang, legend) VALUES (%s, 1, '')",
                (img_id,))
            # Structure PS : img/p/A/B/C/…/id.jpg
            parts = list(str(img_id))
            img_dir = img_root.joinpath(*parts)
            img_dir.mkdir(parents=True, exist_ok=True)
            (img_dir / f"{img_id}.jpg").write_bytes(r.content)
            conn.commit()
        except Exception as e:
            if log: log.warn(f"  Image rank={rank} {url} : {e}")


def export_db(families, db_cfg, coef=2.2, tax_id=1, prefix='PDF', log=None, state=None,
              stock_dict=None, ps_img_dir=None):
    """Exporte les familles couleur vers la BDD PrestaShop.

    families : liste de {'main': product, 'members': [p,…], 'multi_color': bool}
    Pour chaque famille :
      - Upsert le produit PS principal (couleur 1 / référence maîtresse)
      - Construit les combos couleur × taille depuis tous les membres
      - Crée les déclinaisons via _upsert_combinations
      - Désactive les produits PS secondaires (autres couleurs devenues des déclinaisons)
    """
    if not MYSQL_OK:
        if log: log.error("pip install mysql-connector-python  (requis pour mode db)")
        return 0
    try:
        conn = mysql.connector.connect(**db_cfg)
        cur  = conn.cursor()
    except Exception as e:
        if log: log.error(f"Connexion BDD échouée : {e}")
        return 0

    ins = upd = err = 0
    stock_dict = stock_dict or {}
    cat_cache  = {}        # leaf_name → id_category PS (mis en cache par boucle)
    total = len(families)

    if log:
        n_multi   = sum(1 for f in families if f['multi_color'])
        n_members = sum(len(f['members']) for f in families)
        log.info(f"Familles couleur : {total}  ({n_multi} multi-couleurs, {n_members} SKU Matterhorn)")
        if stock_dict:
            log.info(f"Stock CSV actif : {len(stock_dict)} produits Matterhorn disponibles")

    for i, fam in enumerate(families):
        main_p    = fam['main']
        members   = fam['members']
        ref       = f"{prefix}-{main_p['id']}"
        price     = compute_price(main_p['price_raw'], coef)
        price_raw = main_p['price_raw'].strip() if main_p['price_raw'] else ''
        try:
            float(price_raw.replace(',', '.'))
            wholesale = price_raw
        except (ValueError, AttributeError):
            wholesale = '0'
        desc = main_p.get('description', '')

        try:
            # ── Upsert produit principal ──────────────────────────────────────
            cur.execute("SELECT id_product FROM ps_product WHERE reference=%s", (ref,))
            row = cur.fetchone()
            if row:
                ps_id = row[0]
                cur.execute(
                    "UPDATE ps_product "
                    "SET price=%s,wholesale_price=%s,active=1,date_upd=NOW() "
                    "WHERE id_product=%s",
                    (price, wholesale, ps_id))
                cur.execute(
                    "UPDATE ps_product_lang SET name=%s, link_rewrite=%s "
                    "WHERE id_product=%s AND id_lang=1",
                    (main_p['name'],
                     (slugify(main_p['name']) + '-' + str(main_p['id']))[:128],
                     ps_id))
                cur.execute(
                    "UPDATE ps_product_lang SET description=%s,description_short=%s "
                    "WHERE id_product=%s AND id_lang=1 "
                    "AND (description IS NULL OR description='')",
                    (desc, short_desc(desc), ps_id))
                upd += 1
            else:
                cur.execute(
                    "INSERT INTO ps_product"
                    "(reference,price,wholesale_price,active,id_tax_rules_group,date_add,date_upd) "
                    "VALUES(%s,%s,%s,1,%s,NOW(),NOW())",
                    (ref, price, wholesale, tax_id))
                ps_id = cur.lastrowid
                cur.execute(
                    "INSERT INTO ps_product_lang"
                    "(id_product,id_lang,id_shop,name,description,description_short,link_rewrite) "
                    "VALUES(%s,1,1,%s,%s,%s,%s)",
                    (ps_id, main_p['name'], desc, short_desc(desc),
                     (slugify(main_p['name']) + '-' + str(main_p['id']))[:128]))
                ins += 1

            # ── ps_product_shop (PS8 : obligatoire pour l'affichage boutique) ─
            cur.execute(
                "INSERT INTO ps_product_shop"
                " (id_product,id_shop,id_tax_rules_group,price,wholesale_price,"
                "  active,date_add,date_upd)"
                " VALUES(%s,1,%s,%s,%s,1,NOW(),NOW())"
                " ON DUPLICATE KEY UPDATE"
                "  active=1,price=%s,wholesale_price=%s,date_upd=NOW()",
                (ps_id, tax_id, price, wholesale, price, wholesale))

            # ── Catégorie PS (ps_category_product + id_category_default) ─────
            raw_cat = map_category(main_p.get('category_path', ''))
            leaf    = raw_cat.split('->')[-1].strip() if '->' in (raw_cat or '') else (raw_cat or '').strip()
            if leaf:
                if leaf not in cat_cache:
                    cur.execute(
                        "SELECT c.id_category FROM ps_category c "
                        "JOIN ps_category_lang cl ON cl.id_category=c.id_category "
                        "WHERE cl.name=%s AND cl.id_lang=1 AND c.active=1 "
                        "ORDER BY c.level_depth DESC LIMIT 1",
                        (leaf,))
                    row = cur.fetchone()
                    cat_cache[leaf] = row[0] if row else None
                cat_id = cat_cache.get(leaf)
                if cat_id:
                    cur.execute(
                        "INSERT IGNORE INTO ps_category_product"
                        " (id_category, id_product, position) VALUES (%s, %s, 0)",
                        (cat_id, ps_id))
                    cur.execute(
                        "UPDATE ps_product SET id_category_default=%s WHERE id_product=%s",
                        (cat_id, ps_id))
                    cur.execute(
                        "UPDATE ps_product_shop SET id_category_default=%s"
                        " WHERE id_product=%s AND id_shop=1",
                        (cat_id, ps_id))
                elif log:
                    if not hasattr(export_db, '_cat_warned'):
                        export_db._cat_warned = set()
                    if leaf not in export_db._cat_warned:
                        log.warn(f"  Catégorie PS introuvable : '{leaf}' — créer la catégorie dans l'admin PS")
                        export_db._cat_warned.add(leaf)

            # ── Images PS ────────────────────────────────────────────────────
            img_urls_to_dl = main_p.get('images', [])
            if log: log.info(f"  Images : ps_img_dir={'OUI' if ps_img_dir else 'NON'} | {len(img_urls_to_dl)} URL(s)")
            if ps_img_dir and img_urls_to_dl:
                _download_ps_image(cur, conn, ps_id, img_urls_to_dl, ps_img_dir, log)
            elif ps_img_dir and not img_urls_to_dl:
                if log: log.warn(f"  Pas d'URLs images pour produit {ps_id}")

            # ── Construire les combos couleur × taille ────────────────────────
            multi_color = fam['multi_color']
            # Log diagnostic pour les familles multi-couleurs (1 fois sur 500)
            if multi_color and log and (i % 500 == 0):
                clrs = [m.get('color','') for m in members]
                log.info(f"  Famille {ref} : {len(members)} membres, couleurs={clrs}")
            combos = []
            for member in members:
                color_label = (member.get('color') or '').strip() if multi_color else ''
                sizes = stock_dict.get(member['id']) or member.get('options', [])
                m_ref = f"{prefix}-{member['id']}"
                for k, sz in enumerate(sizes):
                    size_label = (sz.get('label') or sz.get('size') or 'Taille unique').strip()
                    combos.append({
                        'color': color_label,
                        'size':  size_label,
                        'qty':   int(sz.get('qty') or 0),
                        'sku':   f"{m_ref}-{k}",
                    })

            if combos:
                _upsert_combinations(cur, conn, ps_id, ref, combos)
            else:
                cur.execute(
                    "INSERT INTO ps_stock_available"
                    "(id_product,id_product_attribute,id_shop,id_shop_group,"
                    " quantity,depends_on_stock,out_of_stock,location,reserved_quantity) "
                    "VALUES(%s,0,1,0,5,0,2,'',0) "
                    "ON DUPLICATE KEY UPDATE quantity=GREATEST(quantity,5)",
                    (ps_id,))

            # ── Désactiver les produits PS secondaires (ex-couleurs séparées) ─
            if multi_color:
                for sec in members[1:]:
                    if sec['id'] == main_p['id']:
                        if log: log.error(f"  BUG auto-désactivation: {ref} → ignoré")
                        continue
                    try:
                        cur.execute(
                            "UPDATE ps_product SET active=0 WHERE reference=%s",
                            (f"{prefix}-{sec['id']}",))
                        cur.execute(
                            "UPDATE ps_product_shop psh"
                            " JOIN ps_product p ON p.id_product=psh.id_product"
                            " SET psh.active=0"
                            " WHERE p.reference=%s AND psh.id_shop=1",
                            (f"{prefix}-{sec['id']}",))
                    except Exception:
                        pass

            conn.commit()

        except Exception as e:
            err += 1; conn.rollback()
            if log: log.error(f"  DB {ref} : {e}")

        if state:
            state.update(processed=i+1, exported=ins+upd,
                         progress=(i+1)/max(total, 1),
                         phase=f"DB MySQL ({i+1}/{total})")

    if log: log.ok(f"DB : {ins} insérés, {upd} mis à jour, {err} erreurs")

    # ── Diagnostic pré-safety-pass ────────────────────────────────────────────
    try:
        cur.execute(
            "SELECT COUNT(*) FROM ps_product "
            "WHERE reference LIKE %s AND active=0", (f"{prefix}-%",))
        cnt_before = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM ps_product WHERE reference LIKE %s", (f"{prefix}-%",))
        cnt_total = cur.fetchone()[0]
        print(f"[SAFETY-PRE] {cnt_before}/{cnt_total} PDF produits active=0 avant pass", flush=True)
        if log: log.info(f"[SAFETY-PRE] {cnt_before}/{cnt_total} produits active=0 avant pass")

        # Vérifier les triggers MySQL qui pourraient réinitialiser active
        cur.execute("SHOW TRIGGERS LIKE 'ps_product'")
        triggers = cur.fetchall()
        if triggers:
            print(f"[SAFETY-TRIGGERS] {len(triggers)} triggers sur ps_product !", flush=True)
            for t in triggers:
                print(f"  → {t[0]} {t[1]} {t[2]}: {str(t[3])[:80]}", flush=True)
            if log: log.error(f"[SAFETY] {len(triggers)} TRIGGERS MySQL trouvés sur ps_product !")
        else:
            print("[SAFETY-TRIGGERS] Aucun trigger sur ps_product", flush=True)

        # Vérifier les doublons de référence
        cur.execute(
            "SELECT reference, COUNT(*) as n FROM ps_product "
            "WHERE reference LIKE %s GROUP BY reference HAVING n > 1 LIMIT 5",
            (f"{prefix}-%",))
        dupes = cur.fetchall()
        if dupes:
            print(f"[SAFETY-DUPES] {len(dupes)} références en double ! ex: {dupes[:2]}", flush=True)
            if log: log.error(f"[SAFETY] Références en double détectées : {dupes[:3]}")
    except Exception as e:
        print(f"[SAFETY-PRE] Erreur diagnostic : {e}", flush=True)

    # ── Safety pass : remet active=1 sur tous les mains ──────────────────────
    print(f"[SAFETY-PASS] Démarrage sur {len(families)} familles…", flush=True)
    safety_fixed = 0
    try:
        for fam in families:
            mref = f"{prefix}-{fam['main']['id']}"
            cur.execute(
                "UPDATE ps_product SET active=1 WHERE reference=%s AND active=0",
                (mref,))
            if cur.rowcount:
                safety_fixed += 1
        conn.commit()
        print(f"[SAFETY-PASS] Terminé : {safety_fixed}/{len(families)} mains remis active=1", flush=True)
        if log:
            if safety_fixed:
                log.warn(f"Safety pass: {safety_fixed}/{len(families)} mains remis active=1")
            else:
                log.ok("Safety pass OK — aucun main n'etait reste a 0")
    except Exception as e:
        print(f"[SAFETY-PASS] ERREUR : {e}", flush=True)
        if log: log.error(f"Safety pass erreur : {e}")
        conn.rollback()

    cur.close(); conn.close()
    return ins + upd


# ═══════════════════════════════════════════════════════════════════════════════
#  GÉNÉRATION DESCRIPTIONS IA  (LM Studio / OpenAI-compatible)
# ═══════════════════════════════════════════════════════════════════════════════

_SYS_AI = ("Tu es rédactrice pour une boutique de lingerie haut de gamme. "
           "Ton chic, sensuel, concret. Pas de superlatifs creux, pas d'émojis. "
           "Interdits : parfait, idéal, offrir, sublimer.")

_USR_AI = ("Produit : {nom}\nCouleur : {couleur}\nMatière : {comp}\nDétails : {desc}\n\n"
           "Réponds STRICTEMENT en JSON sans autre texte :\n"
           '{"courte":"2 phrases max, 160 car.","longue":"<p>3-5 phrases HTML, 80-120 mots</p>"}')


def generate_description(p, port=1234, log=None):
    if not REQUESTS_OK: return None, None
    prompt = _USR_AI.format(
        nom=p.get('name',''), couleur=p.get('color',''),
        comp=p.get('composition','Non disponible'),
        desc=p.get('description','')[:500])
    payload = {"messages":[{"role":"system","content":_SYS_AI},
                            {"role":"user","content":prompt}],
               "temperature":0.7, "max_tokens":512, "stream":False}
    try:
        r = _requests.post(f"http://localhost:{port}/v1/chat/completions",
                           json=payload, timeout=120)
        r.raise_for_status()
        txt = r.json()["choices"][0]["message"]["content"].strip()
        d, f = txt.find("{"), txt.rfind("}")
        if d == -1 or f == -1: return None, None
        data = json.loads(txt[d:f+1])
        return data.get("courte",""), data.get("longue","")
    except Exception as e:
        if log: log.error(f"  IA {p.get('name','?')} : {e}")
        return None, None


# ═══════════════════════════════════════════════════════════════════════════════
#  PIPELINE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def run_pipeline(source_path, output_mode='csv', cat_filter=None, top_n=10,
                 coef=2.2, tax_id=1, prefix='PDF', out_path=None,
                 ps_url='', ps_key='', db_cfg=None,
                 stock_csv_path=None, ps_img_dir=None,
                 allowed_ids=None,
                 ai=False, ai_port=1234, ai_delay=0.5,
                 log=None, state=None):

    if state: state.update(running=True, done=False, error=None,
                            started_at=datetime.now().isoformat())
    if log:
        log.info("=" * 55)
        log.info("PLAISIRS DE FEMMES — Sync Catalogue")
        log.info(f"Source   : {source_path}")
        log.info(f"Mode     : {output_mode.upper()}")
        log.info(f"Filtres  : {', '.join(cat_filter) if cat_filter else 'toutes catégories'}")
        log.info(f"Top/cat  : {top_n or 'illimité'}  |  Coef : ×{coef}")
        log.info("=" * 55)

    try:
        # 1 — Lecture source
        if state: state.update(phase="Lecture source en cours…")
        ext = os.path.splitext(source_path)[1].lower()
        if ext == '.xml':
            products = list(parse_xml(source_path, cat_filter, log))
        else:
            products = list(parse_csv(source_path, cat_filter, log))

        # Filtrage par IDs explicites (import individuel depuis dashboard)
        if allowed_ids:
            allowed_set = set(str(i) for i in allowed_ids)
            products = [p for p in products if str(p.get('id', '')) in allowed_set]
            if log: log.info(f"Filtré par IDs : {len(products)} produits")

        if not products:
            if log: log.warn("Aucun produit après filtrage — arrêt")
            if state: state.update(running=False, done=True, finished_at=datetime.now().isoformat())
            return 0

        if state: state.update(total=len(products))
        if log: log.info(f"Produits lus : {len(products)}")

        # 2 — Descriptions IA (optionnel)
        if ai:
            if state: state.update(phase="Génération descriptions IA…")
            if log: log.info(f"IA activée — LM Studio port {ai_port}")
            for i, p in enumerate(products):
                if not p.get('description'):
                    courte, longue = generate_description(p, ai_port, log)
                    if courte: products[i]['description'] = courte
                    if longue: products[i]['description_longue'] = longue
                    if log and (i+1) % 10 == 0: log.info(f"  IA {i+1}/{len(products)}")
                if state:
                    state.update(processed=i+1,
                                 progress=(i+1)/max(len(products),1)*0.4,
                                 phase=f"IA descriptions ({i+1}/{len(products)})")
                time.sleep(ai_delay)

        # 3 — Sélection Top N (ignoré si IDs explicites)
        effective_top = 0 if allowed_ids else top_n
        if state: state.update(phase="Sélection Top N par catégorie…")
        if log: log.info(f"Sélection Top {effective_top or '∞'} par catégorie…")
        selected = select_top(products, top_n=effective_top, log=log)
        if log: log.ok(f"Sélectionnés : {len(selected)} produits")
        if state: state.update(total=len(selected), phase="Export…")

        # 4 — Export
        result = 0
        if output_mode == 'csv':
            if not out_path:
                base = os.path.splitext(source_path)[0]
                ts   = datetime.now().strftime('%Y%m%d_%H%M')
                out_path = f"{base}_import_{ts}.csv"
            result = export_csv(selected, out_path, coef, tax_id, prefix, log, state)
            if state: state.update(output_file=out_path)

        elif output_mode == 'api':
            result = export_api(selected, ps_url, ps_key, 1, coef, tax_id, prefix, log, state)

        elif output_mode == 'db':
            stock_dict = {}
            if stock_csv_path:
                stock_dict = parse_stock_csv(stock_csv_path, log=log)
            # Regrouper en familles couleur (other_colors → 1 produit PS par famille)
            all_by_id = {p['id']: p for p in products}
            if state: state.update(phase="Regroupement familles couleur…")
            families  = build_color_families(selected, all_by_id)
            n_multi   = sum(1 for f in families if f['multi_color'])
            if log: log.info(f"Familles couleur : {len(families)} ({n_multi} multi-couleurs)")
            result = export_db(families, db_cfg, coef, tax_id, prefix, log, state,
                               stock_dict=stock_dict, ps_img_dir=ps_img_dir)

        if log:
            log.ok("=" * 55)
            log.ok(f"TERMINÉ : {result} produits exportés")
            log.ok("=" * 55)
        if state:
            state.update(running=False, done=True, exported=result,
                         progress=1.0, phase="Terminé ✓",
                         finished_at=datetime.now().isoformat())
        return result

    except Exception as e:
        import traceback
        msg = traceback.format_exc()
        if log: log.error(f"ERREUR PIPELINE : {e}\n{msg}")
        if state: state.update(running=False, done=True, error=str(e),
                                finished_at=datetime.now().isoformat())
        return -1


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD HTML  (template intégré)
# ═══════════════════════════════════════════════════════════════════════════════

_HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PdF — Sync Catalogue</title>
<style>
:root{--rose:#c4748a;--rose-d:#a05570;--rose-l:#f5e8ec;--noir:#1a1a1a;
      --gris:#666;--fond:#f8f6f7;--blanc:#fff;--vert:#2d8a4e;
      --rouge:#c0392b;--bleu:#2471a3;--brd:#e0d0d5;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Segoe UI',sans-serif;background:var(--fond);color:var(--noir);font-size:14px;}
header{background:var(--noir);color:var(--blanc);padding:14px 28px;display:flex;
       align-items:center;gap:14px;border-bottom:3px solid var(--rose);}
header h1{font-size:1.05rem;font-weight:700;letter-spacing:.04em;}
header small{color:var(--rose);font-size:.78rem;}
.wrap{max-width:1140px;margin:0 auto;padding:20px 14px;
      display:grid;grid-template-columns:360px 1fr;gap:20px;}
.card{background:var(--blanc);border-radius:8px;border:1px solid var(--brd);padding:18px;}
.card h2{font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;
         color:var(--rose-d);margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid var(--rose-l);}
label{display:block;font-size:.76rem;font-weight:700;color:var(--gris);margin:10px 0 3px;}
input[type=text],input[type=number],input[type=password],select{
  width:100%;padding:7px 9px;border:1px solid var(--brd);border-radius:5px;
  font-size:.83rem;background:var(--fond);transition:border .15s;}
input:focus,select:focus{outline:none;border-color:var(--rose);}
.tabs{display:flex;gap:0;border-bottom:1px solid var(--brd);margin-bottom:14px;}
.tab{padding:7px 14px;background:none;border:none;cursor:pointer;
     font-size:.78rem;font-weight:700;color:var(--gris);
     border-bottom:2px solid transparent;transition:all .15s;}
.tab.on{color:var(--rose-d);border-bottom-color:var(--rose);}
.tp{display:none;}.tp.on{display:block;}
.rbg{display:flex;gap:6px;flex-wrap:wrap;margin-top:4px;}
.rb input{display:none;}
.rb label{display:block;cursor:pointer;padding:5px 12px;border:1px solid var(--brd);
          border-radius:18px;font-size:.76rem;font-weight:700;color:var(--gris);transition:all .15s;}
.rb input:checked+label{background:var(--rose);border-color:var(--rose);color:#fff;}
.cg{margin-bottom:10px;}
.cgt{font-size:.7rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em;
     color:var(--rose-d);margin-bottom:3px;display:flex;align-items:center;gap:6px;}
.btn-xs{font-size:.65rem;background:none;border:1px solid var(--rose);color:var(--rose);
        padding:1px 7px;border-radius:10px;cursor:pointer;font-weight:700;}
.btn-xs:hover{background:var(--rose);color:#fff;}
.cgrid{display:grid;grid-template-columns:1fr 1fr;gap:2px;}
.ci{display:flex;align-items:center;gap:5px;padding:3px 5px;border-radius:3px;cursor:pointer;}
.ci:hover{background:var(--rose-l);}
.ci input{accent-color:var(--rose);}
.ci label{font-size:.74rem;cursor:pointer;color:var(--noir);margin:0;font-weight:normal;}
.btn-run{display:block;width:100%;padding:11px;background:var(--rose);color:#fff;border:none;
         border-radius:6px;font-size:.9rem;font-weight:800;cursor:pointer;margin-top:18px;
         letter-spacing:.04em;transition:background .15s;}
.btn-run:hover{background:var(--rose-d);}
.btn-run:disabled{background:#ccc;cursor:not-allowed;}
.rcol{display:flex;flex-direction:column;gap:16px;}
.sb{padding:14px 18px;}
.ph{font-size:.8rem;color:var(--gris);margin-bottom:7px;}
.ph b{color:var(--noir);}
.pt{height:7px;background:var(--rose-l);border-radius:4px;overflow:hidden;}
.pf{height:100%;background:linear-gradient(90deg,var(--rose),#e8a0b0);
    border-radius:4px;transition:width .4s ease;width:0;}
.stats{display:flex;gap:14px;margin-top:10px;}
.stat .n{font-size:1.3rem;font-weight:800;color:var(--rose-d);}
.stat .l{font-size:.66rem;text-transform:uppercase;color:var(--gris);letter-spacing:.05em;}
.badge{display:inline-block;padding:2px 9px;border-radius:18px;
       font-size:.68rem;font-weight:800;letter-spacing:.05em;margin-left:10px;}
.bg-idle{background:#999;color:#fff;}
.bg-run{background:var(--bleu);color:#fff;}
.bg-ok{background:var(--vert);color:#fff;}
.bg-err{background:var(--rouge);color:#fff;}
.logp{flex:1;}
.logbox{background:#12121e;border-radius:6px;padding:12px;height:360px;
        overflow-y:auto;font-family:Consolas,monospace;font-size:.74rem;line-height:1.65;}
.le{margin-bottom:1px;}.ts{color:#555;margin-right:5px;}
.INFO .lm{color:#9ab;}.WARN .lm{color:#ec9;}.ERROR .lm{color:#f88;}.OK .lm{color:#7d7;}
.cron-box{background:#12121e;border-radius:5px;padding:10px 12px;
          font-family:monospace;font-size:.76rem;color:#9f9;word-break:break-all;margin-top:6px;}
.out-cfg{display:none;}
.btn-scan{background:var(--rose);color:#fff;border:none;border-radius:5px;
          padding:7px 14px;font-size:.78rem;font-weight:700;cursor:pointer;}
.btn-scan:hover{background:var(--rose-d);}
.cath{background:var(--rose-l);padding:6px 10px;cursor:pointer;
      display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--brd);}
.catb{display:none;max-height:260px;overflow-y:auto;}
.prod-row{display:flex;align-items:center;gap:6px;padding:4px 10px;
          border-bottom:1px solid #f5eef0;font-size:.73rem;}
.prod-row:hover{background:var(--rose-l);}
.prod-score{font-size:.67rem;color:var(--gris);white-space:nowrap;margin-left:auto;}
.sel-bar{background:var(--rose-l);border-radius:6px;padding:8px 12px;
         margin-top:10px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
@media(max-width:760px){.wrap{grid-template-columns:1fr;}}
</style>
</head>
<body>
<header>
  <svg width="26" height="26" viewBox="0 0 24 24"><path d="M12 21.593c-5.63-5.539-11-10.297-11-14.402C1 3.199 3.819 1 6.281 1c1.875 0 3.65 1.024 4.719 2.536C12.07 2.024 13.845 1 15.719 1 18.181 1 21 3.199 21 7.191c0 4.105-5.371 8.863-11 14.402z" fill="#c4748a"/></svg>
  <div><h1>Plaisirs de Femmes — Sync Catalogue</h1><small>Matterhorn → PrestaShop 8</small></div>
</header>

<div class="wrap">
<!-- ── GAUCHE ─────────────────────────────────────────────── -->
<div>
<div class="card">
<h2>Configuration</h2>
<div class="tabs">
  <button class="tab on" onclick="tab(this,'source')">Source</button>
  <button class="tab" onclick="tab(this,'cats')">Catégories</button>
  <button class="tab" onclick="tab(this,'sortie')">Sortie</button>
  <button class="tab" onclick="tab(this,'cron')">Cron</button>
  <button class="tab" onclick="tab(this,'cat')">Catalogue</button>
</div>

<!-- SOURCE -->
<div id="tp-source" class="tp on">
  <label>Fichier source (.xml ou .csv)</label>
  <input id="source" type="text" placeholder="/chemin/vers/catalogue.xml">
  <label>Coefficient prix (wholesale × coef = HT boutique)</label>
  <input id="coef" type="number" value="2.2" step="0.1" min="1">
  <label>Tax Rules ID PrestaShop</label>
  <input id="tax_id" type="number" value="1" min="1">
  <label>Préfixe référence</label>
  <input id="ref_prefix" type="text" value="PDF">
  <label>Top N produits / catégorie (0 = tous)</label>
  <input id="top_n" type="number" value="10" min="0">
  <div style="margin-top:10px">
    <label style="display:flex;align-items:center;gap:7px;font-weight:normal">
      <input type="checkbox" id="ai_on"> Générer descriptions IA (LM Studio local)
    </label>
    <div id="ai_row" style="display:none;margin-top:5px">
      <label>Port LM Studio</label>
      <input id="ai_port" type="number" value="1234">
    </div>
  </div>
</div>

<!-- CATÉGORIES -->
<div id="tp-cats" class="tp">
  <p style="font-size:.74rem;color:var(--gris);margin-bottom:10px">
    Aucune cochée = toutes les catégories.</p>
  <div id="cats-wrap">Chargement…</div>
  <div style="display:flex;gap:6px;margin-top:8px">
    <button class="btn-xs" onclick="allCats(1)" style="font-size:.74rem;padding:3px 10px">Tout cocher</button>
    <button class="btn-xs" onclick="allCats(0)" style="font-size:.74rem;padding:3px 10px">Tout décocher</button>
  </div>
</div>

<!-- CATALOGUE -->
<div id="tp-cat" class="tp">
  <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap">
    <button class="btn-scan" onclick="scanCatalog()">🔍 Scanner le catalogue</button>
    <span id="scan-info" style="font-size:.72rem;color:var(--gris)">Renseignez le fichier source puis cliquez.</span>
  </div>
  <div id="catalog-wrap"></div>
  <div class="sel-bar" id="sel-bar" style="display:none">
    <span id="sel-count" style="font-size:.8rem;font-weight:700;color:var(--rose-d)"></span>
    <button class="btn-run" style="margin:0;padding:6px 16px;font-size:.78rem;width:auto"
            onclick="importSelected()">⬆ Importer la sélection</button>
    <button class="btn-xs" onclick="clearSel()">Tout décocher</button>
    <button class="btn-xs" onclick="top10All()">Top 10 partout</button>
  </div>
</div>

<!-- SORTIE -->
<div id="tp-sortie" class="tp">
  <label>Format de sortie</label>
  <div class="rbg">
    <div class="rb"><input type="radio" name="out" id="o-csv" value="csv" checked><label for="o-csv">CSV Simple Import</label></div>
    <div class="rb"><input type="radio" name="out" id="o-api" value="api"><label for="o-api">API PrestaShop</label></div>
    <div class="rb"><input type="radio" name="out" id="o-db"  value="db" ><label for="o-db">BDD Directe</label></div>
  </div>
  <div id="cfg-csv" class="out-cfg" style="display:block">
    <label>Fichier de sortie (vide = auto)</label>
    <input id="csv_path" type="text" placeholder="output/import.csv">
  </div>
  <div id="cfg-api" class="out-cfg">
    <label>URL boutique</label><input id="ps_url" type="text" placeholder="https://plaisirs-de-femmes.fr">
    <label>Clé API WebService</label><input id="ps_key" type="password" placeholder="Votre clé">
  </div>
  <div id="cfg-db" class="out-cfg">
    <label>Hôte MySQL</label><input id="db_host" type="text" value="localhost">
    <label>Base de données</label><input id="db_name" type="text" placeholder="prestashop_db">
    <label>Utilisateur</label><input id="db_user" type="text" placeholder="ps_user">
    <label>Mot de passe</label><input id="db_pass" type="password">
    <label>Stock CSV Matterhorn (déclinaisons) — facultatif</label>
    <input id="stock_csv" type="text" placeholder="/chemin/vers/prestashop_stock.csv">
    <small style="color:var(--gris);font-size:.71rem">Fichier prestashop_stock.csv fourni par Matterhorn — remplace la colonne sizes_sku_codes pour des tailles propres.</small>
    <label>Dossier images PS (img/p)</label>
    <input id="ps_img_dir" type="text" placeholder="/home/.../htdocs/www.../img/p">
  </div>
</div>

<!-- CRON -->
<div id="tp-cron" class="tp">
  <p style="font-size:.75rem;color:var(--gris);margin-bottom:10px">
    Copiez cette ligne dans votre crontab pour automatiser.</p>
  <label>Fréquence</label>
  <select id="cfreq" onchange="upCron()">
    <option value="0 2 * * *">Chaque nuit à 2h00</option>
    <option value="0 6 * * 1">Chaque lundi à 6h00</option>
    <option value="0 8 1 * *">1er du mois à 8h00</option>
    <option value="0 */6 * * *">Toutes les 6 heures</option>
    <option value="custom">Personnalisé…</option>
  </select>
  <input id="cfreq_c" type="text" placeholder="0 2 * * *" style="display:none;margin-top:5px">
  <label>Commande cron</label>
  <div class="cron-box" id="cron_cmd">—</div>
  <div style="display:flex;gap:6px;margin-top:7px">
    <button class="btn-xs" onclick="upCron()" style="padding:4px 10px;font-size:.74rem">Actualiser</button>
    <button class="btn-xs" onclick="copyCron()" style="padding:4px 10px;font-size:.74rem">Copier</button>
  </div>
</div>

<button class="btn-run" id="btn-run" onclick="go()">▶ Lancer la synchronisation</button>
</div>
</div>

<!-- ── DROITE ─────────────────────────────────────────────── -->
<div class="rcol">
  <div class="card sb">
    <div style="display:flex;align-items:center;margin-bottom:9px">
      <span style="font-weight:800;font-size:.88rem">Statut</span>
      <span class="badge bg-idle" id="sbadge">INACTIF</span>
    </div>
    <div class="ph"><b id="phase">En attente…</b></div>
    <div class="pt"><div class="pf" id="pbar"></div></div>
    <div style="text-align:right;font-size:.7rem;color:var(--gris);margin-top:3px" id="ppct">0 %</div>
    <div class="stats">
      <div class="stat"><div class="n" id="st-tot">—</div><div class="l">Total</div></div>
      <div class="stat"><div class="n" id="st-proc">—</div><div class="l">Traités</div></div>
      <div class="stat"><div class="n" id="st-exp">—</div><div class="l">Exportés</div></div>
    </div>
    <div id="dl-wrap" style="display:none;margin-top:10px">
      <a id="dl-link" href="#" style="font-size:.76rem;color:var(--rose-d)">⬇ Télécharger le CSV</a>
    </div>
  </div>

  <div class="card logp">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
      <h2 style="margin:0;border:0;padding:0">Logs temps réel</h2>
      <button onclick="clearLog()" style="background:none;border:1px solid var(--brd);border-radius:4px;
              padding:2px 8px;font-size:.7rem;cursor:pointer;color:var(--gris)">Effacer</button>
    </div>
    <div class="logbox" id="logbox"></div>
  </div>
</div>
</div><!-- /wrap -->

<script>
// ── Tabs ─────────────────────────────────────────────────────────────────────
function tab(btn, id) {
  document.querySelectorAll('.tab').forEach(b=>b.classList.remove('on'));
  document.querySelectorAll('.tp').forEach(t=>t.classList.remove('on'));
  btn.classList.add('on');
  document.getElementById('tp-'+id).classList.add('on');
}
// ── AI toggle ─────────────────────────────────────────────────────────────────
document.getElementById('ai_on').addEventListener('change',function(){
  document.getElementById('ai_row').style.display=this.checked?'block':'none';
});
// ── Output mode toggle ────────────────────────────────────────────────────────
document.querySelectorAll('input[name=out]').forEach(r=>{
  r.addEventListener('change',()=>{
    document.querySelectorAll('.out-cfg').forEach(d=>d.style.display='none');
    document.getElementById('cfg-'+r.value).style.display=r.checked?'block':'none';
  });
});
// ── Catégories ────────────────────────────────────────────────────────────────
let catData={};
fetch('/categories').then(r=>r.json()).then(d=>{
  catData=d;
  const wrap=document.getElementById('cats-wrap');
  wrap.innerHTML='';
  for(const[uni,cats]of Object.entries(d)){
    const grp=document.createElement('div'); grp.className='cg';
    grp.innerHTML=`<div class="cgt">${uni}
      <button class="btn-xs" onclick="grpCats('${uni}',1)">Tout</button>
      <button class="btn-xs" onclick="grpCats('${uni}',0)">Aucun</button>
    </div><div class="cgrid">${cats.map(c=>`
      <div class="ci">
        <input type="checkbox" id="c_${CSS.escape(c)}" name="cats" value="${c}">
        <label for="c_${CSS.escape(c)}">${c.split('/').pop()||c}</label>
      </div>`).join('')}</div>`;
    wrap.appendChild(grp);
  }
});
function grpCats(uni,v){
  document.querySelectorAll('input[name=cats]').forEach(cb=>{
    if(catData[uni]?.includes(cb.value)) cb.checked=!!v;
  });
}
function allCats(v){
  document.querySelectorAll('input[name=cats]').forEach(cb=>cb.checked=!!v);
}
// ── Pipeline ──────────────────────────────────────────────────────────────────
let sse=null, poll=null;
function go(){
  const src=document.getElementById('source').value.trim();
  if(!src){alert('Spécifiez un fichier source !');return;}
  const cats=[...document.querySelectorAll('input[name=cats]:checked')].map(c=>c.value);
  const mode=document.querySelector('input[name=out]:checked').value;
  clearLog();
  document.getElementById('btn-run').disabled=true;
  setBadge('ACTIF','bg-run');
  fetch('/run',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      source:src, output:mode, categories:cats,
      top_n:+document.getElementById('top_n').value||10,
      coef:+document.getElementById('coef').value||2.2,
      tax_id:+document.getElementById('tax_id').value||1,
      ref_prefix:document.getElementById('ref_prefix').value||'PDF',
      ai_enabled:document.getElementById('ai_on').checked,
      ai_port:+document.getElementById('ai_port').value||1234,
      csv_path:document.getElementById('csv_path').value,
      ps_url:document.getElementById('ps_url').value,
      ps_key:document.getElementById('ps_key').value,
      db_host:document.getElementById('db_host').value,
      db_name:document.getElementById('db_name').value,
      db_user:document.getElementById('db_user').value,
      db_pass:document.getElementById('db_pass').value,
      stock_csv:document.getElementById('stock_csv').value,
      ps_img_dir:document.getElementById('ps_img_dir').value,
    })
  }).then(r=>r.json()).then(res=>{
    if(res.error){addLog('ERROR',res.error,'');setBadge('ERREUR','bg-err');
                  document.getElementById('btn-run').disabled=false;return;}
    startSSE(); startPoll();
  });
}
function startSSE(){
  if(sse) sse.close();
  sse=new EventSource('/stream');
  sse.onmessage=e=>{
    const d=JSON.parse(e.data);
    if(d.done){sse.close();return;}
    if(d.level) addLog(d.level,d.msg,d.ts);
  };
  sse.onerror=()=>sse.close();
}
function startPoll(){
  if(poll) clearInterval(poll);
  poll=setInterval(()=>{
    fetch('/status').then(r=>r.json()).then(s=>{
      document.getElementById('pbar').style.width=s.progress+'%';
      document.getElementById('ppct').textContent=s.progress+' %';
      document.getElementById('phase').textContent=s.phase||'…';
      document.getElementById('st-tot').textContent=s.total||'—';
      document.getElementById('st-proc').textContent=s.processed||'—';
      document.getElementById('st-exp').textContent=s.exported||'—';
      if(s.output_file){
        document.getElementById('dl-wrap').style.display='block';
        document.getElementById('dl-link').href='/download?file='+encodeURIComponent(s.output_file);
        document.getElementById('dl-link').textContent='⬇ '+s.output_file.split(/[\/\\]/).pop();
      }
      if(!s.running&&s.done){
        clearInterval(poll);
        document.getElementById('btn-run').disabled=false;
        setBadge(s.error?'ERREUR':'TERMINÉ',s.error?'bg-err':'bg-ok');
      }
    });
  },600);
}
function setBadge(t,c){const b=document.getElementById('sbadge');b.textContent=t;b.className='badge '+c;}
// ── Logs ─────────────────────────────────────────────────────────────────────
function addLog(lv,msg,ts){
  const b=document.getElementById('logbox');
  const d=document.createElement('div'); d.className='le '+lv;
  d.innerHTML=`<span class="ts">${ts}</span><span class="lm">${esc(msg)}</span>`;
  b.appendChild(d); b.scrollTop=b.scrollHeight;
}
function clearLog(){
  document.getElementById('logbox').innerHTML='';
  document.getElementById('pbar').style.width='0%';
  document.getElementById('ppct').textContent='0 %';
  document.getElementById('phase').textContent='En attente…';
  ['st-tot','st-proc','st-exp'].forEach(i=>document.getElementById(i).textContent='—');
  document.getElementById('dl-wrap').style.display='none';
  setBadge('INACTIF','bg-idle');
}
function esc(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
// ── Cron ─────────────────────────────────────────────────────────────────────
document.getElementById('cfreq').addEventListener('change',function(){
  document.getElementById('cfreq_c').style.display=this.value==='custom'?'block':'none';
  upCron();
});
function upCron(){
  const src=document.getElementById('source').value||'/chemin/vers/catalogue.xml';
  const mode=document.querySelector('input[name=out]:checked').value;
  const cats=[...document.querySelectorAll('input[name=cats]:checked')].map(c=>c.value);
  const top=document.getElementById('top_n').value||10;
  const coef=document.getElementById('coef').value||2.2;
  let fr=document.getElementById('cfreq').value;
  if(fr==='custom') fr=document.getElementById('cfreq_c').value||'0 2 * * *';
  let cmd=`python plaisirs_sync.py --source "${src}" --output ${mode} --top ${top} --coef ${coef} --cron`;
  if(cats.length) cmd+=` --categories "${cats.join(',')}"`;
  document.getElementById('cron_cmd').textContent=`${fr}  ${cmd} >> logs/sync.log 2>&1`;
}
function copyCron(){
  navigator.clipboard.writeText(document.getElementById('cron_cmd').textContent)
    .then(()=>alert('Commande copiée dans le presse-papiers !'));
}
upCron();

// ── Catalogue ─────────────────────────────────────────────────────────────────
let catProds={};
function esc2(t){return t.replace(/'/g,"\'").replace(/"/g,'&quot;');}

function scanCatalog(){
  const src=document.getElementById('source').value.trim();
  if(!src){alert("Renseignez le fichier source d'abord !");return;}
  document.getElementById('scan-info').textContent='Analyse en cours… (peut prendre 1 à 2 min)';
  document.getElementById('catalog-wrap').innerHTML='<div style="padding:20px;text-align:center;color:var(--gris)">⏳ Lecture du catalogue…</div>';
  fetch('/catalog',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({source:src})
  }).then(r=>r.json()).then(data=>{
    if(data.error){document.getElementById('scan-info').textContent='Erreur : '+data.error;return;}
    catProds=data;
    let total=0; Object.values(data).forEach(ps=>total+=ps.length);
    document.getElementById('scan-info').textContent=Object.keys(data).length+' catégories — '+total+' produits';
    renderCatalog(data);
  }).catch(e=>{document.getElementById('scan-info').textContent='Erreur réseau : '+e;});
}

function renderCatalog(data){
  const wrap=document.getElementById('catalog-wrap');
  wrap.innerHTML='';
  for(const[cat,prods] of Object.entries(data)){
    const div=document.createElement('div');
    div.style='border:1px solid var(--brd);border-radius:6px;margin-bottom:6px;overflow:hidden';
    div.innerHTML=`<div class="cath" onclick="toggleCat(this)">
      <input type="checkbox" onclick="catChk(event,'${esc2(cat)}')" style="accent-color:var(--rose)">
      <span style="font-weight:700;font-size:.78rem;flex:1">${esc(cat)}</span>
      <span style="font-size:.7rem;color:var(--gris)">${prods.length} produits</span>
      <button class="btn-xs" onclick="selTop(event,'${esc2(cat)}',10)" style="margin-left:4px">Top 10</button>
      <button class="btn-xs" onclick="selTop(event,'${esc2(cat)}',0)" style="margin-left:2px">Tout</button>
      <span style="font-size:.8rem;margin-left:4px">▾</span>
    </div>
    <div class="catb">${prods.map((p,i)=>`
      <div class="prod-row">
        <input type="checkbox" id="p_${p.id}" name="prod" value="${p.id}"
               onchange="updSel()" ${i<10?'checked':''}>
        <label for="p_${p.id}" style="flex:1;cursor:pointer">${esc(p.name)}</label>
        <span class="prod-score">★${p.score} | ${p.sizes}T | ${p.images}🖼</span>
      </div>`).join('')}</div>`;
    wrap.appendChild(div);
  }
  updSel();
}

function toggleCat(el){
  const b=el.nextElementSibling;
  const open=b.style.display!=='block';
  b.style.display=open?'block':'none';
  el.querySelector('span:last-child').textContent=open?'▴':'▾';
}
function catChk(ev,cat){
  ev.stopPropagation();
  const v=ev.target.checked;
  (catProds[cat]||[]).forEach(p=>{const e=document.getElementById('p_'+p.id);if(e)e.checked=v;});
  updSel();
}
function selTop(ev,cat,n){
  ev.stopPropagation();
  (catProds[cat]||[]).forEach((p,i)=>{const e=document.getElementById('p_'+p.id);if(e)e.checked=n===0||i<n;});
  updSel();
}
function top10All(){
  Object.entries(catProds).forEach(([cat,prods])=>selTop({stopPropagation:()=>{}},cat,10));
}
function clearSel(){document.querySelectorAll('input[name=prod]').forEach(cb=>cb.checked=false);updSel();}
function updSel(){
  const n=document.querySelectorAll('input[name=prod]:checked').length;
  const bar=document.getElementById('sel-bar');
  bar.style.display=n?'flex':'none';
  document.getElementById('sel-count').textContent=n+' produit(s) sélectionné(s)';
}

function importSelected(){
  const ids=[...document.querySelectorAll('input[name=prod]:checked')].map(cb=>cb.value);
  if(!ids.length)return;
  const src=document.getElementById('source').value.trim();
  const mode=document.querySelector('input[name=out]:checked').value;
  clearLog();
  document.getElementById('btn-run').disabled=true;
  setBadge('ACTIF','bg-run');
  fetch('/run',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      source:src, output:mode, product_ids:ids, top_n:0,
      coef:+document.getElementById('coef').value||2.2,
      tax_id:+document.getElementById('tax_id').value||1,
      ref_prefix:document.getElementById('ref_prefix').value||'PDF',
      ai_enabled:document.getElementById('ai_on').checked,
      ai_port:+document.getElementById('ai_port').value||1234,
      csv_path:document.getElementById('csv_path').value,
      ps_url:document.getElementById('ps_url').value,
      ps_key:document.getElementById('ps_key').value,
      db_host:document.getElementById('db_host').value,
      db_name:document.getElementById('db_name').value,
      db_user:document.getElementById('db_user').value,
      db_pass:document.getElementById('db_pass').value,
      stock_csv:document.getElementById('stock_csv').value,
      ps_img_dir:document.getElementById('ps_img_dir').value,
    })
  }).then(r=>r.json()).then(res=>{
    if(res.error){addLog('ERROR',res.error,'');setBadge('ERREUR','bg-err');
                  document.getElementById('btn-run').disabled=false;return;}
    startSSE();startPoll();
  });
}
</script>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════════════════
#  SERVEUR FLASK
# ═══════════════════════════════════════════════════════════════════════════════

def create_app(cfg, state):
    if not FLASK_OK:
        raise RuntimeError("Flask non installé — pip install flask")
    app = Flask(__name__)
    _log_ref = [None]

    @app.route('/')
    def index(): return _HTML

    @app.route('/categories')
    def categories(): return jsonify(UNIVERS)

    @app.route('/catalog', methods=['POST'])
    def catalog():
        data = request.get_json() or {}
        src = data.get('source', '')
        if not src or not os.path.exists(str(src)):
            return jsonify({'error': f'Fichier introuvable : {src}'}), 400
        try:
            products = list(parse_csv(src, log=None))
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        # Scorer et grouper par catégorie PS
        result = {}
        for p in products:
            score = score_product(p)
            cat_raw = map_category(p.get('category_path', ''))
            leaf = cat_raw.split('->')[-1].strip() if '->' in (cat_raw or '') else (cat_raw or '').strip()
            if not leaf:
                leaf = p.get('category_path', '') or 'Sans catégorie'
            result.setdefault(leaf, [])
            result[leaf].append({
                'id':     p['id'],
                'name':   p['name'],
                'score':  score,
                'images': len(p.get('images', [])),
                'sizes':  len(p.get('options', [])),
                'price':  p.get('price_raw', ''),
            })
        # Trier : score desc dans chaque catégorie ; catégories par nb de produits desc
        for cat in result:
            result[cat].sort(key=lambda x: -x['score'])
        result = dict(sorted(result.items(), key=lambda x: -len(x[1])))
        return jsonify(result)

    @app.route('/run', methods=['POST'])
    def run():
        if state.running:
            return jsonify({'error': 'Une tâche est déjà en cours'}), 409
        data = request.get_json() or {}
        state.update(running=False, done=False, error=None, progress=0.0,
                     total=0, processed=0, exported=0, phase='', output_file='')
        log = TaskLogger(cfg.get('paths', {}).get('log_dir', './logs'))
        _log_ref[0] = log

        db_cfg = None
        if data.get('output') == 'db':
            dbc = cfg.get('database', {})
            db_cfg = {'host': data.get('db_host') or dbc.get('host', 'localhost'),
                      'port': 3306,
                      'database': data.get('db_name') or dbc.get('name', ''),
                      'user': data.get('db_user') or dbc.get('user', ''),
                      'password': data.get('db_pass') or dbc.get('password', '')}

        def _bg():
            run_pipeline(
                source_path=data['source'],
                output_mode=data.get('output', 'csv'),
                cat_filter=data.get('categories') or None,
                top_n=data.get('top_n', 10),
                coef=data.get('coef', 2.2),
                tax_id=data.get('tax_id', 1),
                prefix=data.get('ref_prefix', 'PDF'),
                out_path=data.get('csv_path') or None,
                ps_url=data.get('ps_url') or cfg.get('prestashop', {}).get('url', ''),
                ps_key=data.get('ps_key') or cfg.get('prestashop', {}).get('api_key', ''),
                db_cfg=db_cfg,
                stock_csv_path=data.get('stock_csv') or None,
                ps_img_dir=data.get('ps_img_dir') or cfg.get('prestashop', {}).get('img_dir', '') or None,
                allowed_ids=data.get('product_ids') or None,
                ai=data.get('ai_enabled', False),
                ai_port=data.get('ai_port', 1234),
                log=log, state=state,
            )
        threading.Thread(target=_bg, daemon=True).start()
        return jsonify({'ok': True})

    @app.route('/stream')
    def stream():
        log = _log_ref[0]
        def gen():
            if not log:
                return
            while True:
                try:
                    entry = log.q.get(timeout=25)
                    yield f"data: {json.dumps(entry, ensure_ascii=False)}\n\n"
                    if state.done and log.q.empty():
                        yield f"data: {json.dumps({'done': True})}\n\n"
                        break
                except queue.Empty:
                    if state.done:
                        yield f"data: {json.dumps({'done': True})}\n\n"
                        break
                    yield f"data: {json.dumps({'level': 'INFO', 'msg': '', 'ts': ''})}\n\n"
        return Response(stream_with_context(gen()), mimetype='text/event-stream',
                        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

    @app.route('/status')
    def status(): return jsonify(state.snap())

    @app.route('/download')
    def download():
        fp = request.args.get('file', '')
        if fp and os.path.exists(fp):
            return send_file(fp, as_attachment=True)
        return 'Fichier introuvable', 404

    return app


# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

def load_config(path='config.json'):
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            user = json.load(f)
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    else:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        print(f"[INFO] config.json créé — renseignez vos identifiants PS / DB avant d'utiliser ces modes.")
    return cfg


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI + POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def _parser():
    p = argparse.ArgumentParser(prog='plaisirs_sync.py',
                                description='Plaisirs de Femmes — Sync Catalogue',
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog=__doc__)
    p.add_argument('--server',     action='store_true', help='Lance le dashboard web')
    p.add_argument('--port',       type=int,   default=8765)
    p.add_argument('--source',     type=str,   default='',
                                   help='Fichier XML ou CSV fournisseur Matterhorn (requis hors --server)')
    p.add_argument('--output',     type=str,   default='csv',
                                   choices=['csv', 'api', 'db'],
                                   help='Mode de sortie : csv | api | db  (defaut : csv)')
    p.add_argument('--categories', type=str,   default='',
                                   help='Categories Matterhorn separees par virgule (vide = toutes)')
    p.add_argument('--top',        type=int,   default=10,
                                   help='Top N produits par categorie (0 = illimite, defaut 10)')
    p.add_argument('--coef',       type=float, default=2.2,
                                   help='Coefficient prix wholesale (defaut 2.2)')
    p.add_argument('--taxe',       type=int,   default=1,
                                   help='Tax rules ID PrestaShop (defaut 1 = TVA 20 %%)')
    p.add_argument('--ref-prefix', type=str,   default='PDF',
                                   help='Prefixe reference PS (defaut PDF)')
    p.add_argument('--out',        type=str,   default='',
                                   help='Fichier CSV de sortie (mode csv uniquement)')
    p.add_argument('--stock-csv',  type=str,   default='',
                                   help='CSV de stock Matterhorn (filtre disponibilite)')
    p.add_argument('--ps-url',     type=str,   default='',
                                   help='URL boutique PrestaShop (mode api)')
    p.add_argument('--ps-key',     type=str,   default='',
                                   help='Cle API PrestaShop (mode api)')
    p.add_argument('--db-host',    type=str,   default='',
                                   help='Hote MySQL (mode db)')
    p.add_argument('--db-name',    type=str,   default='',
                                   help='Nom de la base MySQL (mode db)')
    p.add_argument('--db-user',    type=str,   default='',
                                   help='Utilisateur MySQL (mode db)')
    p.add_argument('--db-pass',    type=str,   default='',
                                   help='Mot de passe MySQL (mode db)')
    p.add_argument('--ps-img-dir', type=str,   default='',
                                   help='Dossier racine images PS (ex: /var/www/html/img/p)')
    p.add_argument('--ai',         action='store_true',
                                   help='Active la generation de descriptions via LM Studio')
    p.add_argument('--ai-port',    type=int,   default=1234,
                                   help='Port LM Studio (defaut 1234)')
    p.add_argument('--cron',       action='store_true',
                                   help='Mode silencieux : log fichier uniquement, pas de stdout')
    p.add_argument('--config',     type=str,   default='config.json',
                                   help='Fichier de configuration JSON (defaut config.json)')
    return p


def main():
    args = _parser().parse_args()
    cfg  = load_config(args.config)

    if args.server:
        state = TaskState()
        app   = create_app(cfg, state)
        print(f'[INFO] Dashboard -> http://localhost:{args.port}')
        app.run(host='0.0.0.0', port=args.port, debug=False, threaded=True)
        return

    if not args.source:
        _parser().error('--source est requis hors du mode --server')

    log = TaskLogger(
        log_dir=cfg.get('paths', {}).get('log_dir', './logs'),
        cron=args.cron,
    )

    cat_filter = [c.strip() for c in args.categories.split(',') if c.strip()] or None

    db_cfg = None
    if args.output == 'db':
        dbc    = cfg.get('database', {})
        db_cfg = {
            'host':     args.db_host or dbc.get('host', 'localhost'),
            'port':     dbc.get('port', 3306),
            'database': args.db_name or dbc.get('name', ''),
            'user':     args.db_user or dbc.get('user', ''),
            'password': args.db_pass or dbc.get('password', ''),
        }

    ps_img_dir = args.ps_img_dir or cfg.get('prestashop', {}).get('img_dir', '') or None

    run_pipeline(
        source_path=args.source,
        output_mode=args.output,
        cat_filter=cat_filter,
        top_n=args.top,
        coef=args.coef,
        tax_id=args.taxe,
        prefix=args.ref_prefix,
        out_path=args.out or None,
        ps_url=args.ps_url or cfg.get('prestashop', {}).get('url', ''),
        ps_key=args.ps_key or cfg.get('prestashop', {}).get('api_key', ''),
        db_cfg=db_cfg,
        stock_csv_path=args.stock_csv or None,
        ps_img_dir=ps_img_dir,
        ai=args.ai,
        ai_port=args.ai_port,
        log=log,
    )


if __name__ == '__main__':
    main()
