# Le Cabinet d'Iris — Design System

**Boutique e-commerce lifestyle sensuel** sur PrestaShop 8.x. Le site transforme le thème Milibido (BonTheme, thème sexshop/lingerie générique) en un univers « **cabinet de curiosités élégant** » : noir d'encre, or antique, ivoire — loin du sexshop générique.

## Le concept : deux niveaux de navigation

1. **La Vitrine** — l'étage public : lingerie fine, cosmétiques, nuisettes.
   Catégories : *Les Étoffes · Les Nuits · Les Voiles · Les Élixirs · Les Écrins*
2. **Le Cabinet** — l'arrière-boutique : sextoys, fétiche, BDSM élégant, accessible via le bouton « **Poussez la porte** » et une page sas (confirmation 18+).
   Catégories : *Les Apparitions · Les Objets · Les Confessions · Les Complicités · Le Boudoir Noir · Les Caprices*

**Iris** est la curatrice fictive de la boutique : tout le contenu est écrit dans sa voix (« Sélection d'Iris », « Les Carnets d'Iris », « Iris a rassemblé ici ce qu'elle ne montre qu'à ceux qui poussent la porte. »).

**Positionnement** : entre le sexshop discount et le wellness clinical — « l'élégance de l'interdit ». Mood : cabinets de curiosités XVIIIᵉ, bijouterie de luxe, roman noir, boudoir parisien. Marques de référence : Cire Trudon, Maison Close, Byredo.

## Sources

- `02-Dev/BRIEF - Claude Code (Customisation Milibido).md` (aussi `uploads/`) — brief de customisation complet (palette, typographie, CSS composants, arborescence catégories, mécanisme du sas). **Source de vérité technique.**
- Brief identité de marque (collé en conversation) — logo, iconographie, gabarits réseaux sociaux, références mood, interdits. **Source de vérité brand.**
- `02-Dev/01-Specs/`, `02-Dev/05-PrestaShop/` — templates de specs (vides).
- ⚠️ Le code source du thème Milibido lui-même **n'était pas fourni** ; ce design system est construit à partir du brief, pas du thème compilé.
- Photo hero « clair-obscur » mentionnée dans le brief : **à fournir** (placeholder utilisé).
- Monogramme Iris (SVG) mentionné dans le brief : **à fournir** (monogramme typographique utilisé en attendant).

---

## CONTENT FUNDAMENTALS

**Langue** : français exclusivement. **Vouvoiement** systématique (« vous confirmez avoir plus de 18 ans »).

**Voix** : celle d'Iris, curatrice — troisième personne quand on parle d'elle (« Iris a rassemblé ici… »), adresse directe et feutrée au visiteur. Jamais de « nous » commercial.

**Ton** : suggestif, jamais explicite. Littéraire, métaphorique, légèrement mystérieux. Le vocabulaire vient du cabinet de curiosités et du boudoir XIXᵉ, pas du e-commerce.

**Lexique de marque** (à respecter strictement) :
- Catégories = noms poétiques avec article : « Les Étoffes », « Le Boudoir Noir » — jamais « Lingerie », « BDSM ».
- « Poussez la porte » = l'entrée du Cabinet (jamais « 18+ », « adultes »).
- Stock bas = badge « **Pièce rare** » (jamais « Plus que 2 en stock ! »).
- Blog = « **Les Carnets d'Iris** ». Produits mis en avant = « **Sélection d'Iris** ».
- Réassurance : « Livraison discrète », « Paiement sécurisé », « Curation Iris », « Retours sous 14j ».

**Casing** : titres en capitalisation normale française (majuscule initiale seulement) ; la navigation et les boutons sont mis en capitales par CSS (`text-transform: uppercase`), jamais tapés en capitales.

**Emoji** : jamais. Aucune exclamation racoleuse, pas de prix barrés criards, pas d'urgence artificielle.

**Exemples canoniques** :
- Hero : « Le Cabinet d'Iris — Collection privée de curiosités sensuelles »
- Sas : « Iris a rassemblé ici ce qu'elle ne montre qu'à ceux qui poussent la porte. »
- Notice légale, discrète : « En entrant, vous confirmez avoir plus de 18 ans. »
- CTA : « Entrer dans la Vitrine », « Entrer », « Retourner à la Vitrine », « Ajouter au panier »

---

## VISUAL FOUNDATIONS

**Palette** — 5 couleurs, c'est tout :
- Noir d'encre `#1A1A2E` (fonds header/footer/sas, texte) · Or antique `#C9A96E` (accents, bordures, prix, CTA) · Ivoire `#F5F0E8` (fond de page) · Prune `#4A2040` (badge/univers Cabinet) · Bordeaux `#6B2D3E` (badge « Pièce rare », alertes).
- Le doré n'est **jamais** un fond de grande surface : c'est un métal d'accent (bordures, texte, boutons).
- Pas de blanc pur, pas de gris neutres froids : l'ivoire et ses variantes (`--color-background-dark` #EBE5D9) servent de neutres chauds.

