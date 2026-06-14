# BRIEF — Customisation Thème Milibido → Le Cabinet d'Iris

> Ce document est un brief autonome. Copie-le tel quel dans une session Claude Code pour obtenir les modifications du thème PrestaShop.

---

## Contexte

**Projet** : Le Cabinet d'Iris — boutique e-commerce lifestyle sensuel sur PrestaShop 8.x.
**Thème de base** : Milibido (BonTheme) — thème PrestaShop pour sexshop/lingerie. Licence acquise, déjà installé.
**Objectif** : Transformer le design « sexshop générique » de Milibido en univers « cabinet de curiosités élégant ».

Le concept repose sur **deux niveaux de navigation** :
- **La Vitrine** : lingerie fine, cosmétiques, nuisettes (5 catégories)
- **Le Cabinet** : sextoys, fétiche, BDSM élégant (6 catégories), accessible via un bouton « Poussez la porte »

---

## 1. Palette CSS — Variables à remplacer

Remplacer toutes les couleurs du thème Milibido par cette palette :

```css
:root {
  /* Couleurs principales */
  --color-primary: #1A1A2E;       /* Noir d'encre — fonds, texte principal */
  --color-accent: #C9A96E;        /* Or antique — accents, bordures, logo, prix */
  --color-background: #F5F0E8;    /* Ivoire — fond pages, fiches produit */
  --color-cabinet: #4A2040;       /* Prune — catégories Cabinet, CTA secondaires */
  --color-alert: #6B2D3E;         /* Bordeaux — alertes stock, badges */
  
  /* Variantes */
  --color-primary-light: #2A2A4E;
  --color-primary-dark: #0F0F1A;
  --color-accent-light: #D4BC8A;
  --color-accent-dark: #A88B52;
  --color-background-dark: #EBE5D9;
  
  /* Texte */
  --color-text-primary: #1A1A2E;
  --color-text-secondary: #5A5A6E;
  --color-text-on-dark: #F5F0E8;
  --color-text-on-accent: #1A1A2E;
  
  /* Bordures */
  --color-border: rgba(201, 169, 110, 0.3);  /* Or antique 30% */
  --color-border-strong: #C9A96E;
  
  /* Boutons */
  --color-btn-primary-bg: #C9A96E;
  --color-btn-primary-text: #1A1A2E;
  --color-btn-primary-hover: #A88B52;
  --color-btn-secondary-bg: transparent;
  --color-btn-secondary-text: #C9A96E;
  --color-btn-secondary-border: #C9A96E;
}
```

**Méthode** : Identifier le fichier CSS principal du thème Milibido (probablement `themes/milibido/assets/css/theme.css` ou compilé depuis SASS/LESS). Rechercher toutes les valeurs de couleur hardcodées et les remplacer par les variables ci-dessus. Si le thème utilise SASS, modifier les variables source et recompiler.

---

## 2. Typographie

**Charger via Google Fonts** dans le `<head>` du thème :

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
```

**CSS typographique** :

```css
/* Titres */
h1, h2, h3, .product-title, .category-name, .brand-name {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: var(--color-primary);
}

/* Corps */
body, p, .product-description, .category-description {
  font-family: 'Lato', 'Helvetica Neue', sans-serif;
  font-weight: 400;
  font-size: 15px;
  line-height: 1.7;
  color: var(--color-text-primary);
}

/* Prix */
.product-price, .price {
  font-family: 'Lato', sans-serif;
  font-weight: 300;
  color: var(--color-accent);
  letter-spacing: 0.05em;
}

/* Tailles de titres */
h1 { font-size: 2rem; }
h2 { font-size: 1.6rem; }
h3 { font-size: 1.3rem; }
```

---

## 3. Header et navigation

### Structure du menu principal

```
[Logo Le Cabinet d'Iris]

Les Étoffes    Les Nuits    Les Voiles    Les Élixirs    Les Écrins    |    Poussez la porte
```

Les 5 premières entrées = La Vitrine (catégories publiques).
Le dernier élément « Poussez la porte » = lien vers Le Cabinet.

### CSS du header

```css
/* Header */
header, .header-nav {
  background-color: var(--color-primary);
  border-bottom: 1px solid var(--color-accent);
}

/* Navigation links */
.main-menu a, .top-menu a {
  font-family: 'Cormorant Garamond', serif;
  font-weight: 400;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--color-text-on-dark);
  transition: color 0.3s ease;
}

.main-menu a:hover {
  color: var(--color-accent);
}

/* Séparateur avant "Poussez la porte" */
.menu-separator {
  display: inline-block;
  width: 1px;
  height: 20px;
  background-color: var(--color-accent);
  margin: 0 20px;
  vertical-align: middle;
}

