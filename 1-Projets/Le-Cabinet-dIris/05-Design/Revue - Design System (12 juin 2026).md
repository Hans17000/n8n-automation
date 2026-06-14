---
date: 2026-06-12
tags: [design, revue]
type: note
status: active
---

# Revue du Design System — 12 juin 2026

Livrable de Claude Design, déposé dans `02-Dev/03-Design/`.

## Verdict global

Excellent travail. Le design system est fidèle au brief, structuré professionnellement, et directement exploitable par Claude Code.

## Ce qui est conforme au brief

### Palette — 100% conforme
- Les 5 couleurs du brief sont reprises à l'identique (Noir d'encre `#1A1A2E`, Or antique `#C9A96E`, Ivoire `#F5F0E8`, Prune `#4A2040`, Bordeaux `#6B2D3E`)
- Variantes ajoutées (primary-light/dark, accent-light/dark, background-dark) — cohérentes
- Aliases sémantiques (surface-page, surface-dark, text-body, text-price...) — bonus utile pour Claude Code

### Typographie — 100% conforme
- Cormorant Garamond pour titres/nav/boutons, Lato pour corps/prix/badges, Pinyon Script pour citations d'Iris
- Poids respectés : 600 titres, 400 hero/nav, 300 prix
- Letter-spacings généreux conformes au brief (nav 0.15em, boutons 0.1em, sous-titres 0.2em)

### Formes et espacements — conforme
- Radius 0 partout (1px badges, 2px bouton cabinet-entry) — univers rectiligne respecté
- Hairlines dorées 0.5px — conforme
- Transitions 0.3s ease uniquement — conforme (« tout fond, rien ne saute »)

### Lexique de marque — scrupuleusement respecté
- « Pièce rare » (pas « Plus que 2 en stock ! »)
- « Poussez la porte » (pas « 18+ » ou « adultes »)
- « Sélection d'Iris », « Les Carnets d'Iris »
- Vouvoiement systématique
- Aucun emoji, aucune exclamation

### Composants livrés
| Composant | Variantes | Statut |
|-----------|----------|--------|
| Button | primary, secondary, cabinet-entry, ghost | OK |
| Badge | rare, cabinet | OK |
| PriceTag | — | OK |
| SectionTitle | avec sous-titre optionnel | OK |
| EditorialText | — | OK |
| Separator | — | OK |
| IrisQuote | — | OK |
| ReassuranceItem | — | OK |
| ProductCard | avec badge, catégorie, hover | OK |
| CategoryTile | tone vitrine/cabinet | OK |

### UI Kit boutique
Maquette interactive complète avec navigation entre :
- Homepage (hero, Sélection d'Iris, univers, citation, Carnets)
- Page sas « Poussez la porte » (confirmation 18+)
- Le Cabinet (6 catégories prune)
- Pages catégorie (éditorial d'Iris + grille produits)
- Fiche produit (cadre passe-partout, badges, réassurance)

## Points d'attention pour Claude Code

### 1. Format JSX → Smarty/TPL
Les composants sont en React/JSX. PrestaShop utilise des templates Smarty (.tpl). Claude Code devra :
- **Importer les tokens CSS tels quels** (`colors.css`, `typography.css`, `spacing.css`) dans le thème enfant
- **Traduire la logique des composants JSX** en markup HTML/Smarty + CSS natif
- Les fichiers JSX servent de **référence visuelle et de spécification**, pas de code à copier

### 2. Placeholders à remplacer
| Élément | Statut | Action requise |
|---------|--------|----------------|
| Photo hero clair-obscur | Placeholder (aplat noir) | Omar doit fournir ou acheter une photo |
| Monogramme / Logo SVG | Placeholder typo (« I » entre filets) | À créer (brief design prévu — ou commande externe) |
| Icônes custom (clé, cadenas, plume, écrin, flacon) | Lucide en substitution (flagué) | À créer ou acheter un set cohérent |

### 3. Fichiers directement exploitables par Claude Code
```
02-Dev/03-Design/tokens/colors.css       → copier dans le thème enfant
02-Dev/03-Design/tokens/typography.css    → copier (ajuster @import Google Fonts si déjà chargé)
02-Dev/03-Design/tokens/spacing.css      → copier
02-Dev/03-Design/styles.css              → point d'entrée, importe les 3 tokens
```

### 4. Guidelines HTML à consulter
Les fichiers `guidelines/*.html` contiennent des spécimens visuels pour :
- Palette et variantes
- Hiérarchie typographique
- Espacements et bordures
- Monogramme, séparateurs, réassurance
- États hover et animations

## Actions restantes

- [ ] Fournir la photo hero clair-obscur
- [ ] Créer le logo/monogramme SVG définitif
- [ ] Créer ou acheter les icônes custom gravure
- [ ] Mettre à jour le brief Claude Code (en cours)
- [ ] Lancer Claude Code quand il voudra bien démarrer
