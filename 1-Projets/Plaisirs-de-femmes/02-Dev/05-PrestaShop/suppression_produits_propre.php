<?php
/**
 * ============================================================
 *  NETTOYAGE BOUTIQUE — Suppression produits (catégories intactes)
 *  Boutique : plaisirs-de-femmes.fr  |  PS 8.2.6
 * ------------------------------------------------------------
 *  À déposer à la RACINE de PrestaShop (à côté de index.php).
 *  Lancement en CLI uniquement :
 *
 *    php suppression_produits_propre.php                        → simulation produits
 *    php suppression_produits_propre.php --apply               → suppression produits
 *    php suppression_produits_propre.php --apply --batch=200   → par lot de 200
 *    php suppression_produits_propre.php --apply --marques     → + vide les marques
 *    php suppression_produits_propre.php --apply --fournisseurs → + vide les fournisseurs
 *    php suppression_produits_propre.php --apply --marques --fournisseurs → tout nettoyer
 *
 *  Ce script supprime :
 *    ✅ Produits et leurs déclinaisons
 *    ✅ Images produits (fichiers disque)
 *    ✅ Stocks associés
 *    ✅ Tags et associations fournisseurs
 *    ✅ Marques/fabricants (avec --marques)
 *    ✅ Fournisseurs (avec --fournisseurs)
 *
 *  Ce script NE TOUCHE PAS à :
 *    🔒 Catégories
 *    🔒 Attributs et groupes d'attributs (Taille, Couleur…)
 *    🔒 Commandes et clients
 *    🔒 Configuration boutique
 * ============================================================
 */

/* ── Config ──────────────────────────────────────────────── */

const ID_SHOP    = 1;
const ID_LANG    = 1;
const BATCH_SIZE = 100;   // produits traités par lot (évite les timeouts mémoire)

/* ── Arguments CLI ───────────────────────────────────────── */

$opts       = getopt('', ['apply', 'batch::', 'marques', 'fournisseurs']);
define('DRY_RUN',         !isset($opts['apply']));
define('BATCH',           isset($opts['batch']) ? max(1, (int)$opts['batch']) : BATCH_SIZE);
define('VIDER_MARQUES',   isset($opts['marques']));
define('VIDER_FOURNIS',   isset($opts['fournisseurs']));

/* ── Bootstrap PrestaShop ────────────────────────────────── */

if (!file_exists(__DIR__ . '/config/config.inc.php')) {
    echo "ERREUR : ce script doit être à la racine de PrestaShop.\n";
    exit(1);
}

require_once __DIR__ . '/config/config.inc.php';

$context           = Context::getContext();
$context->shop     = new Shop(ID_SHOP);
$context->language = new Language(ID_LANG);

/* ── Logger ──────────────────────────────────────────────── */

function log_msg(string $msg): void {
    echo '[' . date('H:i:s') . '] ' . $msg . PHP_EOL;
}

/* ── Suppression d'un produit ────────────────────────────── */

/**
 * Suppression directe via SQL pour contourner les hooks de modules tiers
 * (ex: iqitproductvariants) qui peuvent planter sur hookActionObjectProductDeleteAfter.
 * On reproduit ce que fait Product::delete() sans déclencher les hooks.
 */
