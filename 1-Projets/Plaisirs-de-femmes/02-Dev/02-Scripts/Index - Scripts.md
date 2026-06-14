---
date: 2026-06-10
tags: [dev, scripts, python, php, catalogue]
type: index
status: active
---

# 🧰 Index — Scripts

Scripts de traitement du catalogue **plaisirs-de-femmes.fr**.

---

## Pipeline principal (actif)

- [[csv_to_prestashop.py]] — **source principale catalogue**. Lit le gros CSV fournisseur Matterhorn (UTF-8 ou Latin-1, tab ou virgule), filtre marques whitelist + stock > 0, mappe path FR → sous-catégories PS, explose `sizes_stock` en déclinaisons (EAN + SKU par taille). Sortie : UTF-8 BOM, séparateur `;`, format Simple CSV Import. Options : `--in`, `--out`, `--univers`, `--marque`, `--limit`. ✅ Actif.

---

## Scripts API Matterhorn (complémentaires)

Voir [[Index - PrestaShop]] pour le détail.

- [[mh_fetch_catalog.php]] — export brut API → CSV (utile pour syncs stock temps réel).
- [[mh_prepare_import.php]] — ancienne version API → Simple CSV Import. 🗄️ Archivé.
- [[matterhorn_connector.php]] — connecteur direct API → PS. 🗄️ Archivé.

---

## Anciens scripts d'extraction XML/CSV (référence)

Ces scripts précèdent le pipeline CSV direct. Conservés pour référence ou cas particuliers.

- [[extract_xml.py]] — parcourt `products_ver2__sizesFR.xml` (≈168 Mo) en streaming (`iterparse`) → `catalogue_complet.csv`.
- [[exploit.py]] — extrait uniquement les produits présents en boutique (intersection avec `produits_a_decrire.csv`). Sortie : `produits_mistral.csv`.
- [[exploit2.py]] — variante de `exploit.py` → `produits_mistral1.csv`, trace les références sans description.
- [[exploit4.py]] — même objectif mais source = CSV fournisseur `product_feed_fr_*.csv` (≈35 Mo).
- [[exploit3.py]] — diagnostic références manquantes : compare `refs_manquantes.csv` aux ids du XML.

---

## Nettoyage

- [[netoyage.py]] — nettoyage CSV avec pandas : réaligne colonnes décalées, supprime HTML, normalise espaces. Réutilisable sur tout fichier catalogue.

---

## Génération de descriptions (IA)

- [[mistral.py]] — réécrit les descriptions en français via Mistral / LM Studio (`localhost:1234`). Entrée `produits_a_decrire.csv` → sortie `descriptions.csv`. Voir [[Workflow - Génération descriptions IA]].

---

## Backend site

- [[conseil-handler.php]] — traitant du formulaire « Demander conseil ». Valide et envoie à `contact@plaisirs-de-femmes.fr`.

---

> Scripts PrestaShop / API Matterhorn : voir [[Index - PrestaShop]].
> Données catalogue (CSV, XML, mapping catégories) : voir [[Index - Imports-Exports]].
