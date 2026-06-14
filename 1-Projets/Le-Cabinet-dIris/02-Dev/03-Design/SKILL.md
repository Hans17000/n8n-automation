---
name: cabinet-iris-design
description: Use this skill to generate well-branded interfaces and assets for Le Cabinet d'Iris (boutique e-commerce lifestyle sensuel — univers « cabinet de curiosités élégant », noir d'encre / or antique / ivoire), either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the README.md file within this skill, and explore the other available files.
If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.
If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

Key facts:
- All copy is in French, in the voice of Iris (curatrice fictive) — vouvoiement, suggestive, never explicit, never promotional. See readme.md CONTENT FUNDAMENTALS.
- Tokens live in `tokens/*.css`, entry point `styles.css`. Fonts: Cormorant Garamond (display), Lato (body), Pinyon Script (Iris quotes only) — all Google Fonts.
- Hard rules: no pink, no hearts, no emoji, no gradients, no shiny gold, no rounded corners (max 2px), 0.3s ease transitions only, gold is an accent metal never a large fill, le vide fait partie du design.
- Components: `components/core/` (Button, Badge, PriceTag, SectionTitle, EditorialText, Separator, IrisQuote, ReassuranceItem) and `components/commerce/` (ProductCard, CategoryTile).
- Full storefront recreation: `ui_kits/boutique/index.html` (homepage, sas « Poussez la porte », Le Cabinet, catégories, fiche produit).
