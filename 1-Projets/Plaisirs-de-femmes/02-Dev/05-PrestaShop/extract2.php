<?php
// export_api_descriptions.php — à la racine PrestaShop, php export_api_descriptions.php
const MH_API_BASE = 'https://matterhorn-wholesale.com/B2BAPI/';
define('MH_API_KEY_FILE', '/home/plaisirs-de-femmes/.matterhorn_key');

$BRAND_WHITELIST = [4,608,384,65,38,39,46,539,615,498,444,610,547,19,17,199,52,197,
                    432,260,503,422,175,305,438,363,435,85,350,48,50,258,487,582,75,517];

$key = trim((string)file_get_contents(MH_API_KEY_FILE));

// références réellement en boutique (export_a_decrire.php)
$refs = [];
if ($fr = fopen('refs_boutique.csv', 'r')) {
    fgetcsv($fr);
    while ($row = fgetcsv($fr)) { if (!empty($row[0])) $refs[trim($row[0])] = true; }
    fclose($fr);
}

function api_get($params, $key) {
    $url = MH_API_BASE . 'ITEMS/?' . http_build_query($params);
    $ch = curl_init($url);
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER=>true, CURLOPT_TIMEOUT=>60,
        CURLOPT_HTTPHEADER=>['Authorization: '.$key, 'accept: application/json']]);
    $b = curl_exec($ch); curl_close($ch);
    return json_decode($b, true) ?: [];
}
function composition($txt) {  // 1re ligne du size_table_txt
    if (preg_match('/^(.*?%.*?)\s{2,}/u', trim((string)$txt), $m)) return trim($m[1]);
    return '';
}

$out = fopen('produits_a_decrire.csv', 'w');
fputcsv($out, ['reference','nom','couleur','composition','texte_source']);
$n = 0;
foreach ($BRAND_WHITELIST as $bid) {
    $page = 1;
    do {
        $items = api_get(['brand_id'=>$bid, 'page'=>$page], $key);
        foreach ($items as $it) {
            $ref = 'MH' . $it['id'];
            if (!isset($refs[$ref])) continue;                 // borne à la boutique
            $desc = trim((string)($it['description'] ?? ''));
            if ($desc === '') continue;
            fputcsv($out, [$ref, trim((string)($it['name']??'')),
                trim((string)($it['color']??'')),
                composition($it['size_table_txt'] ?? ''), $desc]);
            $n++;
        }
        $page++;
    } while (count($items) === 1000);
    echo "marque $bid : cumul $n\n";
}
fclose($out);
echo "TOTAL : $n descriptions -> produits_a_decrire.csv\n";