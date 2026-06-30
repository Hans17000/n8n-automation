#!/usr/bin/env python3
"""
Mini API Flask pour traiter Matterhorn XML → CSV Simple Import
- POST /parse : reçoit XML, retourne CSV
- GET /health : check que l'API marche

Usage:
  pip install flask
  python api_matterhorn.py
  # Puis depuis n8n: POST http://localhost:5000/parse avec {"xml_content": "..."}
"""

from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
from datetime import datetime

app = Flask(__name__)

# ─── CATEGORY MAPPING ───
CATEGORY_MAP = {
    "Soutiens-Gorge Push Up": "Corps & Désirs->Soutiens-Gorge Galbe",
    "Soutiens-Gorge Balconnet": "Corps & Désirs->Soutiens-Gorge Décolleté",
    "Corsets et Bodys Femme": "Corps & Désirs->Bodys de Soie",
    "Culottes": "Corps & Désirs->Dessous Précieux",
    "Strings": "Corps & Désirs->Dentelles Effilées",
    "Collants, Bas": "Fils de Soie->Bas & Collants de Soie",
    "Nuisettes, Chemises de Nuit": "L'Heure Bleue->Nuits de Dentelle",
    "Pyjamas, Ensembles de Nuit": "L'Heure Bleue->Nuits Sereines",
    "Peignoirs, Robes de Chambre et Kimonos": "L'Heure Bleue->Matins de Soie",
    "Culottes, Shortys et Strings Amincissants": "Architecture Intime->Affinements Secrets",
    "Corsets, Body Femme, Ceintures Modelantes et Gainantes": "Architecture Intime->Silhouettes Architecturées",
    "Ensembles Sexy": "L'Impudence->Objets du Désir",
    "Bodys, Caracos, Porte-Jarreteles": "L'Impudence->Objets du Désir",
    "Guêpières, Bustiers, Nuisettes et Babydolls": "L'Impudence->Objets du Désir",
    "Maillots de Bain 1 Pièce": "La Garde-Robe->Balnéaire Une Pièce",
    "Maillots de Bain 2 Pièces": "La Garde-Robe->Balnéaire Deux Pièces",
    "Robes de Plage, Paréos": "La Garde-Robe->Échappées Balnéaires",
    "Robes de Jour": "La Garde-Robe->Robes du Jour",
    "Robes de Soirée": "La Garde-Robe->Robes du Soir",
    "Robes de cocktail": "La Garde-Robe->Robes de Cérémonie",
    "Chemises Femme": "La Garde-Robe->Chemises d'Auteur",
    "Tops Femme, T-shirts": "La Garde-Robe->Tops & Essentiels",
    "Leggings Femme": "La Garde-Robe->Leggings de Caractère",
    "Pantalons femme, Shorts femme": "La Garde-Robe->Pantalons & Shorts",
    "Sweats et sweat-shirts femme": "La Garde-Robe->Sweats & Molletons",
    "Pulls, Chandails, Pullovers": "La Garde-Robe->Tricots & Cols Roulés",
    "Cardigans Femme": "La Garde-Robe->Cardigans & Ponchos",
    "Bottes et boots": "Chaussures->Bottes & Boots",
    "Bottes, Cuissardes": "Chaussures->Cuissardes",
    "Sandales et mules": "Chaussures->Sandales & Mules",
    "Escarpins": "Chaussures->Escarpins",
    "Talons aiguilles": "Chaussures->Talons Aiguilles",
}

def score_product(product):
    """Calcule un score de popularité (heuristique)"""
    score = 1
    images = len([img for img in product.get('images', '').split(',') if img.strip()])
    if images >= 4:
        score += 3
    if len(product.get('description', '')) > 200:
        score += 2
    return score

def map_category(category_path):
    """Mappe catégorie Matterhorn → PrestaShop"""
    path_lower = (category_path or '').lower()
    for matterhorn_cat, ps_cat in CATEGORY_MAP.items():
        if matterhorn_cat.lower() in path_lower:
            return ps_cat
    return "Corps & Désirs->Parures d'Exception"

def parse_xml_and_generate_csv(xml_content, top_n=50):
    """Parse XML Matterhorn → CSV Simple Import (max 500 produits)"""
    try:
        root = ET.fromstring(xml_content)
        products = []

        for item_elem in root.findall('.//item'):
            if len(products) >= 500:
                break
            product = {}
            for field in ['id', 'name', 'color', 'description', 'category_path', 'brand', 'active', 'price', 'images']:
                elem = item_elem.find(field)
                product[field] = elem.text.strip() if elem is not None and elem.text else ''
            if product.get('id') and product.get('active') == '1':
                products.append(product)

        products_scored = [(p, score_product(p)) for p in products]
        products_sorted = sorted(products_scored, key=lambda x: x[1], reverse=True)
        top_products = [p for p, score in products_sorted[:top_n]]

        header = ['Reference', 'Name', 'Active', 'Price', 'Tax', 'Categories', 'Description', 'Color']
        csv_lines = ['﻿' + ';'.join(header)]  # UTF-8 BOM

        for p in top_products:
            ref = f"PDF-{p['id']}"
            price = f"{float(p.get('price', 0)) * 2.2:.2f}"
            category = map_category(p.get('category_path', ''))
            description = p.get('description', '')[:300].replace(';', ',')
            color = p.get('color', 'Standard')
            line = ';'.join([ref, p.get('name', '').replace(';', ','), '1', price, '1', category, description, color])
            csv_lines.append(line)

        return {
            'status': 'success',
            'total_parsed': len(products),
            'top_selected': len(top_products),
            'csv_lines': len(csv_lines) - 1,
            'csv_content': '\n'.join(csv_lines)
        }

    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat(), 'service': 'Matterhorn XML Parser'})

@app.route('/parse', methods=['POST'])
def parse():
    """Parse XML → CSV. Input: {"xml_content": "...", "top_n": 50}"""
    try:
        data = request.get_json()
        xml_content = data.get('xml_content', '')
        top_n = data.get('top_n', 50)
        if not xml_content:
            return jsonify({'status': 'error', 'message': 'xml_content required'}), 400
        result = parse_xml_and_generate_csv(xml_content, top_n)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("🚀 API Matterhorn Parser started on http://localhost:5000")
    print("   POST /parse - Parse XML → CSV")
    print("   GET /health - Health check")
    app.run(host='localhost', port=5000, debug=False)
