# Matterhorn REST API — Documentation

> Source : documentation officielle Matterhorn, sauvegardée le 2026-06-12

---

## Endpoints

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/B2BAPI/ITEMS/?page=1` | Liste produits (100/page, max 1000 via `limit`) |
| GET | `/B2BAPI/ITEMS/{id}` | Détail d'un produit |
| GET | `/B2BAPI/DICTIONARIES/BRANDS` | Liste des marques |
| GET | `/B2BAPI/DICTIONARIES/CATEGORIES` | Liste des catégories |
| GET | `/B2BAPI/DICTIONARIES/DELIVERY` | Méthodes de livraison |
| PUT | `/B2BAPI/ACCOUNT/ORDERS/` | Passer une commande |
| GET | `/B2BAPI/ACCOUNT/ORDERS/{id}` | Détail d'une commande |

## Domaines par langue

- **Français** : `lingeriematterhorn.fr`
- Anglais : `matterhorn-wholesale.com`
- Allemand : `matterhorn-moda.de`

## Authentification

```
Authorization: YOUR-API-KEY
accept: application/json
```

Clé stockée sur le serveur : `/home/plaisirs-de-femmes/.matterhorn_key`

## Filtres produits

- `brand_id` — ID fabricant
- `category_id` — ID catégorie
- `new_collection=1` — nouveautés (60 derniers jours)
- `last_update=YYYY-MM-DD HH:MM` — modifiés depuis (stock/prix)
- `page` / `limit` — pagination

## Champs réponse produit

```
id, active, name, name_without_number, description, creation_date,
color, category_name, category_id, category_path, brand_id, brand,
stock_total, url, images[], new_collection, variants[],
size_table, prices{}, size_table_txt, size_table_html
```

### Structure variant

```json
{
    "variant_uid": "1090549",
    "name": "34",
    "stock": "35",
    "max_processing_time": "3",
    "ean": ""
}
```

## Notes importantes

- **variant_uid** est requis pour les commandes (pas le product id)
- Le paiement se fait hors API (lien email ou panel client)
- L'API ne contient PAS `other_colors` — ce champ n'est dispo que dans le **CSV fournisseur**
