---
date: 2026-06-09
tags: [ia, conversation, csv, outil, python, prestashop]
type: conversation
status: active
---

# 💬 Application graphique de traitement CSV

Session de conception d'une **application Python à interface graphique** pour manipuler les gros fichiers CSV fournisseur (encodage, découpage, nettoyage, mapping PrestaShop, fusion).

## Besoin

Charger de gros CSV, corriger l'encodage (français — `é è € `, plus de « hiéroglyphes »), découper selon un critère (marque, catégorie…), et exporter des fichiers prêts pour Excel / PrestaShop.

## Fonctions livrées

**v1**
- **Chargement** : détection auto de l'encodage via `chardet` (lecture des 200 premiers ko).
- **Lecture** : choix du séparateur source (`;` Excel FR / `,` PrestaShop), forçage d'encodage possible.
- **Aperçu & stats** : tableau des N premières lignes, comptage des valeurs manquantes.
- **Découpage** : par colonne (marque, catégorie…), filtrage sur valeurs précises, max lignes/fichier.
- **Export** : 5 encodages dont `UTF-8-BOM` (Excel FR) et `UTF-8` (PrestaShop) ; noms de fichiers assainis.

**v2 (3 onglets ajoutés)**
- **🧹 Nettoyage** : suppression de doublons, normalisation des prix français (`1.234,56 €` → `1234.56`), nettoyage du texte.
- **🗂️ Cartographie PS** : mapping des colonnes vers ~60 champs PrestaShop standards, pré-matching auto (`brand`→`manufacturer`, `stock`→`quantity`), sauvegarde du mapping en JSON réutilisable.
- **🔗 Fusion CSV** : empilement vertical ou jointure par clé (`reference`, `ean13`…), modes `outer`/`inner`/`left`.

## Distribution

Trois fichiers livrés + `installer_et_lancer.bat` (installe les dépendances et lance l'app). *(Code produit dans une session de travail dédiée ; à rapatrier dans [[Index - Scripts]] si tu souhaites le versionner dans le vault.)*

## Liens

- Scripts de la même chaîne : [[Index - Scripts]]
- Données concernées : [[Index - Imports-Exports]]
