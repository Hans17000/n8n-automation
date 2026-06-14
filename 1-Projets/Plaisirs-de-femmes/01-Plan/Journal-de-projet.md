---
date: 2026-06-10
tags: [journal, projet, decisions]
type: journal
status: active
---

# 📓 Journal de projet

## 2026-06-10

### Incident cron — réimport automatique Matterhorn
Catalogue remis à zéro la veille, mais 3 592 produits réapparus le matin. Cause : cron `0 */2 * * *` sur `matterhorn_connector.php --apply` toujours actif. **Action : commenter la ligne dans `crontab -e` avant toute suppression. ✅ Fait.**

### Décision architecture — pivot vers CSV source principale
L'API Matterhorn donnait des descriptions en anglais et pas de stock par taille individuelle. Le CSV fournisseur est supérieur sur tous les points utiles à l'import initial :

| Donnée | API | CSV |
|--------|-----|-----|
| Description | Anglais | **Français ✅** |
| Stock par taille | ❌ (total seulement) | **`sizes_stock` ✅** |
| EAN par taille | ❌ | **`ean_codes` ✅** |
| SKU Matterhorn par taille | ❌ | **`sizes_sku_codes` ✅** |
| Produits du set | ❌ | **`products_in_set` ✅** |
| Autres coloris | partiel | **`other_colors` ✅** |

L'API reste utile pour les **syncs de stock ponctuelles** (`mh_fetch_catalog.php --brand=X`).

### Architecture pipeline retenue

```
CSV Matterhorn (gros fichier)
    ↓
csv_to_prestashop.py       ← source principale
    ↓
import_ps.csv              ← Simple CSV Import (séparateur ;, UTF-8 BOM)
    ↓
PrestaShop 8.2.6
    ↓ (descriptions vides)
pipeline Ollama             ← enrichissement descriptions FR (à venir)
```

### Scripts livrés aujourd'hui

| Script | Rôle | Statut |
|--------|------|--------|
| `mh_fetch_catalog.php` | Export brut API → CSV (stock temps réel) | ✅ |
| `mh_prepare_import.php` | CSV brut API → Simple CSV Import | ✅ archivé (remplacé) |
| `csv_to_prestashop.py` | **CSV fournisseur → Simple CSV Import** | ✅ actif |

### Analyse `matterhorn_connector.php` (archivé)
Script conservé comme référence : idempotence, logique de prix/marge réutilisable, cartographie marques. Peut servir pour sync stock ponctuelle (`--brand=X --apply`). **Ne plus faire tourner en cron.**

### Mapping Simple CSV Import — profil configuré dans PS
Format : UTF-8 BOM, séparateur `;`, 1 ligne produit + N lignes déclinaisons (Reference comme clé de liaison).
Sections actives : Informations, Prix, Associations, Déclinaisons, Images, Fournisseurs.

### Arbo catégories PS — reconstituée

| ID | Univers | Sous-catégories (IDs) |
|----|---------|-----------------------|
| 3  | Corps & Désirs | 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| 13 | L'Heure Bleue | 14, 15, 16, 17, 18 |
| 19 | Architecture Intime | 20, 21, 22, 23 |
| 24 | La Garde-Robe | 25–50 |
| 51 | Fils de Soie | 52, 53 |
| 54 | L'Impudence | 55 |
| 56 | Toutes les Grâces | 57–70 |
| 71 | **Chaussures** (nouveau) | 72 Bottes & Boots, 73 Cuissardes, 74 Sandales & Mules, 75 Sneakers, 76 Mocassins & Lords, 77 Ballerines, 78 Chaussons, 79 Escarpins, 80 Talons Aiguilles, 81 Talons Bloc |

✅ Catégories orphelines 71–106 supprimées. IDs 71–81 réattribués à l'univers Chaussures (SQL `create_chaussures.sql`).

### Session 2026-06-11 soir — Bilan et prochaine session

**Fait ce soir** :
- CATEGORY_MAP finalisé (65 entrées + 12 variantes encodage = 77 mappings)
- Normalisation sans accents ajoutée dans `map_category()` (fallback automatique)
- Script `top10_xml.py` exécuté sur le fichier complet : 669 produits sélectionnés, CSV généré
- SQL `create_chaussures.sql` livré avec descriptions SEO et meta pour les 11 catégories
- Univers Chaussures créé en BDD (IDs 71–81)

**Demain matin — session suivante** :
1. Import du CSV top 10 (669 produits) via Simple Import
2. Beautification des noms produits (Gemma local ou script)
3. Réécriture descriptions SEO produits
4. Configuration des modules anglais pertinents conservés (IQITADDITIONALTABS, IQITSIZECHARTS, IQITEXTENDEDPRODUCT, etc.)
5. Vérification visuelle en boutique post-import

### Champs API Matterhorn (référence)
`id, active, name, name_without_number, description, creation_date, color, category_name, category_id, category_path, brand_id, brand, stock_total, url, images, new_collection, variants, size_table, weight, other_colors, prices, size_table_txt, size_table_html`

