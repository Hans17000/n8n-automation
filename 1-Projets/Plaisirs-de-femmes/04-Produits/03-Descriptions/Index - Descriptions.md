---
date: 2026-06-09
tags: [produits, descriptions, ia, seo]
type: index
status: active
---

# ✍️ Index — Descriptions produits

Chaîne de production des descriptions françaises, réécrites pour l'unicité Google (pas de copie de la source fournisseur).

- `produits_a_decrire.csv` — liste des références **sans description** exportée de PrestaShop par [[export.php]] (référence, nom, marque, catégorie). Entrée de la génération IA.
- `produits_mistral.csv` / `produits_mistral1.csv` — données produit préparées pour l'IA (référence, nom, couleur, type, texte source), issues de [[exploit.py]] / [[exploit2.py]].
- `descriptions.csv` — **sortie finale** : descriptions courtes + longues générées en français par [[mistral.py]] (Mistral via LM Studio).
- `refs_sans_description.csv` — *(vide / placeholder)* — suivi des références restant à décrire.

> Voix de la maison et règles rédactionnelles : voir le prompt système dans [[06-IA/Prompts]] et le workflow dans [[06-IA/Workflows]].