/* Bouton "Poussez la porte" — style distinct */
.cabinet-entry {
  font-family: 'Cormorant Garamond', serif;
  font-style: italic;
  color: var(--color-accent) !important;
  border: 1px solid var(--color-accent);
  padding: 6px 18px;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.cabinet-entry:hover {
  background-color: var(--color-accent);
  color: var(--color-primary) !important;
}
```

---

## 4. Homepage

### Hero section

Remplacer le slider promo par défaut de Milibido par un hero sobre :

```html
<section class="hero-cabinet">
  <div class="hero-overlay">
    <h1>Le Cabinet d'Iris</h1>
    <p class="hero-subtitle">Collection privée de curiosités sensuelles</p>
    <a href="/la-vitrine" class="btn-vitrine">Entrer dans la Vitrine</a>
  </div>
</section>
```

```css
.hero-cabinet {
  position: relative;
  height: 70vh;
  background-color: var(--color-primary);
  background-image: url('img/hero-bg.jpg'); /* Photo clair-obscur à fournir */
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-overlay {
  text-align: center;
  padding: 40px;
}

.hero-cabinet h1 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 3.5rem;
  font-weight: 400;
  color: var(--color-text-on-dark);
  letter-spacing: 0.1em;
  margin-bottom: 10px;
}

.hero-subtitle {
  font-family: 'Lato', sans-serif;
  font-weight: 300;
  font-size: 1.1rem;
  color: var(--color-accent);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin-bottom: 40px;
}

.btn-vitrine {
  font-family: 'Cormorant Garamond', serif;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--color-accent);
  border: 1px solid var(--color-accent);
  padding: 12px 40px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-vitrine:hover {
  background-color: var(--color-accent);
  color: var(--color-primary);
}
```

### Sections homepage après le hero

1. **Sélection d'Iris** — grille 4 produits curatés avec bordure dorée fine
2. **Les univers** — 2 colonnes (Vitrine à gauche, Cabinet à droite) avec visuels
3. **Les Carnets d'Iris** — 3 derniers articles du blog

---

## 5. Fiches produit

### Modifications de layout

```css
/* Cadre autour de l'image produit */
.product-cover img {
  border: 0.5px solid var(--color-border-strong);
  padding: 8px;
  background: var(--color-background);
}

/* Nom du produit */
.product-detail h1 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 8px;
}

/* Prix */
.product-price .current-price {
  font-family: 'Lato', sans-serif;
  font-weight: 300;
  font-size: 1.6rem;
  color: var(--color-accent);
}

/* Description produit */
.product-description {
  font-family: 'Lato', sans-serif;
  line-height: 1.8;
  color: var(--color-text-secondary);
}

/* Bouton Ajouter au panier */
.add-to-cart {
  background-color: var(--color-accent);
  color: var(--color-primary);
  font-family: 'Cormorant Garamond', serif;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border: none;
  padding: 14px 40px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.add-to-cart:hover {
  background-color: var(--color-accent-dark);
}

/* Badge "Pièce rare" (stock bas) */
.badge-rare {
  background-color: var(--color-alert);
  color: var(--color-text-on-dark);
  font-family: 'Lato', sans-serif;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 4px 12px;
  border-radius: 1px;
}

/* Badge "Cabinet" (catégorie niveau 2) */
.badge-cabinet {
  background-color: var(--color-cabinet);
  color: var(--color-text-on-dark);
  font-family: 'Lato', sans-serif;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 4px 12px;
  border-radius: 1px;
}
```

---

## 6. Pages catégories

### Texte éditorial en tête de catégorie

Chaque catégorie a un texte d'introduction (rédigé dans le ton d'Iris). Placer ce bloc avant la grille produits :

```css
.category-description {
  max-width: 700px;
  margin: 0 auto 40px;
  text-align: center;
  font-family: 'Lato', sans-serif;
  font-style: italic;
  color: var(--color-text-secondary);
  line-height: 1.8;
  padding: 30px 20px;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}
```

### Grille produits

```css
.products-grid .product-miniature {
  border: 0.5px solid var(--color-border);
  background: var(--color-background);
  transition: border-color 0.3s ease;
}

.products-grid .product-miniature:hover {
  border-color: var(--color-accent);
}
```

---

## 7. Footer

```css
footer, .footer-container {
  background-color: var(--color-primary);
  color: var(--color-text-on-dark);
  border-top: 1px solid var(--color-accent);
}

footer h4 {
  font-family: 'Cormorant Garamond', serif;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-accent);
  font-size: 14px;
}

