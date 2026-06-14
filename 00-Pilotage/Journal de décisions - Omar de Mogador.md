---
tags:
  - décision
  - journal
  - stratégie
type: journal-décisions
parent: "[[MOC - Omar de Mogador]]"
---

# Journal de décisions

> [!info] Journal stratégique
> Trace chronologique des décisions structurantes du projet Omar de Mogador. Chaque décision indique : ce qui a été tranché, pourquoi, et ce qui a été écarté.

---

## 2026-06-08 — Pivot de nom de marque

**Décision** : Abandon de *Ethnika Oud* au profit d'*Omar de Mogador*

**Raisons**
- *Ethnika Oud* lisait comme un comptoir spécialisé
- *Omar de Mogador* installe un personnage, une adresse, un récit
- Cohérence supérieure avec l'ambition cosmopolite

**Domaines acquis** : omardemogador.fr · .com · .org

**Lien** : [[Naming et positionnement]]

---

## 2026-06-08 — Adoption de la fleur de jasmin comme emblème

**Décision** : Fleur de jasmin stylisée à cinq pétales

**Pistes écartées**
- Étoile à huit branches (trop religieuse)
- Arc (associations funéraires)
- Rose des vents (territoire automobile)
- Paris–Casablanca duo de villes (trop attendu)

**Lien** : [[Charte graphique]]

---

## 2026-06-08 — Constitution de l'équipe avatars

**Décision** : 5 avatars représentant les deux rives méditerranéennes

| Avatar | Origine | Rôle |
|---|---|---|
| [[Yasmine]] | Essaouira | Chef de projet |
| [[Nour]] | Beyrouth | Rédactrice |
| [[Sofia]] | Séville | Community manager |
| [[Marco]] | Venise | Publicité |
| [[Leïla]] | Paris/Fès | SEO |

**Raison** : la composition même de l'équipe doit refléter la philosophie *Orient · Occident*.

**Lien** : [[MOC - Équipe avatars]]

---

## 2026-06-09 — Stratégie sourcing en trois cercles

**Décision** : architecture en trois cercles d'accessibilité

1. **1er cercle** (immédiat) — Balqis France, BTSWholesaler, Nova Engel, BigBuy
2. **2e cercle** (sous 10 jours) — L'Univers Oriental, Grossiste Orient, Alepia, Naturare
3. **3e cercle** (phase 2, 3–6 mois) — Oriental Group, Argamine, producteurs directs Maroc/Golfe

**Hero product candidat** : roll-on huiles parfumées sans alcool

**Liens** : [[Stratégie sourcing]] · [[Produits qui cartonnent 2026]]

---

## 2026-06-10 — Faire.com reporté en phase 2, veille activée

**Décision** : Faire.com est qualifié comme « cercle 1,5 » mais ses **achats sont différés** jusqu'à la vitesse de croisière de la boutique. La fonction d'éclaireur démarre dès maintenant.

**Déclencheur d'activation des achats** (mesurable) :
- 15–20 commandes/mois sur **deux mois consécutifs**, et
- 3 à 5 références validées par la demande réelle en dropshipping

**Dès maintenant (coût nul)** :
- Ouverture du compte détaillant (SIRET, case « pas de n° TVA »)
- Veille catalogue : comparaison des marges face à Balqis, repérage de marques pour le 2e cercle

**Cadre des achats en phase 2** : micro-stock net 60 plafonné à 300–500 € d'encours, réservé aux références validées et aux coffrets. La ligne rouge n°4 reste en vigueur — ceci est son unique exception, encadrée.

**Raison** : le net 60 et le retour gratuit de première commande déplacent le risque du stock vers l'étagère plutôt que la trésorerie, mais tester à l'aveugle ce que le dropshipping teste gratuitement n'aurait aucun sens. Observer n'est pas stocker.

**Lien** : [[Fournisseur - Faire.com]]

---

## 2026-06-11 — Nouveau flux XML Matterhorn v2 et refonte de la chaîne d'import

**Décision** : Adoption du nouveau format XML v2 fourni par Matterhorn comme source unique d'import catalogue. Suppression de l'ancienne chaîne multi-étapes.

**Contexte** : Matterhorn a proposé un échantillon XML enrichi. Après analyse, le format s'avère complet à 100% (nom, marque, catégorie avec chemin, prix wholesale, description + composition, images URLs, tailles/stock/EAN). L'ancien flux nécessitait 4 scripts chaînés et des fichiers de mapping manuels pour compenser les données manquantes.

**Ce qui change** :
- Un seul script [[matterhorn_to_prestashop.py]] remplace `extract_xml.py` → `netoyage.py` → `to_prestashop.py`
- Le mapping catégories est intégré au script (dictionnaire `CATEGORY_MAP`)
- Plus besoin de fichiers intermédiaires par univers (_net, _enrichi)
- Les anciens CSV et fichiers de mapping ont été supprimés du vault

**Fichiers reçus** : `products_sizesFR.xml` (85 Mo, toutes catégories) + `products_sizesFR4.xml` (1 Mo, Sacs & Accessoires, test)

**Prochaines étapes** : cartographier toutes les catégories du fichier complet, compléter le mapping, demander la doc API Matterhorn pour la synchro continue

**Lien** : [[Index - Imports-Exports]]

---

## 2026-06-11 — Mapping catégories finalisé et création de l'univers Chaussures

**Décision** : Mapping complet des 72 catégories Matterhorn vers les 7 univers poétiques PrestaShop (65 entrées `CATEGORY_MAP`). Création d'un 8e univers « Chaussures » avec 10 sous-catégories pour accueillir les 4 388 produits chaussures du catalogue.

**Choix de placement notables** :
- Bonnets/chapeaux → La Garde-Robe > Coiffures d'Été (pas de catégorie accessoires séparée)
- Foulards → La Garde-Robe > Soieries & Foulards
- 3 catégories érotiques (lingerie) fusionnées → L'Impudence > Objets du Désir
- Bretelles → Corps & Désirs > Corps & Velours (accessoire lingerie)
- Ensembles grandes tailles → La Garde-Robe > Mises en Scène

**Coefficient prix** : ×2.2 sur wholesale (marge ~55%), confirmé après benchmark concurrence.

**Scripts livrés** : `top10_xml.py` et `matterhorn_to_prestashop.py` synchronisés avec le même dictionnaire.

**Lien** : [[Journal-de-projet]]

---

## Décisions en attente

> [!warning] À trancher prochainement

- [ ] **Validation des 15 références de lancement** (après réception des catalogues 2e cercle)
- [ ] **Date précise de mise en ligne** (cible : avant Aïd al-Adha 2026)
- [ ] **Calendrier de passage en SASU** (préalable au sourcing direct Maroc)
- [ ] **Choix du nom de la première gamme** (réserve : Fatima, Aïcha — phase 2)
- [ ] **Coffret cadeau de lancement** (composition à définir)
- [ ] **Message marketing de lancement** (cf. étude 5 jours, livrable J+5)

---

## Principes directeurs (non négociables)

> [!important] Lignes rouges
> 1. **Pas de folklore, pas de bazar.** La marque reste premium et narrative.
> 2. **Pas de communication communautaire fermée.** On s'adresse aux deux rives simultanément.
> 3. **Pas de superlatifs vides** dans les textes. Toujours un détail concret.
> 4. **Pas d'achat de stock tant qu'on est en dropshipping.** La trésorerie reste libre.
> 5. **Pas de fournisseur sans qualification qualité.** Mieux vaut moins de produits que des références médiocres.

---

## Liens internes
- [[MOC - Omar de Mogador]]
- [[Identité de marque]]
- [[Plan 5 jours]]