**Typographie** — duo strict serif/sans :
- **Cormorant Garamond** (Google Fonts) : tous les titres, la navigation, les libellés de boutons. Poids 600 pour les titres courants, 400 pour le hero/sas/nav. Italique = registre « Cabinet » (bouton « Poussez la porte », textes éditoriaux).
- **Lato** (Google Fonts) : corps 15px/1.7, prix en **300 light** doré avec `letter-spacing: 0.05em`, badges 11px uppercase.
- Letter-spacing généreux partout : nav 0.15em, boutons 0.1em, sous-titres 0.2em — c'est un marqueur fort de la marque.
- **Pinyon Script** (Google Fonts) : uniquement les citations d'Iris, 18–22px. Jamais pour l'UI.

**Formes** : rectiligne. Radius 0 partout (1px badges, 2px max pour le bouton nav). Pas d'ombres portées — la profondeur vient des **hairlines dorées** (0.5px–1px, or antique à 30% d'opacité, 100% au hover ou pour les cadres forts).

**Cartes & images produit** : fond ivoire, bordure hairline dorée 0.5px, image encadrée avec padding 8px (effet passe-partout de gravure). Hover = la bordure passe à l'or plein (`border-color` 0.3s ease). Pas de zoom, pas de scale.

**Backgrounds** : aplats unis uniquement. Ivoire pour les pages, noir d'encre pour header/footer/hero/sas, prune pour l'univers Cabinet. Le hero porte une photo clair-obscur sombre (à fournir) sous un voile sombre. Pas de dégradés, pas de motifs, pas de textures générées.

**Animation** : uniquement des transitions `0.3s ease` sur color/background/border/opacity. Jamais de rebond, de scale, de slide. L'univers est feutré : tout fond, rien ne saute.

**Hover states** : liens nav → couleur vers l'or ; liens footer → opacité 0.7 → 1 ; boutons or → or sombre `#A88B52` ; boutons outline → fond or + texte noir d'encre ; cartes → bordure dorée pleine.

**Layout** : textes éditoriaux centrés, max 700px, en Lato italique entre deux filets dorés horizontaux. Sections généreusement aérées (40–80px). Séparateur vertical doré 1×20px dans la nav avant « Poussez la porte ».

**Imagerie** : photo clair-obscur, chaude, sombre, suggestive — jamais clinique ni criarde. Cadrages serrés, matières (dentelle, velours, métal). Texture de fond optionnelle (marbre noir / grain papier ancien / trame soie) à 5–8% d'opacité max.

**Logo** : monogramme « I » inscrit dans un cadre ovale (cachet de cire / camée), style gravure fine. Or sur noir d'encre, noir sur ivoire, + monochromes. Doré toujours **mat**. Lisible à 32px. *SVG officiel à fournir — monogramme typographique provisoire dans ce système.*

**Interdits absolus** : rose bonbon, cœurs, emoji ; polices fantaisie ; design « sexshop néon » (rouge vif, noir brillant, typo impact) ; dorure brillante/métallique ; gradients et effets de lumière artificiels ; surcharge visuelle — **le vide fait partie du design**.

---

## ICONOGRAPHY

- **Aucun fichier d'icône fourni**. Le brief brand définit le style : **trait fin 1–1.5px**, angles arrondis doux, grille 24×24, or antique sur fond sombre / noir d'encre sur fond clair. Icônes de marque à créer : clé ancienne (motif récurrent — « la clé du Cabinet »), cadenas ouvert, plume (Carnets d'Iris), écrin, flacon, boîte neutre, paiement sécurisé, retours.
- **Substitution flaguée** : [Lucide](https://lucide.dev) via CDN (`lucide-static`), trait 1.5px, couleur `--color-accent` — le style trait fin correspond à l'esprit gravure. Icônes utilisées : `package`, `lock-keyhole`, `key-round`, `undo-2`, plus panier/recherche/compte (`shopping-bag`, `search`, `user`). À remplacer si la marque fournit ses propres icônes gravées.
- **Monogramme** : en attendant le SVG officiel, monogramme typographique — « I » Cormorant Garamond entre deux filets, doré (voir `assets/monogram.html` rendu dans les cartes Brand).
- Jamais d'emoji, jamais d'icônes pleines/filled, jamais d'icônes colorées multicolores.

---

## INDEX

| Chemin | Contenu |
|---|---|
| `styles.css` | Point d'entrée CSS (importe tous les tokens) |
| `tokens/colors.css` · `tokens/typography.css` · `tokens/spacing.css` | Variables CSS : palette, type, espacements/bordures/motion |
| `guidelines/` | Cartes specimen (couleurs, type, espacements, brand) |
| `components/core/` | Button, Badge, PriceTag, SectionTitle, EditorialText, ReassuranceItem |
| `components/commerce/` | ProductCard, CategoryTile |
| `ui_kits/boutique/` | Recréation du site : homepage, sas du Cabinet, page catégorie, fiche produit (cliquable) |
| `SKILL.md` | Compatibilité Claude Code Agent Skills |

**Composants** : `Button` (primary/secondary/cabinet-entry/ghost), `Badge` (rare/cabinet), `PriceTag`, `SectionTitle`, `EditorialText`, `Separator`, `IrisQuote`, `ReassuranceItem`, `ProductCard`, `CategoryTile`.

**UI kit** : `ui_kits/boutique/index.html` — boutique cliquable complète : accueil (hero, Sélection d'Iris, deux univers, citation, Carnets), sas « Poussez la porte » (confirmation 18+), Le Cabinet (6 catégories prune), pages catégorie avec éditorial d'Iris, fiche produit (cadre passe-partout, badges, réassurance).
