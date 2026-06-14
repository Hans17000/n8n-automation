---
date: 2026-06-09
tags: [ia, workflow, descriptions, seo, mistral]
type: workflow
status: active
---

# 🔄 Workflow — Génération des descriptions produits (IA)

Pipeline complet de réécriture des descriptions fournisseur en français, dans la voix de la maison, pour l'unicité SEO.

## Étapes

1. **Exporter les références à décrire** — [[export.php]] interroge PrestaShop et sort `produits_a_decrire.csv` (produits `MH%` sans description).
2. **Récupérer le texte source** — soit depuis le XML fournisseur via [[exploit.py]] / [[exploit2.py]], soit depuis le CSV feed via [[exploit4.py]], soit via l'API Matterhorn ([[extract2.php]]). Sortie : `produits_mistral.csv`.
3. **Nettoyer** — [[netoyage.py]] : retire le HTML, réaligne les colonnes, normalise les espaces.
4. **Générer** — [[mistral.py]] appelle Mistral (LM Studio, `localhost:1234`) avec le prompt système maison → `descriptions.csv` (description courte + longue, JSON strict). Pilote limité à 20 fiches (`LIMIT`), passer à 0 pour tout traiter.
5. **Réimporter** dans PrestaShop.

## Garde-fous

- Réécriture, pas traduction littérale (aucune phrase ne calque la source).
- Fidélité stricte aux faits (matières, coloris, coupe) — pas d'invention.
- Les tailles / tableaux de mesures sont ignorés.

## Liens

- Prompt système : [[Prompt - Voix de la maison (descriptions)]]
- Données : [[Index - Descriptions]]
