# SEO Technique — Implémentation PrestaShop

> Checklist et recommandations techniques pour l'optimisation SEO de la boutique Plaisirs de Femmes sur PrestaShop.

---

## 1. Données structurées (Schema.org)

### 1.1 Product Schema (priorité haute)

Chaque fiche produit doit générer un bloc JSON-LD `Product` avec :

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Soutien-Gorge Push-Up en Dentelle Noir",
  "image": ["url_image_1", "url_image_2"],
  "description": "...",
  "brand": {
    "@type": "Brand",
    "name": "Axami"
  },
  "sku": "PDF-206154",
  "gtin13": "5905677...",
  "offers": {
    "@type": "Offer",
    "price": "29.90",
    "priceCurrency": "EUR",
    "availability": "https://schema.org/InStock",
    "url": "https://plaisirs-de-femmes.fr/soutien-gorge-push-up-noir-206154"
  }
}
```

**Module recommandé :** « SEO Schema Markup Structured Data Rich Snippet » sur PrestaShop Addons (~60€, compatible PS 1.7–9.x) ou « PrestaShop Schema Pro » de PrestaPremium. Les deux génèrent le JSON-LD automatiquement à partir des données produit.

### 1.2 BreadcrumbList

Le fil d'Ariane doit être balisé en schema.org :

```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Accueil", "item": "https://plaisirs-de-femmes.fr/"},
    {"@type": "ListItem", "position": 2, "name": "Lingerie Sexy", "item": "https://plaisirs-de-femmes.fr/lingerie-sexy-femme"},
    {"@type": "ListItem", "position": 3, "name": "Ensembles", "item": "https://plaisirs-de-femmes.fr/ensemble-lingerie-sexy"}
  ]
}
```

Natif dans la plupart des thèmes PS récents. Vérifier avec Google Rich Results Test.

### 1.3 Organization + LocalBusiness

Sur la page d'accueil et le footer, ajouter les schema Organization et LocalBusiness avec logo, coordonnées, réseaux sociaux.

### 1.4 FAQ Schema

Sur les pages catégories principales, ajouter un bloc FAQ balisé (« Comment choisir sa taille ? », « Quel soutien-gorge pour ma morphologie ? »). Google affiche ces FAQ directement dans les résultats.

---

## 2. URLs & Canonicals

### 2.1 Structure d'URL

```
/lingerie-femme/                          → Catégorie pilier
/lingerie-femme/soutien-gorge-push-up/    → Sous-catégorie
/soutien-gorge-push-up-dentelle-noir-206154  → Fiche produit
```

**Règles :**
- Pas de `/fr/` inutile si le site est monolingue
- Pas d'ID numérique dans l'URL catégorie (désactiver dans PS > SEO & URLs)
- Tirets uniquement, pas d'underscores
- Tout en minuscules

### 2.2 Canonical

- Chaque page doit avoir une balise `<link rel="canonical">` pointant vers elle-même
- Les pages de pagination (`?page=2`) doivent pointer vers la page 1 OU utiliser `rel="next/prev"`
- Les filtres (taille, couleur) ne doivent PAS créer de nouvelles URLs indexables → canonical vers la page non filtrée

**Module :** Vérifier que le thème actif gère les canonicals. Sinon, « SEO Expert » de PrestaShop Addons.

---

## 3. Sitemap XML

### 3.1 Configuration

- Activer le module natif « Sitemap Google » dans PrestaShop
- Générer automatiquement (cron quotidien)
- Soumettre dans Google Search Console

### 3.2 Contenu du sitemap

Inclure :
- Pages catégories (toutes)
- Fiches produit actives uniquement
- Pages CMS (À propos, Guide des tailles, FAQ)

Exclure :
- Pages de recherche interne
- Pages filtrées
- CGV, mentions légales (noindex de toute façon)

### 3.3 Sitemap images

Activer le sitemap images pour que Google indexe les photos produit. Le module natif PS le supporte.

---

## 4. Performance & Core Web Vitals

### 4.1 Images

- **Format :** WebP avec fallback JPEG (module « Image Converter WebP » ~30€)
- **Lazy loading :** Activer le chargement différé sur les images sous la ligne de flottaison
- **Dimensions :** Spécifier `width` et `height` sur chaque `<img>` pour éviter le CLS
- **Alt text :** Généré automatiquement par le script → « Soutien-gorge push-up dentelle noir femme — Plaisirs de Femmes »
- **Taille max :** 200 Ko par image produit, 100 Ko pour les miniatures

### 4.2 Vitesse

- Activer la compression Gzip/Brotli côté serveur
- Activer le cache PrestaShop (Smarty cache + CCC)
- Minifier CSS/JS (module « Page Speed » ou CCC natif)
- CDN pour les images si trafic > 5k visiteurs/jour

### 4.3 Mobile

- Vérifier que le thème est responsive (tester avec Lighthouse)
- Taille des boutons tactiles ≥ 48×48 px
- Texte lisible sans zoom (font-size ≥ 16px)

---

## 5. Indexation & Crawl

### 5.1 Robots.txt

```
User-agent: *
Allow: /
Disallow: /module/
Disallow: /cart
Disallow: /order
Disallow: /login
Disallow: /my-account
Disallow: /*?q=
Disallow: /*?order=
Disallow: /*&order=

Sitemap: https://plaisirs-de-femmes.fr/sitemap.xml
```

### 5.2 Meta robots

- Pages produit actives : `index, follow`
- Pages filtrées / triées : `noindex, follow`
- Pages de pagination > 1 : `noindex, follow` (avec canonical vers page 1)
- Pages panier, compte, commande : `noindex, nofollow`

### 5.3 Hreflang

Non nécessaire pour le moment (site monolingue FR). À implémenter si expansion vers BE, CH, ou version EN.

---

## 6. Maillage interne

### 6.1 Principes

- Chaque fiche produit doit lier vers sa catégorie parente et au moins 2 produits similaires
- Chaque page catégorie doit lier vers ses sous-catégories et vers la catégorie parente
- Le footer doit contenir les liens vers les catégories principales (pas toutes les sous-catégories)
- La page d'accueil doit lier vers les 5–6 catégories principales

### 6.2 Produits similaires

Configurer le module « Produits similaires » ou « Cross-selling » de PrestaShop pour afficher 4–6 produits de la même catégorie sur chaque fiche. Ces liens transmettent du jus SEO et augmentent le temps passé sur le site.

### 6.3 Blog / Pages piliers

Créer des pages de contenu éditorial (guide des tailles, guide d'achat lingerie, comment choisir son soutien-gorge) qui lient vers les catégories produit. Ces pages captent le trafic informationnel et redistribuent l'autorité.

---

## 7. Google Search Console — Actions initiales

1. Vérifier la propriété du domaine (DNS ou balise HTML)
2. Soumettre le sitemap
3. Demander l'indexation des pages clés
4. Vérifier les erreurs d'exploration (404, redirections)
5. Surveiller les Core Web Vitals
6. Configurer les alertes email pour les erreurs critiques

---

## 8. Google Merchant Center (optionnel, phase 2)

Si tu veux apparaître dans Google Shopping :
- Générer un flux produit (module « Google Shopping / Merchant Center » ~80€)
- Le flux doit contenir : titre, description, prix, dispo, GTIN/EAN, images, catégorie Google
- Le titre du flux doit suivre le format SEO mot-clé first : « Soutien-Gorge Push-Up Dentelle Noir Femme — Axami »

---

## Checklist de lancement

- [ ] Module Schema.org installé et configuré
- [ ] Canonical sur toutes les pages
- [ ] Sitemap XML généré et soumis à GSC
- [ ] Robots.txt vérifié
- [ ] Meta robots correctes (noindex sur filtres, panier, compte)
- [ ] Images en WebP avec alt text
- [ ] Textes SEO catégories ajoutés (voir Strategie-SEO-Categories.md)
- [ ] Fil d'Ariane balisé BreadcrumbList
- [ ] URLs propres (pas d'ID, tirets, minuscules)
- [ ] Lighthouse score > 80 sur mobile
- [ ] Google Search Console configurée
- [ ] Produits similaires activés sur les fiches
