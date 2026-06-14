---
date: 2026-06-10
tags: [dev, prestashop, matterhorn, api, import]
type: index
status: active
---

# 🛒 Index — PrestaShop & Matterhorn

Intégration entre le grossiste **Matterhorn Wholesale** et la boutique **PrestaShop 8.2.6** de plaisirs-de-femmes.fr.

---

## Pipeline actif (2026-06-10)

- [[csv_to_prestashop.py]] — **source principale**. Lit le gros CSV fournisseur Matterhorn, filtre marques whitelist + stock > 0, mappe path FR → sous-catégories PS, explose `sizes_stock` en déclinaisons avec EAN et SKU par taille. Sortie : UTF-8 BOM, séparateur `;`, format Simple CSV Import. Options : `--in`, `--out`, `--univers`, `--marque`, `--limit`. ✅ Actif.

---

## Scripts API Matterhorn (complémentaires)

- [[mh_fetch_catalog.php]] — export brut API Matterhorn → CSV. Utile pour **syncs de stock ponctuelles** (prix temps réel, stock API). Filtre stock > 0, prix EUR uniquement. Options : `--brand=`, `--limit=`, `--out=`. ✅ Opérationnel.
- [[mh_prepare_import.php]] — ancienne version CSV brut API → Simple CSV Import. **Remplacé par `csv_to_prestashop.py`**. Conservé pour référence. 🗄️ Archivé.

---

## Connecteur Matterhorn (archivé)

- [[matterhorn_connector.php]] — connecteur direct Matterhorn → PrestaShop via API. Idempotent, match sur référence `MH{id}`. Marge `MARGIN_COEF = 2.5`. **Ne plus faire tourner en cron.** Conservé comme modèle d'architecture et pour syncs ponctuelles (`--brand=X --apply`). 🗄️ Archivé.

---

## Export / inspection SQL

- [[export.php]] — requête SQL PS : exporte les produits `MH%` sans description → `produits_a_decrire.csv`.
- [[extract2.php]] — appelle l'API Matterhorn (`ITEMS/`) pour récupérer descriptions filtrées sur les références en boutique.
- [[test_api.php]] — diagnostic : inspecte un item API pour une marque donnée.

---

## Maintenance (⚠️ destructif)

- [[suppression_de_produits_prestashop.php]] — supprime tous les produits par lots de 100. Mode `?dryrun=1` disponible. **À manier avec une extrême prudence.**

---

> Scripts Python d'extraction/nettoyage : voir [[Index - Scripts]].
> Décisions et journal : voir [[Journal-de-projet]].
