<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);
set_time_limit(0);

require_once __DIR__ . '/config/config.inc.php';
require_once __DIR__ . '/init.php';

$dryRun = isset($_GET['dryrun']) ? (bool)$_GET['dryrun'] : false;
$batchSize = 100;

$context = Context::getContext();
$idLang = (int)Configuration::get('PS_LANG_DEFAULT');

$db = Db::getInstance();

$total = (int)$db->getValue('SELECT COUNT(*) FROM `' . _DB_PREFIX_ . 'product`');
echo "Produits trouvés : {$total}<br>";

if ($dryRun) {
    echo "Mode DRY RUN actif : aucune suppression effectuée.<br>";
    exit;
}

$deleted = 0;

do {
    $rows = $db->executeS('
        SELECT p.`id_product`
        FROM `' . _DB_PREFIX_ . 'product` p
        ORDER BY p.`id_product` ASC
        LIMIT ' . (int)$batchSize
    );

    if (empty($rows)) {
        break;
    }

    foreach ($rows as $row) {
        $idProduct = (int)$row['id_product'];
        $product = new Product($idProduct, false, $idLang);

        if (!Validate::isLoadedObject($product)) {
            echo "Produit #{$idProduct} introuvable ou déjà supprimé.<br>";
            continue;
        }

        try {
            if ($product->delete()) {
                $deleted++;
                echo "Produit #{$idProduct} supprimé.<br>";
            } else {
                echo "Échec suppression produit #{$idProduct}.<br>";
            }
        } catch (Exception $e) {
            echo "Erreur produit #{$idProduct} : " . htmlspecialchars($e->getMessage()) . "<br>";
        }

        @ob_flush();
        flush();
    }

} while (!empty($rows));

echo "<br>Terminé. Produits supprimés : {$deleted}<br>";
echo "Arborescence des catégories conservée.<br>";