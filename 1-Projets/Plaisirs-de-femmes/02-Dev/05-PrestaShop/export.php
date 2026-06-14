<?php
// export_a_decrire.php  — à déposer à la racine, lancer : php export_a_decrire.php
require_once __DIR__ . '/config/config.inc.php';
const ID_LANG = 1;

$rows = Db::getInstance()->executeS(
  'SELECT p.reference, pl.name, m.name AS marque, cl.name AS categorie
   FROM ' . _DB_PREFIX_ . 'product p
   JOIN ' . _DB_PREFIX_ . 'product_lang pl
        ON pl.id_product = p.id_product AND pl.id_lang = ' . (int)ID_LANG . '
   LEFT JOIN ' . _DB_PREFIX_ . 'manufacturer m
        ON m.id_manufacturer = p.id_manufacturer
   LEFT JOIN ' . _DB_PREFIX_ . 'category_lang cl
        ON cl.id_category = p.id_category_default AND cl.id_lang = ' . (int)ID_LANG . '
   WHERE p.reference LIKE "MH%"
     AND (pl.description_short IS NULL OR pl.description_short = "")'  // seulement les non décrits
);

$out = fopen('produits_a_decrire.csv', 'w');
fputcsv($out, ['reference', 'nom', 'marque', 'categorie']);
foreach ($rows as $r) {
    fputcsv($out, [$r['reference'], $r['name'], $r['marque'], $r['categorie']]);
}
fclose($out);
echo count($rows) . " produits exportés vers produits_a_decrire.csv\n";