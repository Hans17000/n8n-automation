---
date: 2026-06-10
tags: [roadmap, planning]
type: roadmap
status: active
---

# 🗺️ Roadmap — plaisirs-de-femmes.fr

## ✅ Fait

- Infrastructure VPS (Ubuntu 24.04, CloudPanel, Nginx, Mailcow)
- PrestaShop 8.2.6 installé et configuré
- Arborescence catégories créée (7 univers, ~60 sous-catégories)
- Fournisseur Matterhorn intégré (API + CSV analysés)
- Cron matterhorn_connector.php désactivé
- Pipeline CSV → Simple CSV Import opérationnel (`csv_to_prestashop.py`)
- Premier export lingerie : 322 produits, 2 774 déclinaisons prêts à importer
- Nouveau pipeline XML v2 : `matterhorn_to_prestashop.py` (script unique, remplace l'ancienne chaîne)
- Script top 10 bestsellers par catégorie : `top10_xml.py` (669 produits sélectionnés sur 30 546)
- Mapping CATEGORY_MAP finalisé : 65 entrées, 72 catégories Matterhorn → 7 univers PS poétiques
- Coefficient prix validé : ×2.2 (marge ~55%)
- Test import Simple Import : 425 produits, 0 erreurs, format déclinaisons corrigé

## 🔄 En cours

- Nettoyage attribut « Taille:select:0 » résiduel dans PS
- Nettoyage catégories orphelines (IDs 71–106)

## 🔲 À faire (par priorité)

1. Créer l'univers Chaussures + 10 sous-catégories dans le backoffice PS
2. Lancer `top10_xml.py` sur le fichier complet (85 Mo) en local et importer le CSV résultant
3. Pipeline descriptions Gemma en local — raffiner le ton maison
4. Beautification noms produits via Gemma
5. SEO — balises titre, meta descriptions, URLs simplifiées par catégorie
6. Demander doc API Matterhorn pour sync stock/prix automatique
7. Workflow n8n pour mises à jour automatisées
8. Lancement omardemogador.fr (même moteur technique, voix Mogador)