### Import v1 — échec format déclinaisons (2026-06-10)
Simple CSV Import a créé un produit distinct par ligne au lieu de regrouper les déclinaisons. Cause : les colonnes produit (nom, prix, catégorie, images) étaient vides sur les lignes de tailles → module les interprète comme nouveaux produits à 0€.

**Correction à faire dans `csv_to_prestashop.py`** : répéter toutes les colonnes produit sur chaque ligne de déclinaison. Attente du détail exact du profil (section Déclinaisons) pour valider le bon format.

Produits importés supprimés. Import annulé à ~50%.

### Résultats premier run complet — lingerie (2026-06-10)
```
Lignes lues          : 7 783
Produits exportés    : 322
Lignes déclinaisons  : 2 452
Total lignes CSV     : 2 775 (header inclus)
Ignorés (marque)     : 7 461  ← normal, whitelist ~35 marques
Ignorés (stock=0)    : 0
Ignorés (hors cat)   : 0      ← mapping path FR 100% efficace
Moyenne déclinaisons : ~7,6 tailles/produit
```
**Décision : import en l'état, descriptions Ollama après.** Voir les produits en boutique d'abord, affiner les détails, puis lancer le pipeline de génération.

### Champs CSV fournisseur (référence)
`id, name, short_name, date_add, color, description, category, path, brand, wholesale_price, currency, size_table_and_fabric_content, sizes_stock, image_1-4, manufacturer_id, ean_codes, products_in_set, other_colors, sizes_sku_codes`

### Mapping CATEGORY_MAP finalisé (2026-06-11)

65 entrées couvrant les 72 catégories Matterhorn FEMME. Chaque catégorie feuille du `category_path` XML est mappée vers l'arborescence poétique PrestaShop avec le séparateur `->` pour Simple Import.

| Univers PS | Catégories Matterhorn mappées |
|---|---|
| Corps & Désirs | SG Push Up → Galbe, SG Balconnet → Décolleté, SG Soft → Douceur, Corsets/Bodys → Bodys de Soie, Culottes → Dessous Précieux, Strings → Dentelles Effilées, Shortys → Shortys de Charme, Bretelles → Corps & Velours |
| Fils de Soie | Collants/Bas → Bas & Collants de Soie, Gants → Gants d'Élégance |
| L'Heure Bleue | Nuisettes → Nuits de Dentelle, Pyjamas → Nuits Sereines, Peignoirs → Matins de Soie |
| Architecture Intime | Culottes amincissantes → Affinements Secrets, Corsets gainants → Silhouettes Architecturées |
| L'Impudence | Ensembles Sexy + Bodys/Caracos + Guêpières → Objets du Désir |
| La Garde-Robe | Maillots 1P/2P/Plage, Bonnets → Coiffures d'Été, Foulards → Soieries & Foulards, Robes (Jour/Soir/Cocktail), Combinaisons, Jupes, Blouses, Chemises, Tops, Leggings, Pantalons (3 variantes), Shorts, Blazers, Vestes, Sweats, Pulls, Cardigans, Ensembles GT → Mises en Scène |
| Toutes les Grâces | SG Maternité, Robes/Pantalons/Blouses/Leggings/Tuniques grossesse, Robes GT → Robes de Grâce, Chemises GT, Pulls GT → Tricots GT, T-shirts GT → Hauts Essentiels GT, Sweats GT → Molletons GT |
| **Chaussures** (à créer) | Bottes & Boots, Cuissardes, Sandales & Mules, Sneakers, Mocassins & Lords, Ballerines, Chaussons, Escarpins, Talons Aiguilles, Talons Bloc |

**Scripts mis à jour** : `top10_xml.py` et `matterhorn_to_prestashop.py` — mapping identique, vérifié 0 fallback sur les catégories test.

## 2026-06-12

### Port des améliorations nom + SEO dans `top10_xml.py` ✅

Toutes les fonctions développées dans `generer_catalogue.py` ont été portées dans le vrai script de production :

- `TRADUCTION_TYPES` (~70 entrées) : types Matterhorn → noms chic français
- `nom_commercial()` : utilise `<type>` du XML directement, enrichit avec matière/couleur/style
- `balise_titre_seo()` : title hybride mot-clé + attributs + nom boutique (max 65 car.)
- `meta_description_seo()` : meta conversion (max 155 car.)
- URL SEO basée sur nom commercial + ID produit
- `SEO_KEYWORDS` : mapping type traduit → termes réellement recherchés
- Colonnes `Meta title[fr-FR]` et `Meta description[fr-FR]` ajoutées au CSV

### Accord genre adjectifs/couleurs ✅

Ajout de `TYPES_MASCULINS`, `ACCORD_FEMININ`, `_accorder()`. Les adjectifs et couleurs s'accordent au genre du type produit :
- Veste (fém.) → « Veste Élégante en Satin Noire »
- Soutien-Gorge (masc.) → « Soutien-Gorge Push-Up en Dentelle Noir »

**Décision** : pas d'accord de proximité (« Dentelle Noire ») — on garde l'accord avec le nom principal. Les deux sont corrects, on reste simple.

