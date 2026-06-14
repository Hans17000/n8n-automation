---
date: 2026-06-07
tags: [ia, conversation, catalogue, categories, prestashop, balneaire]
type: conversation
status: active
---

# 💬 Restructuration des catégories — La Garde-Robe

Session de travail sur la restructuration des catégories du catalogue, univers **balnéaire / maillots** (« La Garde-Robe »), aboutissant à un fichier d'import PrestaShop.

## Contexte

Sélection de **30 produits** répartis en trois familles : Balnéaire Deux Pièces, Balnéaire Une Pièce, Échappées Balnéaires. Objectif : produire un CSV d'import PrestaShop propre, avec déclinaisons de tailles explosées.

## Décisions actées

- **Doublons** → supprimés / mis de côté (ex. références Ewlon vert 214341 / 214342). À revoir plus tard.
- **Produits une seule taille** → écartés car peu utiles en boutique (ex. 211878 Ava). Remplacés par des articles mieux déclinés : **211419** Marko noir (4 tailles) pour Deux Pièces, **164287** Marko multicouleur (3 tailles) pour Une Pièce.
- **Article ancien mais classique** → conservé : 112272 Marko (2018, 72 en stock) — « si ça se vend encore après 8 ans, c'est un classique ».
- **Prix limites** (ex. 194082 Etna à 113,80 €) → acceptés vu le positionnement haute couture.

## Livrable

Fichier d'import PrestaShop : **30 produits, 95 lignes** (base + déclinaisons de tailles), UTF-8 BOM, séparateur `;`. Contient : catégories raffinées, **prix boutique = grossiste × 2**, références `PDF-{id}`, URLs images fournisseur, une ligne de combinaison par taille (SKU + stock).

## Suite prévue

Les descriptions sont encore les noms fonctionnels du fournisseur → passe de réécriture en « ton maison haute couture » (voir [[Workflow - Génération descriptions IA]]).

## Liens

- Données catégories : [[Index - Imports-Exports]]
- Stratégie d'arborescence : [[Structure-catalogue]], [[Univers-et-categories]]
