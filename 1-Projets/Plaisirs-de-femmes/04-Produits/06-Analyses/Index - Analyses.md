---
date: 2026-06-09
tags: [produits, analyse, qualite-donnees]
type: index
status: active
---

# 🔎 Index — Analyses

- `refs_manquantes.csv` — références présentes côté boutique mais introuvables (ou mal rattachées) dans la source fournisseur. Analysées par [[exploit3.py]], qui vérifie si chaque référence existe comme `<product>`, membre de `<set>`, ou option/taille dans le XML.
