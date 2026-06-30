# Plaisirs de Femmes — Contexte Projet

> Ce fichier est lu automatiquement par Codex à chaque session.
> Dernière mise à jour : 2026-06-12

---

## Projet

Boutique e-commerce **Plaisirs de Femmes** — lingerie, prêt-à-porter et accessoires femme.
Positionnement : chic, élégant, haute couture accessible.

## Fournisseur

**Matterhorn** (grossiste) — flux XML (~85 Mo), produits en français.
Structure XML : `<type>`, `<brand>`, `<name>` (format `Type model ID Brand`), `<color>`, `<description>`, `<category_path>`, `<option>` (tailles/stock/EAN).

## Script principal

**`1-Projets/Plaisirs-de-femmes/02-Dev/02-Scripts/top10_xml.py`**

- Lit le XML Matterhorn directement via `ET.iterparse`
- Sélectionne les **top N** (défaut 10) bestsellers par catégorie
- Score : `tailles_en_stock + bonus_recent(5) + bonus_4_images(3) + bonus_desc(2)`
- Coefficient prix : **×2.2** (grossiste → boutique)
- Génère un CSV d'import PrestaShop
- Contient : `CATEGORY_MAP` (77 mappings vers arbo chic), `TRADUCTION_TYPES` (~70 entrées), `nom_commercial()`, `balise_titre_seo()`, `meta_description_seo()`, `SEO_KEYWORDS`
- Référence produit : `PDF-{id}`

### Autres scripts (ne pas confondre)

- `generer_catalogue.py` — ancien script CSV, **NE PAS UTILISER** (remplacé par top10_xml.py)
- `matterhorn_to_prestashop.py` — contient le CATEGORY_MAP original (référence)

## Arborescence catégories (univers chic)

```
Corps & Désirs          → lingerie (soutiens-gorge, strings, culottes, bodies, corsets…)
L'Impudence             → lingerie sexy, ensembles, accessoires érotiques
Fils de Soie            → bas, collants, porte-jarretelles
L'Heure Bleue           → nuisettes, déshabillés, peignoirs, pyjamas
Architecture Intime     → gaines, bustiers, sculptants
Toutes les Grâces       → maillots de bain
La Garde-Robe           → robes, jupes, hauts, pantalons, vestes
Chaussures              → escarpins, bottines, ballerines, sandales
```

## Nommage produit

Pipeline automatique (pas d'IA) :
1. Extraire le type depuis `<type>` du XML
2. Traduire via `TRADUCTION_TYPES` → nom chic français
3. Enrichir avec matière/couleur/style extraits de la description
4. Résultat : « Soutien-Gorge Push-Up en Dentelle Noir »

## SEO

**Approche hybride** : noms chic pour le client, mots-clés recherchés dans les balises title/meta.

- Title SEO : `Soutien Gorge Push Up Femme Dentelle Noir | Plaisirs de Femmes` (max 65 car.)
- Meta desc : `Découvrez notre soutien-gorge push-up en dentelle noir. [phrase desc]. Plaisirs de Femmes.` (max 155 car.)
- URL : `soutien-gorge-push-up-en-dentelle-noir-206154`
- Stratégie catégories : `03-SEO/Categories/Strategie-SEO-Categories.md`
- SEO technique : `03-SEO/SEO-Technique-PrestaShop.md`

## Descriptions produit

Pas encore faites. Seront générées par Omar avec **Gemma** (LLM local via Ollama).
Les descriptions n'affectent PAS le SEO title/meta/URL (générés depuis le type traduit).

## Journal de projet

**`1-Projets/Plaisirs-de-femmes/01-Plan/Journal-de-projet.md`**
→ Historique complet des sessions, décisions, incidents. **Consulter en début de session.**

## Conventions

- Ton de la boutique : chic, élégant, littéraire (style narratif classique britannique, ironie subtile)
- Omar est le fondateur, expert e-commerce PrestaShop (10+ ans)
- Langue de travail : français
- Réponses : concises, directes, pas de bavardage inutile
- Toujours vérifier dans Obsidian avant de supposer quoi que ce soit

## Fichiers clés dans le vault

```
01-Plan/Journal-de-projet.md          → journal de bord
02-Dev/02-Scripts/top10_xml.py        → script principal (LE SEUL À MODIFIER)
03-SEO/Categories/Strategie-SEO-Categories.md  → SEO catégories
03-SEO/SEO-Technique-PrestaShop.md    → checklist technique SEO
06-IA/Conversations/                  → logs des sessions précédentes
```
