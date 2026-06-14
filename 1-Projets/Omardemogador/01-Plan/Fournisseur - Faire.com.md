---
date: 2026-06-10
tags: [fournisseur, sourcing, marketplace-b2b, analyse]
type: fournisseur
statut: "🟠 Veille active — achats différés (phase 2)"
priorité: moyenne
parent: "[[MOC - Sourcing]]"
---

# 🏷️ Faire.com — Analyse de pertinence

> **Site :** [faire.com/fr](https://www.faire.com/fr/)
> **Nature :** marketplace B2B de gros — met en relation détaillants et marques indépendantes (~100 000 marques, forte dominante artisanale et premium)
> **Modèle :** achat de stock en gros, expédié chez vous. **Ce n'est pas du dropshipping.**

---

## ⚖️ Verdict en une phrase

Faire n'a pas sa place dans le 1er cercle — la ligne rouge n°4 du [[Journal de décisions - Omar de Mogador|journal]] l'interdit — mais constitue un remarquable **cercle intermédiaire** : le paiement à 60 jours transforme l'achat de stock en quasi-dropshipping de trésorerie, et le catalogue regorge précisément des marques artisanales premium que les généralistes du 1er cercle ne savent pas offrir.

---

## Conditions constatées

| Condition | Détail | Verdict pour nous |
|---|---|---|
| Inscription | Justificatif d'activité — le SIRET suffit | ✅ Compatible auto-entrepreneur |
| N° TVA intracom | Facultatif — case « je n'ai pas de numéro de TVA » à l'inscription | ✅ mais voir vigilance ci-dessous |
| Minimum de commande | Fixé par marque, souvent dès 100–150 € | ✅ Accessible |
| Paiement | **Net 60** : payable 60 jours après réception, sans frais | ✅ L'argument décisif |
| Retours | **Gratuits sur la première commande** auprès de chaque marque | ✅ Test sans risque produit |
| Abonnement | Aucun | ✅ Conforme au cahier des charges |
| Revente | Boutique en ligne propre autorisée ; marketplaces tierces (Amazon, eBay) interdites | ✅ omardemogador.fr = cas prévu |

---

## Lecture stratégique — où le ranger dans les trois cercles

Le cœur du sujet tient en peu de mots : Faire vend du stock, et le journal de décisions est formel — *pas d'achat de stock tant qu'on est en dropshipping*. On pourrait s'arrêter là. Ce serait pourtant se priver d'une subtilité comptable qui change la nature du risque : avec le net 60 et le retour gratuit de première commande, une référence achetée 120 € peut être **vendue avant d'être payée**, ou retournée si elle ne part pas. Le stock pèse sur l'étagère, non sur la trésorerie.

D'où la recommandation : ne pas amender la ligne rouge, mais lui ménager **une exception encadrée**.

> [!success] Usage recommandé — « cercle 1,5 »
> 1. **Éclaireur de marques** : Faire est le meilleur annuaire vivant de marques artisanales premium (bougies, encens, soins naturels, coffrets) — exactement la profondeur qui manque à BigBuy ou BTSWholesaler. Repérer, qualifier, puis selon le cas commander via Faire ou négocier en direct (2e cercle).
> 2. **Micro-stock de test** : uniquement sur des références déjà validées par le dropshipping, ou pour les coffrets cadeaux (intenables en dropshipping multi-fournisseurs). Plafond suggéré : 300–500 € d'encours net 60, jamais plus que ce que la caisse pourrait absorber si rien ne se vendait.
> 3. **Pas de colonne vertébrale** : Balqis France et le 2e cercle restent la charpente du catalogue. Faire complète, il ne fonde pas.

### Adéquation au positionnement

| Critère Omar de Mogador | Faire |
|---|---|
| Premium, pas de bazar | ✅ ADN artisanal/indépendant de la plateforme |
| Univers oriental (argan, hammam, oud) | 🟡 Présent mais à inventorier — la profondeur réelle ne se voit qu'après inscription (prix et catalogue sous login) |
| Packaging soigné, storytelling | ✅ Les marques Faire vivent de leur image — assets souvent excellents |
| Dropshipping pur | ❌ Inexistant sur Faire |
| Marge | 🟡 Coefficient de gros classique ×2 à ×2,5 — comparable au 2e cercle, mais TVA non récupérable (cf. vigilance) |

---

## ⚠️ Points de vigilance

> [!warning] À garder en tête avant la première commande
> - **TVA non récupérable** : sans numéro intracom, la TVA facturée sur les achats (FR ou UE) reste à notre charge — la marge réelle s'en trouve rognée d'environ 20 % sur le prix d'achat. C'est le même plafond de verre que partout : il saute au passage en société.
> - **Seuil des 10 000 €** : au-delà de 10 000 € d'acquisitions intracommunautaires par an, le numéro de TVA intracom devient obligatoire même en franchise en base. Loin d'être atteint au démarrage, mais à surveiller.
> - **Conformité cosmétique** : privilégier les marques européennes (étiquetage FR, responsable UE, CPNP en règle). Une marque américaine séduisante sur la photo peut être invendable légalement en France.
> - **Frais de port** : variables par marque, parfois dissuasifs depuis l'étranger — à intégrer au calcul de marge avant toute commande.
> - **Stockage et expédition** : qui dit stock dit colisage maison — prévoir le consommable d'emballage premium cohérent avec la charte.

---

## 📦 Import des produits vers PrestaShop

Pas de module PrestaShop côté détaillant (l'intégration officielle n'existe que pour Shopify et quelques POS), pas d'API acheteur. Mais Faire fournit un **export officiel complet**, prévu précisément pour créer ses fiches produit ailleurs :

> **Commandes → Download orders →** `Product info (.csv)` + `Photos (.zip)`
> Le CSV contient : nom, **description**, **URL des images**, variante, SKU, **GTIN/EAN**, prix de gros, **prix de vente conseillé**, poids, marque.

Limite à connaître : l'export ne porte que sur les produits **commandés**. On ne siphonne pas le catalogue en amont — ce qui, pour un micro-stock choisi, n'est pas un drame.

### Chaîne d'import (semi-automatisée)

1. Commander sur Faire (net 60).
2. Exporter le `Product info (.csv)` de la commande.
3. Convertir au format d'import natif PrestaShop : script [[faire_vers_prestashop.py]] déposé dans `Sourcing/` — il mappe SKU→Référence, GTIN→EAN13, description, prix, poids, images, et sort un CSV séparé par `;` prêt pour **Paramètres avancés → Import**.
4. Réécrire les descriptions dans la [[Prompt - Voix de Mogador (descriptions)|Voix de Mogador]] — l'export livre la prose du fabricant, jamais la nôtre.
5. Vérifier images (poids, fond), catégories et étiquetage avant mise en ligne.

> [!tip] Voie zéro effort
> Déposer le CSV exporté dans le vault et me le confier : je rends le fichier d'import PrestaShop fini, descriptions réécrites comprises.

---

## Prochaines actions

> [!note] Décision du 2026-06-10
> Achats différés jusqu'à la vitesse de croisière — déclencheur : 15–20 commandes/mois sur deux mois consécutifs et 3–5 références validées. Veille activée dès maintenant. Cf. [[Journal de décisions - Omar de Mogador]].

**Maintenant (veille, coût nul)**
- [ ] Créer le compte détaillant Faire (SIRET, case « pas de n° TVA »)
- [ ] Inventorier l'offre réelle : argan, savon noir, oud, bougies, coffrets — shortlist de 5 marques cohérentes
- [ ] Comparer prix de gros Faire vs Balqis/2e cercle sur 3 références communes

**Phase 2 (au déclenchement)**
- [ ] Première commande micro-stock net 60 — plafond 300–500 €, références validées et coffrets uniquement
- [ ] Export `Product info (.csv)` → [[faire_vers_prestashop.py]] → import PrestaShop

---

## Liens internes
- [[Stratégie sourcing]] · [[MOC - Sourcing]]
- [[Fournisseurs - 1er cercle]] · [[Fournisseurs - 2e cercle]]
- [[Fournisseur - Les Sens de Marrakech]]
