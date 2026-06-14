---
date: 2026-06-11
tags: [produits, catalogue, import, export, categories, matterhorn, xml]
type: index
status: active
updated: 2026-06-11
---

# 📦 Index — Imports / Exports

Données brutes du catalogue fournisseur Matterhorn et fichiers d'import PrestaShop.

## Flux XML Matterhorn v2 (juin 2026)

Nouveau format XML fourni par Matterhorn, nettement plus complet que l'ancien `products_ver2__sizesFR.xml`. Chaque `<product>` contient désormais : nom, marque, catégorie avec chemin complet (`category_path`), couleur, type, prix wholesale, description avec composition matières, images (URLs directes), et options/déclinaisons avec taille, stock et EAN.

- `products_sizesFR.xml` (≈85 Mo) — flux XML complet toutes catégories
- `products_sizesFR4.xml` (≈1 Mo) — sous-ensemble Sacs et Accessoires (fichier test)

### Structure XML par produit

```xml
<product id="...">
    <name>, <brand>, <category_path>, <category id="...">,
    <color>, <type>, <price>, <description> (prose + composition),
    <images>/<image_url> (1-4 URLs),
    <options>/<option id="..."> (option_name, STOCK, ean, avaible_in)
</product>
```

### Statistiques (fichier test Sacs & Accessoires)

- 702 produits, 0 champ manquant (100% complétude)
- 3 catégories, 8 marques, 15 couleurs, 8 types
- 850 EAN présents (100%), 1-4 images par produit (moy. 3.3)

## Script de conversion

- [[matterhorn_to_prestashop.py]] — script unique XML → CSV PrestaShop 8. Remplace l'ancienne chaîne `extract_xml.py` → `netoyage.py` → `to_prestashop.py`. Gère prix (×coef), stock, EAN, catégories mappées, images, déclinaisons tailles. Option `--filtre` pour ne traiter qu'un univers.

## Cartographie des catégories

Le mapping catégories Matterhorn → PrestaShop est intégré directement dans le script `matterhorn_to_prestashop.py` (dictionnaire `CATEGORY_MAP`). À compléter lors du traitement du fichier complet 85 Mo avec toutes les catégories.

> Réflexion stratégique sur l'arborescence : voir [[Structure-catalogue]] et [[Univers-et-categories]] (dossier 01-Plan).

## Anciens fichiers (supprimés le 2026-06-11)

Les fichiers suivants de l'ancienne chaîne ont été supprimés lors du passage au flux XML v2 :

- `products_ver2__sizesFR.xml` (ancien flux XML v1, ≈168 Mo)
- `product_feed_fr_*.csv` (ancien flux CSV, ≈36 Mo)
- `catalogue_complet.csv`, `catalogue_complet.xml`
- Fichiers par univers : `lingerie.csv`, `lingerie_net.csv`, `lingerie_net_enrichi.csv`, `maillots.csv`, `maillots_nettoyes.csv`, `maillots_prestashop_import.csv`, `vetements.csv`, `vetements_net.csv`, `sacs_accessoires.csv`, `sac_net.csv`
- Fichiers de mapping : `categories_prestashop.csv`, `categories_prestashop_raffinees.csv`, `nouvelle_arbo.csv`, `Mapping_Categories_Fournisseur_Boutique.csv/.xlsx`, `Correspondance_Categories_Raffinées.xlsx`

## Prochaines étapes

1. Lancer `matterhorn_to_prestashop.py` sur le fichier complet (85 Mo) pour cartographier toutes les catégories
2. Compléter le `CATEGORY_MAP` dans le script avec l'arborescence PrestaShop cible
3. Demander à Matterhorn la documentation API pour la synchro continue (stock/prix)
4. Monter un workflow n8n pour l'automatisation des mises à jour