footer a {
  color: var(--color-text-on-dark);
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

footer a:hover {
  opacity: 1;
  color: var(--color-accent);
}
```

### Blocs de réassurance (footer ou pré-footer)

Remplacer les icônes par défaut par :
- « Livraison discrète » — icône boîte neutre
- « Paiement sécurisé » — icône cadenas
- « Curation Iris » — icône clé ancienne
- « Retours sous 14j » — icône flèche retour

Style : icône or antique, texte ivoire, fond noir d'encre, disposition horizontale 4 colonnes.

---

## 8. Transition Vitrine → Cabinet

### Implémentation du mécanisme « Poussez la porte »

**Option A — Page interstitielle** (recommandée pour le SEO et la conformité) :

Créer une page CMS PrestaShop `/le-cabinet` qui sert de sas :

```html
<section class="cabinet-gate">
  <div class="gate-content">
    <div class="gate-monogram"><!-- SVG monogramme Iris --></div>
    <h1>Le Cabinet</h1>
    <p>Iris a rassemblé ici ce qu'elle ne montre qu'à ceux qui poussent la porte.</p>
    <p class="gate-notice">En entrant, vous confirmez avoir plus de 18 ans.</p>
    <a href="/le-cabinet/les-apparitions" class="btn-enter">Entrer</a>
    <a href="/" class="btn-back">Retourner à la Vitrine</a>
  </div>
</section>
```

```css
.cabinet-gate {
  min-height: 80vh;
  background-color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.gate-monogram {
  width: 80px;
  height: 80px;
  margin: 0 auto 30px;
  opacity: 0.8;
}

.cabinet-gate h1 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.5rem;
  font-weight: 400;
  color: var(--color-text-on-dark);
  letter-spacing: 0.15em;
  margin-bottom: 15px;
}

.cabinet-gate p {
  font-family: 'Lato', sans-serif;
  color: var(--color-text-on-dark);
  opacity: 0.7;
  max-width: 500px;
  margin: 0 auto 10px;
}

.gate-notice {
  font-size: 13px;
  margin-bottom: 30px !important;
}

.btn-enter {
  display: inline-block;
  font-family: 'Cormorant Garamond', serif;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--color-primary);
  background-color: var(--color-accent);
  padding: 14px 50px;
  text-decoration: none;
  margin-right: 15px;
  transition: all 0.3s ease;
}

.btn-enter:hover {
  background-color: var(--color-accent-light);
}

.btn-back {
  display: inline-block;
  font-family: 'Lato', sans-serif;
  font-size: 13px;
  color: var(--color-text-on-dark);
  opacity: 0.5;
  text-decoration: underline;
}
```

**Option B — Menu déroulant** (plus simple) :

Le lien « Poussez la porte » dans le menu ouvre un mega-menu sombre listant les 6 catégories du Cabinet avec descriptions courtes.

---

## 9. Arborescence des catégories PrestaShop

### Niveau 1 — La Vitrine
```
La Vitrine (catégorie parente, non affichée directement)
├── Les Étoffes (id_parent: La Vitrine)
├── Les Nuits
├── Les Voiles
├── Les Élixirs
└── Les Écrins
```

### Niveau 2 — Le Cabinet
```
Le Cabinet (catégorie parente)
├── Les Apparitions
├── Les Objets
├── Les Confessions
├── Les Complicités
├── Le Boudoir Noir
└── Les Caprices
```

---

## 10. Fichiers à identifier et modifier dans Milibido

Le thème Milibido est structuré en standard PrestaShop. Les fichiers clés à modifier :

| Fichier | Modification |
|---------|-------------|
| `themes/milibido/templates/_partials/header.tpl` | Logo, navigation, bouton « Poussez la porte » |
| `themes/milibido/templates/index.tpl` | Hero section, grille homepage |
| `themes/milibido/templates/catalog/product.tpl` | Layout fiche produit, badges |
| `themes/milibido/templates/catalog/listing/product-list.tpl` | Grille catégorie |
| `themes/milibido/templates/_partials/footer.tpl` | Footer et réassurance |
| `themes/milibido/assets/css/theme.css` (ou SASS source) | Toutes les couleurs, typos, espacements |
| `themes/milibido/config/theme.yml` | Configuration des hooks et modules |

### Important — thème enfant

**Créer un thème enfant** (`cabinet-iris`) qui hérite de Milibido pour ne pas perdre les modifications lors d'une mise à jour du thème parent :

```
themes/
├── milibido/           ← thème parent, ne pas modifier
└── cabinet-iris/       ← thème enfant
    ├── config/
    │   └── theme.yml
    ├── assets/
    │   └── css/
    │       └── custom.css
    ├── templates/
    │   └── _partials/
    │       ├── header.tpl
    │       └── footer.tpl
    └── preview.png
```

---

## 11. Modules PrestaShop à configurer

| Module | Statut | Notes |
|--------|--------|-------|
| Module Busyx | Déjà acquis | Configurer l'import catalogue |
| Module Tendance Sensuelle | À vérifier | Import CSV ou module dédié |
| Blog (Prestablog ou similaire) | À installer | Pour « Les Carnets d'Iris » |
| Réassurance | Natif PrestaShop | Remplacer icônes et textes |
| Slider / Hero | Désactiver le slider Milibido | Remplacer par hero statique |

---

## Résultat attendu

Un thème PrestaShop fonctionnel qui transforme Milibido en une boutique noir-or-ivoire élégante, avec une navigation à deux niveaux (Vitrine / Cabinet), une typographie serif/sans-serif cohérente, et une ambiance « cabinet de curiosités » — loin du sexshop générique d'origine.
