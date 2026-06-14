---
date: 2026-06-09
tags: [ressources, partage, reutilisable]
type: index
status: active
---

# 🔗 Hub — Ressources partagées

Briques réutilisables d'une boutique à l'autre. Elles **vivent dans Plaisirs de Femmes** (premier projet) ; les autres projets y font référence par lien plutôt que de les recopier. Quand une brique est améliorée, elle l'est une seule fois, ici référencée.

## Traitement des données

- [[netoyage.py]] — nettoyage CSV générique (encodage, HTML, colonnes décalées, prix FR). Applicable à n'importe quel catalogue fournisseur.
- Application graphique de traitement CSV — voir [[Conversation - Application traitement CSV]] (chargement, découpage, mapping PrestaShop, fusion).

## Descriptions produits (IA)

- [[Workflow - Génération descriptions IA]] — pipeline export → source → nettoyage → génération → réimport. Réutilisable tel quel ; seul le connecteur fournisseur change.
- [[Prompt - Voix de la maison (descriptions)]] — **gabarit** de prompt. À **dupliquer et réécrire** pour chaque marque (la voix « bien-être / oriental » d'Omardemogador ≠ la voix « lingerie » de Plaisirs de Femmes).

## Patterns Dev

- Connecteur fournisseur → PrestaShop : [[matterhorn_connector.php]] sert de **modèle d'architecture** (idempotent, match sur référence, marge paramétrable, clé API hors racine). À réimplémenter par grossiste.
- Export PrestaShop des produits sans description : [[export.php]].

## Administratif

- [[Formulaire_TVA_intracommunautaire_rempli.pdf]] — demande d'attribution du numéro de TVA intracommunautaire auprès du SIE de La Rochelle (SIRET 499 108 545 00020). Concerne les deux boutiques : achats intra-UE < 10 000 €, régime dérogatoire. Envoyé le 11 juin 2026.

## À ne PAS mutualiser

Tout ce qui est spécifique à un fournisseur (clés API, whitelists de marques, mapping de catégories) ou à une marque (voix, branding, design system) reste dans son projet.
