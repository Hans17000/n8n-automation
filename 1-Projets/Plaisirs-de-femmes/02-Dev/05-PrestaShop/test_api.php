<?php
// inspect_api_item.php  — php inspect_api_item.php 4   (4 = brand_id Axami)
$brand = (int)($argv[1] ?? 4);
$key = trim((string)file_get_contents('/home/plaisirs-de-femmes/.matterhorn_key'));
$url = 'https://matterhorn-wholesale.com/B2BAPI/ITEMS/?'
     . http_build_query(['brand_id' => $brand, 'page' => 1]);
$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => ['Authorization: ' . $key, 'accept: application/json'],
]);
$item = (json_decode(curl_exec($ch), true)[0]) ?? null;
curl_close($ch);
if (!$item) { echo "Pas d'item renvoyé.\n"; exit; }

echo "=== Clés de premier niveau ===\n";
foreach ($item as $k => $v) {
    $ap = is_scalar($v) ? mb_substr((string)$v, 0, 80) : '[' . gettype($v) . ']';
    echo sprintf("  %-22s : %s\n", $k, $ap);
}
echo "\n=== Champs ressemblant à une description ===\n";
foreach ($item as $k => $v) {
    if (is_string($v) && (stripos($k, 'desc') !== false || mb_strlen($v) > 120)) {
        echo "--- $k ---\n" . mb_substr($v, 0, 500) . "\n\n";
    }
}