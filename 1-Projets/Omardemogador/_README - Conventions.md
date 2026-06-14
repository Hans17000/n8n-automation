---
date: 2026-06-09
tags: [template, boutique, mode-emploi]
type: template
status: active
---

# 🧩 Template — Projet Boutique

Squelette standard d'une boutique e-commerce. **À cloner** dans `1-Projets/` pour chaque nouvelle boutique, puis renommer le dossier au nom du projet.

## Mode d'emploi

1. Copier le dossier `Template-Boutique` dans `1-Projets/` et le renommer (ex. `Omardemogador`).
2. Remplir d'abord `01-Plan/Vision`, `Objectifs`, `Branding` — ils orientent tout le reste, jusqu'au ton des descriptions IA.
3. Au fil du travail, déposer le code dans `02-Dev`, les données dans `04-Produits`, le design dans `05-Design`, et journaliser les sessions dans `06-IA`.
4. Tenir à jour le `MOC` du projet (point d'entrée).

## Convention de notes

Frontmatter YAML sur chaque note :

```yaml
---
date: AAAA-MM-JJ
tags: []
type: note | index | conversation | workflow | prompt | moc | template
status: active | archive
---
```

Liens internes en `[[Nom de la note]]`. Une note d'index par dossier de données/code (`Index - …`).

## Arborescence

- `01-Plan` — vision, objectifs, branding, personas, roadmap, structure catalogue.
- `02-Dev` — specs, scripts, tests, automatisation, PrestaShop, StoreCommander, erreurs.
- `03-SEO` — catégories, clusters, pages piliers.
- `04-Produits` — fiches, photos, descriptions, variantes, imports/exports, analyses.
- `05-Design` — design system, maquettes, identité visuelle.
- `06-IA` — conversations, prompts, workflows.

## Ressources mutualisées

Les briques réutilisables entre boutiques (nettoyage CSV, workflow + prompt descriptions, patterns design) vivent dans [[Hub - Ressources partagées]]. Ne pas les recopier ici : y faire référence par lien.