function supprimer_produit(int $id_product): string {
    if (DRY_RUN) {
        return "SIMULATION suppression produit #$id_product";
    }

    $db  = Db::getInstance();
    $id  = (int)$id_product;
    $pre = _DB_PREFIX_;

    // Nom pour le log
    $nom = (string)$db->getValue(
        "SELECT name FROM {$pre}product_lang WHERE id_product=$id AND id_lang=" . ID_LANG
    );
    if (!$nom) $nom = "produit #$id";

    // 1. Images : suppression fichiers disque + BDD
    $images = Image::getImages(ID_LANG, $id);
    foreach ($images as $img_data) {
        $img = new Image((int)$img_data['id_image']);
        $img->delete();
    }

    // 2. Suppression SQL directe — tables passant par id_product_attribute d'abord
    // On récupère les IDs des déclinaisons avant de les supprimer
    $pa_ids = $db->executeS(
        "SELECT id_product_attribute FROM `{$pre}product_attribute` WHERE id_product=$id"
    );
    if ($pa_ids) {
        $pa_list = implode(',', array_column($pa_ids, 'id_product_attribute'));
        $db->execute("DELETE FROM `{$pre}product_attribute_combination`
                      WHERE id_product_attribute IN ($pa_list)");
        $db->execute("DELETE FROM `{$pre}product_attribute_image`
                      WHERE id_product_attribute IN ($pa_list)");
        @$db->execute("DELETE FROM `{$pre}product_attribute_lang`
                      WHERE id_product_attribute IN ($pa_list)");
    }

    // 3. Tables avec id_product direct
    $tables = [
        "product_attribute",
        "product_lang",
        "product_tag",
        "product_carrier",
        "product_shop",
        "product_supplier",
        "specific_price",
        "stock_available",
        "category_product",
        "cart_product",
        "product",                         // table principale en dernier
    ];
    foreach ($tables as $table) {
        $db->execute("DELETE FROM `{$pre}{$table}` WHERE id_product=$id");
    }

    // Tables optionnelles — certaines n'existent pas selon les modules installés
    $optionnelles = [
        "DELETE FROM `{$pre}layered_product_attribute` WHERE id_product=$id",
        "DELETE FROM `{$pre}favorite_product`          WHERE id_product=$id",
        "DELETE FROM `{$pre}stock_mvt` WHERE id_stock IN
            (SELECT id_stock FROM `{$pre}stock` WHERE id_product=$id)",
        "DELETE FROM `{$pre}stock` WHERE id_product=$id",
    ];
    foreach ($optionnelles as $sql) {
        try { $db->execute($sql); } catch (Exception $e) { /* table absente, on ignore */ }
    }

    return "SUPPRIMÉ « $nom » (#$id)";
}

/* ── Programme principal ─────────────────────────────────── */

/* ── Suppression marques ─────────────────────────────────── */

function vider_marques(): void {
    $db  = Db::getInstance();
    $pre = _DB_PREFIX_;

    $ids = $db->executeS("SELECT id_manufacturer FROM `{$pre}manufacturer`");
    if (empty($ids)) { log_msg('  Aucune marque trouvée.'); return; }

    $nb = 0;
    foreach ($ids as $row) {
        $id = (int)$row['id_manufacturer'];
        if (DRY_RUN) {
            log_msg("  SIMULATION suppression marque #$id");
            continue;
        }
        $nom = (string)$db->getValue(
            "SELECT name FROM `{$pre}manufacturer` WHERE id_manufacturer=$id"
        );
        $db->execute("DELETE FROM `{$pre}manufacturer_lang`  WHERE id_manufacturer=$id");
        $db->execute("DELETE FROM `{$pre}manufacturer_shop`  WHERE id_manufacturer=$id");
        $db->execute("DELETE FROM `{$pre}manufacturer`       WHERE id_manufacturer=$id");
        log_msg("  MARQUE supprimée : « $nom » (#$id)");
        $nb++;
    }
    if (!DRY_RUN) log_msg("  → $nb marque(s) supprimée(s)");
}

/* ── Suppression fournisseurs ────────────────────────────── */

function vider_fournisseurs(): void {
    $db  = Db::getInstance();
    $pre = _DB_PREFIX_;

    $ids = $db->executeS("SELECT id_supplier FROM `{$pre}supplier`");
    if (empty($ids)) { log_msg('  Aucun fournisseur trouvé.'); return; }

    $nb = 0;
    foreach ($ids as $row) {
        $id = (int)$row['id_supplier'];
        if (DRY_RUN) {
            log_msg("  SIMULATION suppression fournisseur #$id");
            continue;
        }
        $nom = (string)$db->getValue(
            "SELECT name FROM `{$pre}supplier` WHERE id_supplier=$id"
        );
        $db->execute("DELETE FROM `{$pre}supplier_lang`  WHERE id_supplier=$id");
        $db->execute("DELETE FROM `{$pre}supplier_shop`  WHERE id_supplier=$id");
        $db->execute("DELETE FROM `{$pre}product_supplier` WHERE id_supplier=$id");
        $db->execute("DELETE FROM `{$pre}supplier`       WHERE id_supplier=$id");
        log_msg("  FOURNISSEUR supprimé : « $nom » (#$id)");
        $nb++;
    }
    if (!DRY_RUN) log_msg("  → $nb fournisseur(s) supprimé(s)");
}

/* ── Programme principal ─────────────────────────────────── */

log_msg('══════════════════════════════════════════════════');
log_msg('  NETTOYAGE BOUTIQUE' . (DRY_RUN ? ' [SIMULATION]' : ' [RÉEL]'));
log_msg('══════════════════════════════════════════════════');

// Récupère tous les IDs produits
$ids = Db::getInstance()->executeS(
    'SELECT id_product FROM ' . _DB_PREFIX_ . 'product ORDER BY id_product ASC'
);

if (empty($ids)) {
    log_msg('Aucun produit trouvé — boutique déjà vide.');
    exit(0);
}

$total     = count($ids);
$traites   = 0;
$supprimes = 0;
$erreurs   = 0;

log_msg("$total produit(s) trouvé(s) — lot de " . BATCH . " à la fois");
if (DRY_RUN) {
    log_msg('Mode SIMULATION — relancez avec --apply pour supprimer réellement.');
}
log_msg('──────────────────────────────────────────────────');

foreach (array_chunk($ids, BATCH) as $lot) {
    foreach ($lot as $row) {
        $id  = (int)$row['id_product'];
        $res = supprimer_produit($id);
        log_msg("  $res");
        $traites++;
        if (!DRY_RUN && str_starts_with($res, 'SUPPRIMÉ')) {
            $supprimes++;
        }
    }
    // Libère la mémoire entre les lots
    if (!DRY_RUN) {
        gc_collect_cycles();
    }
    $pct = round($traites / $total * 100);
    log_msg("  → Progression : $traites / $total ($pct%)");
}

// Marques
if (VIDER_MARQUES) {
    log_msg('──────────────────────────────────────────────────');
    log_msg('  MARQUES / FABRICANTS');
    log_msg('──────────────────────────────────────────────────');
    vider_marques();
}

// Fournisseurs
if (VIDER_FOURNIS) {
    log_msg('──────────────────────────────────────────────────');
    log_msg('  FOURNISSEURS');
    log_msg('──────────────────────────────────────────────────');
    vider_fournisseurs();
}

log_msg('══════════════════════════════════════════════════');
if (DRY_RUN) {
    log_msg("SIMULATION terminée — $total produit(s) auraient été supprimés.");
    log_msg("Relancez avec --apply pour effectuer la suppression.");
} else {
    log_msg("TERMINÉ — $supprimes produit(s) supprimés sur $total.");
}
log_msg('══════════════════════════════════════════════════');