### Script exécuté et validé par Omar ✅

Le script tourne en ~2 secondes sur le XML complet. Noms, SEO et accords validés.

### Mémoire persistante — `CLAUDE.md` créé ✅

Fichier `CLAUDE.md` à la racine du vault avec tout le contexte projet. Lu automatiquement à chaque nouvelle session.

### Prompt Gemma 4 pour descriptions produit ✅

Prompt système + template utilisateur livrés dans `06-IA/Prompts/prompt-descriptions-gemma.md`. Calibré pour Gemma 4 E4B via LM Studio. Génère une description courte (2 phrases, 300 car.) + longue (4-6 phrases, 800 car.) par produit, ton littéraire chic sans jargon promotionnel.

### CSV descriptions pour Gemma ajouté au script ✅

`top10_xml.py` génère maintenant un second fichier `*_descriptions.csv` — une ligne par produit avec : référence, nom commercial, type, couleur, marque, composition, description fournisseur. Prêt à copier-coller dans LM Studio.

### Script `generer_descriptions.py` livré ✅

Script Python autonome qui appelle LM Studio (API locale, port 1234) produit par produit. Lit le CSV descriptions, envoie le prompt Gemma, parse [COURTE] et [LONGUE], écrit un CSV de sortie. Fonctionnalités : reprise après crash (`--resume`), retry automatique (3 tentatives), flush immédiat, log des erreurs de parsing.

### Génération descriptions — modèle retenu ✅

Après tests de Gemma 4 E4B (thinking incontrôlable), Qwen 2.5 7B (ton trop promo), Mistral 3B a été retenu : 8s/fiche, ton chic-magazine, ventilo silencieux. Prompt calibré avec deux exemples few-shot, mots interdits, troncature auto à 300/800 caractères. Quelques fautes mineures attendues (modèle 3B) — relecture manuelle prévue après génération.

669/669 descriptions générées ✅. Plusieurs passes nécessaires (parser amélioré en cours de route pour gérer les formats variables de Mistral). Résultat final : fichier `*_avec_descriptions.csv` complet.

### Import PrestaShop — catégories + descriptions ✅

- Premier import : catégories créées en doublon (toggle « Lier aux existantes » était sur Non). Corrigé, réimport OK.
- Descriptions Mistral intégrées sans erreur.
- 16 erreurs EAN13 non bloquantes (checksums invalides côté Matterhorn).

### Correction accord genre/nombre — refonte complète ✅

L'approche par nom exact (`TYPES_MASCULINS`) ne marchait pas — trop de types avec modifieurs (« Blazer femme », « Bottes de sport »). Remplacé par détection via le **premier mot** du type (`MOTS_MASCULINS`, `MOTS_PLURIELS`, `_detecter_genre_nombre()`). Gère maintenant tous les cas : masculin/féminin × singulier/pluriel.

### Regroupement variantes couleur — refonte majeure ✅

Les produits existant en plusieurs couleurs (ex: Culotte Beige / Noire / Blanche) étaient importés comme des produits séparés. Refonte complète du pipeline pour les regrouper en UN seul produit avec déclinaisons Couleur × Taille.

**Changements dans `top10_xml.py` :**
- Phase 1 : parsing du champ `<other_colors>` du XML pour identifier les variantes
- Phase 1b : Union-Find pour construire les groupes de couleur (clustering automatique)
- Phase 2 : sélection top N **groupes** par catégorie (au lieu de produits individuels). Score du groupe = meilleur membre.
- Phase 3 : CSV avec attributs `Couleur:select:0,Taille:select:1`. Images regroupées de toutes les variantes.
- Phase 4 : CSV descriptions adapté (couleurs listées, nom sans couleur)
- `nom_commercial()` : nouveau paramètre `inclure_couleur=False` pour les produits groupés
- `_traduire_couleur()` : traduction EN→FR des couleurs Matterhorn
- `map_category()` : fallback amélioré — essaie chaque segment du chemin, exclut "FEMME" du dernier recours
- Diagnostic fin de script : liste les catégories non mappées avec leur forme normalisée

### Correction mapping catégories — fallback sans FEMME ✅

Le fallback de `map_category()` recréait `FEMME->Lingerie->...` quand une catégorie ne matchait pas → catégorie « FEMME » (ID 284) créée en doublon dans PS. Corrigé : le fallback exclut « FEMME » et essaie chaque segment du chemin contre CATEGORY_MAP avant de tomber en dernier recours.

### Prochaines étapes

- Supprimer la catégorie « FEMME » (284) et ses sous-catégories dans PS
- Relancer `top10_xml.py` et réimporter le CSV
- Vérifier les catégories non mappées (diagnostic en fin de script)
- Investiguer l'encodage des accents dans les catégories PS (Pi?ce, Gu?pi?res)
- Investiguer les produits importés comme inactifs
- Relecture finale des descriptions (fautes Mistral 3B) — Omar
- Implémentation SEO technique PrestaShop (modules, schema.org, sitemap)
- Vérification visuelle en boutique post-import
