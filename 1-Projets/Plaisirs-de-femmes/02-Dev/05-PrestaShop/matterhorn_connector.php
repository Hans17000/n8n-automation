<?php
/**
 * ============================================================
 *  CONNECTEUR MATTERHORN  ->  PRESTASHOP 8.2.6
 *  Boutique : plaisirs-de-femmes.fr
 * ------------------------------------------------------------
 *  À DÉPOSER À LA RACINE DE PRESTASHOP (à côté de index.php).
 *  Lancement en CLI :   php matterhorn_connector.php
 *  Options :
 *     --brand=38        ne traite qu'une marque (test)
 *     --limit=20        s'arrête après N produits (test)
 *     --apply           désactive le mode simulation (écrit pour de vrai)
 *
 *  PHILOSOPHIE : idempotent. On match sur la référence Matterhorn.
 *  Relancer 10 fois = même résultat. JAMAIS de doublon.
 * ============================================================
 */

/* =======================  CONFIG  ======================= */

const MH_API_BASE = 'https://matterhorn-wholesale.com/B2BAPI/';
// Clé API lue dans un fichier HORS racine web (jamais en clair dans ce fichier) :
define('MH_API_KEY_FILE', '/home/plaisirs-de-femmes/.matterhorn_key');

const MARGIN_COEF       = 2.5;     // coefficient de marge — LE chiffre à ajuster un jour
const VAT_RATE          = 0.20;    // TVA 20 %
const PRICE_ENDING      = 0.90;    // arrondi psychologique ,90

// --- IDs PrestaShop à CONFIRMER dans ton back-office ---
const ID_TAX_RULES_GROUP = 1;      // TODO Localisation > Taxes : groupe "FR TVA 20%"
const ID_LANG            = 1;      // TODO id langue FR
const ID_SHOP            = 1;      // TODO id boutique
const ID_CATEGORY_HOME   = 2;      // racine "Accueil"

// Univers boutique => id catégorie PrestaShop (TODO : confirme/complète ces IDs)
$UNIVERS_CATEGORY = [
    'bodies_ensembles' => 19,   // 01
    'nuisettes'        => 25,   // 02
    'corsets'          => 21,   // 03
    'robes'            => 26,   // 04
    'bas'              => 23,   // 05
    'audace'           => 32,   // 06
    'courbes'          => 0,    // TODO id de l'Atelier des Courbes (0 = ignorer tant qu'absent)
];

// Liste blanche : brand_id Matterhorn => nom (pour le journal)
$BRAND_WHITELIST = [
    4=>'Axami', 608=>'Casmir', 384=>'Angels Never Sin', 65=>'Anais', 38=>'Obsessive',
    39=>'Livia Corsetti Fashion', 46=>'Passion', 539=>'Vittoria Ventini', 615=>'Pure Sin',
    498=>'MissO', 444=>'PariPari Lingerie', 610=>'Barbara Lingerie', 547=>'Momenti Per Me',
    19=>'Gaia', 17=>'Mat', 199=>'Gorsenia Lingerie', 52=>'Gorteks', 197=>'Kinga',
    432=>'Sensis', 260=>'Esotiq', 503=>'De Lafense', 422=>'Kalimo',
    175=>'Gabriella', 305=>'Gatta', 438=>'Fiore', 363=>'Lemoniade', 435=>'Bas Bleu',
    85=>'Julimex', 350=>'Kamea',
    48=>'Irall', 50=>'Eldar', 258=>'Donna', 487=>'Dn-nightwear', 582=>'Doctor Nap',
    75=>'Nipplex', 517=>'Julimex Shapewear',
];

// Catégorie Matterhorn (feuille) => univers boutique
$MH_CAT_TO_UNIVERS = [
    // 01 Bodies & Ensembles  (soutiens-gorge, culottes, parures)
    25=>'bodies_ensembles', 155=>'bodies_ensembles', 1=>'bodies_ensembles', 26=>'bodies_ensembles',
    27=>'bodies_ensembles', 3=>'bodies_ensembles', 10=>'bodies_ensembles', 2=>'bodies_ensembles',
    38=>'bodies_ensembles',
    // 02 Nuisettes & Déshabillés
    29=>'nuisettes', 12=>'nuisettes', 11=>'nuisettes', 23=>'nuisettes',
    // 03 Corsets & Guêpières
    8=>'corsets', 152=>'corsets', 137=>'corsets',
    // 04 Robes & Tenues
    39=>'robes',
    // 05 Bas & Collants
    187=>'bas',
    // 06 Audace & Wetlook  (Obsessive / Livia atterrissent surtout ici)
    37=>'audace', 153=>'audace',
    // Atelier des Courbes (catégories plus size dédiées)
    358=>'courbes', 359=>'courbes', 339=>'courbes',
];

// Catégories Matterhorn EXCLUES d'office (sexshop -> réservé à ose-le.fr)
$MH_CAT_EXCLUDE = [146, 135];

define('LOG_FILE', '/home/plaisirs-de-femmes/matterhorn_sync.log');

/* =======================  ARGUMENTS CLI  ======================= */

$opts       = getopt('', ['brand::', 'limit::', 'apply']);
$ONLY_BRAND = isset($opts['brand']) ? (int)$opts['brand'] : null;
$LIMIT      = isset($opts['limit']) ? (int)$opts['limit'] : 0;
define('DRY_RUN', !isset($opts['apply']));   // par défaut : SIMULATION

/* =======================  BOOTSTRAP PRESTASHOP  ======================= */

require_once __DIR__ . '/config/config.inc.php';

$context        = Context::getContext();
$context->shop   = new Shop(ID_SHOP);
$context->language = new Language(ID_LANG);

/* =======================  OUTILS  ======================= */

function mh_log(string $msg): void {
    $line = '[' . date('Y-m-d H:i:s') . '] ' . $msg . PHP_EOL;
    echo $line;
    @file_put_contents(LOG_FILE, $line, FILE_APPEND);
}

/** Appel GET à l'API Matterhorn (JSON décodé en tableau). */
function mh_api_get(string $path, array $params = []): ?array {
    static $key = null;
    if ($key === null) {
        $key = trim((string)@file_get_contents(MH_API_KEY_FILE));
        if ($key === '') { mh_log('ERREUR : clé API introuvable dans ' . MH_API_KEY_FILE); exit(1); }
    }
    $url = MH_API_BASE . ltrim($path, '/');
    if ($params) { $url .= '?' . http_build_query($params); }

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 60,
        CURLOPT_HTTPHEADER     => ['Authorization: ' . $key, 'accept: application/json'],
    ]);
    $body = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($code !== 200) { mh_log("ERREUR API ($code) sur $path"); return null; }
    $data = json_decode($body, true);
    return is_array($data) ? $data : null;
}

/** Prix net HT -> [prix_ht_a_stocker, prix_ttc_affiche] avec arrondi ,90. */
function mh_prix(float $net): array {
    $ttc  = $net * MARGIN_COEF * (1 + VAT_RATE);
    $base = floor($ttc);
    $cand = $base + PRICE_ENDING;
    if ($cand < $ttc) { $cand += 1.0; }      // on monte au prochain X,90 (jamais sous la marge)
    $ttc_final = round($cand, 2);
    $ht_final  = round($ttc_final / (1 + VAT_RATE), 6);
    return [$ht_final, $ttc_final];
}

/** Récupère (ou crée) le groupe d'attributs "Taille". */
function mh_taille_group(): int {
    static $id = null;
    if ($id !== null) return $id;
    $sql = 'SELECT id_attribute_group FROM ' . _DB_PREFIX_ . "attribute_group_lang
            WHERE name='Taille' AND id_lang=" . (int)ID_LANG;
    $id = (int)Db::getInstance()->getValue($sql);
    if ($id) return $id;
    if (DRY_RUN) { return $id = 0; }
    $g = new AttributeGroup();
    $g->is_color_group = false;
    $g->group_type = 'select';
    $g->name = [ID_LANG => 'Taille'];
    $g->public_name = [ID_LANG => 'Taille'];
    $g->add();
    return $id = (int)$g->id;
}

/** Récupère (ou crée) une valeur de taille -> id_attribute. */
function mh_taille_attr(string $taille): int {
    static $cache = [];
    $taille = trim($taille);
    if ($taille === '') $taille = 'Unique';
    if (isset($cache[$taille])) return $cache[$taille];

    $gid = mh_taille_group();
    $sql = 'SELECT a.id_attribute FROM ' . _DB_PREFIX_ . 'attribute a
            JOIN ' . _DB_PREFIX_ . 'attribute_lang al ON al.id_attribute=a.id_attribute
            WHERE a.id_attribute_group=' . (int)$gid . " AND al.name=" . (DRY_RUN ? "''" : "'" . pSQL($taille) . "'") . '
            AND al.id_lang=' . (int)ID_LANG;
    $id = (int)Db::getInstance()->getValue($sql);
    if ($id) return $cache[$taille] = $id;
    if (DRY_RUN) return $cache[$taille] = 0;

    $a = new ProductAttribute();
    $a->id_attribute_group = $gid;
    $a->name = [ID_LANG => $taille];
    $a->add();
    return $cache[$taille] = (int)$a->id;
}

/** Récupère (ou crée) un fabricant -> id_manufacturer. */
function mh_manufacturer(string $brand): int {
    static $cache = [];
    if (isset($cache[$brand])) return $cache[$brand];
    $id = (int)Manufacturer::getIdByName($brand);
    if ($id) return $cache[$brand] = $id;
    if (DRY_RUN) return $cache[$brand] = 0;
    $m = new Manufacturer();
    $m->name = $brand;
    $m->active = true;
    $m->add();
    return $cache[$brand] = (int)$m->id;
}

/** Détermine la catégorie boutique (id PS) pour un produit Matterhorn.
 *  Le NOM du produit prime sur le category_path, car les catégories Matterhorn
 *  sont souvent des fourre-tout ("Sexy Bodysuits, Corsets, Belts, Panties...").
 *  Règles testées du plus spécifique au plus général. À AFFINER librement. */
function mh_univers_categorie(array $item): int {
    global $UNIVERS_CATEGORY;
    $nom  = mb_strtolower($item['name'] ?? '');
    $path = mb_strtolower($item['category_path'] ?? '');
    $hay  = $nom . ' | ' . $path;   // on cherche dans le nom PUIS le chemin

    // 1) Exclusions sexshop (accessoires érotiques -> réservés à ose-le.fr)
    if (str_contains($path, 'erotic accessories') || str_contains($path, 'sex, erotic')) return 0;

    // 2) Mots-clés par univers (ordre = priorité)
    $regles = [
        'courbes'          => ['plus size', 'grande taille'],
        'bas'              => ['stocking', 'tights', 'hold-up', 'hold up', 'stay-up', 'hosiery',
                               'collant', 'bas ', 'fishnet tights'],
        'nuisettes'        => ['nightgown', 'nightdress', 'nightie', 'babydoll', 'baby doll', 'chemise',
                               'negligee', 'peignoir', 'dressing gown', 'bathrobe', 'kimono',
                               'pyjama', 'pajama', 'nuisette', 'deshabille', 'sleepwear', 'nightwear'],
        'corsets'          => ['corset', 'guepiere', 'guêpière', 'basque', 'bustier', 'waist cincher',
                               'suspender belt', 'garter belt'],
        'robes'            => ['dress', 'skirt', 'jupe', 'gown', 'robe '],
        'audace'           => ['wetlook', 'wet look', 'vinyl', 'latex', 'leather', 'harness',
                               'crotchless', 'open ', 'ouvert'],
        'bodies_ensembles' => ['push up', 'push-up', 'balconette', 'bra', 'soutien', 'body', 'bodysuit',
                               'ensemble', 'lingerie set', 'sets', 'thong', 't-back', 'tback', 'string',
                               'panties', 'panty', 'brief', 'knicker', 'culotte', 'slip', 'tanga'],
    ];
    foreach ($regles as $u => $mots) {
        foreach ($mots as $kw) {
            if (str_contains($hay, $kw)) {
                return (int)($UNIVERS_CATEGORY[$u] ?? 0);
            }
        }
    }
    return 0; // non classé -> ignoré
}

/** Importe l'image de couverture si le produit n'en a pas encore. */
function mh_image_cover(int $id_product, array $images): void {
    if (DRY_RUN || empty($images)) return;
    if (Db::getInstance()->getValue('SELECT id_image FROM ' . _DB_PREFIX_ . 'image WHERE id_product=' . (int)$id_product)) {
        return; // déjà une image
    }
    $url = $images[0];
    $img = new Image();
    $img->id_product = $id_product;
    $img->position   = 1;
    $img->cover      = true;
    if (!$img->add()) return;
    $img->associateTo([ID_SHOP]);
    $tmp = tempnam(sys_get_temp_dir(), 'mh');
    $bin = @file_get_contents($url);
    if ($bin === false) { @unlink($tmp); return; }
    file_put_contents($tmp, $bin);
    $path = $img->getPathForCreation();
    ImageManager::resize($tmp, $path . '.jpg');
    foreach (ImageType::getImagesTypes('products') as $t) {
        ImageManager::resize($tmp, $path . '-' . $t['name'] . '.jpg', (int)$t['width'], (int)$t['height']);
    }
    @unlink($tmp);
}

/* =======================  UPSERT D'UN PRODUIT  ======================= */

function mh_upsert(array $item, string $brand): string {
    $ref = 'MH' . $item['id'];                 // clé d'idempotence
    $id_cat = mh_univers_categorie($item);
    if ($id_cat <= 0) return 'ignoré (hors univers/exclu)';

    [$ht, $ttc] = mh_prix((float)($item['prices']['EUR'] ?? 0));
    if ($ht <= 0) return 'ignoré (prix nul)';

    // Stock total -> visibilité : on MASQUE les ruptures (active=0), on ne supprime jamais.
    // Le produit réapparaît tout seul au prochain cron dès que le stock revient.
    $stock_total = 0;
    foreach (($item['variants'] ?? []) as $v) { $stock_total += (int)$v['stock']; }
    $actif = $stock_total > 0 ? 1 : 0;

    $nom = trim(preg_replace('/\s+/', ' ', $item['name']));
    $existe = (int)Product::getIdByReference($ref);

    if (DRY_RUN) {
        return ($existe ? 'MAJ' : 'CREATION') . " | $nom | $ttc EUR TTC | cat $id_cat | "
             . count($item['variants'] ?? []) . " tailles | stock $stock_total"
             . ($actif ? '' : ' (masqué)');
    }

    $p = $existe ? new Product($existe) : new Product();
    // --- Champs TOUJOURS rafraîchis (pilotés par le fournisseur) ---
    $p->reference           = $ref;
    $p->price               = $ht;
    $p->id_tax_rules_group  = ID_TAX_RULES_GROUP;
    $p->id_category_default = $id_cat;
    $p->active              = $actif;
    $p->is_virtual          = 0;

    if (!$existe) {
        // --- Champs posés UNE SEULE FOIS à la création ---
        // (ensuite préservés : tes descriptions Mistral et tes images ComfyUI survivent au cron)
        $p->name            = [ID_LANG => $nom];
        $p->link_rewrite    = [ID_LANG => Tools::link_rewrite($nom . '-' . $item['id'])];
        $p->description     = [ID_LANG => ($item['size_table_html'] ?? '')];
        $p->id_manufacturer = mh_manufacturer($brand);
        $p->add();
    } else {
        $p->save();   // ne réécrit QUE prix / catégorie / visibilité ; nom, description, image intacts
    }

    // Catégories pilotées par le routage (recalculées à chaque passage : si tu affines les règles,
    // un simple --apply re-range tout le catalogue)
    $p->updateCategories([ID_CATEGORY_HOME, $id_cat]);

    // Déclinaisons par taille + stock (idempotent : reference = variant_uid)
    foreach (($item['variants'] ?? []) as $v) {
        $vref  = (string)$v['variant_uid'];
        $stock = (int)$v['stock'];
        $idpa  = (int)Db::getInstance()->getValue(
            'SELECT id_product_attribute FROM ' . _DB_PREFIX_ . 'product_attribute
             WHERE id_product=' . (int)$p->id . " AND reference='" . pSQL($vref) . "'");
        if (!$idpa) {
            $c = new Combination();
            $c->id_product       = (int)$p->id;
            $c->reference        = $vref;
            $c->minimal_quantity = 1;
            $c->add();
            $c->setAttributes([mh_taille_attr((string)$v['name'])]);
            $idpa = (int)$c->id;
        }
        StockAvailable::setQuantity((int)$p->id, $idpa, $stock, ID_SHOP);
    }

    // Image de couverture : posée à la création seulement (mh_image_cover s'abstient si une image existe)
    mh_image_cover((int)$p->id, $item['images'] ?? []);

    return ($existe ? 'MAJ' : 'CREATION') . " | $nom | $ttc EUR | cat $id_cat | stock $stock_total"
         . ($actif ? '' : ' (masqué)');
}

/* =======================  BOUCLE PRINCIPALE  ======================= */

mh_log('==== SYNC MATTERHORN ' . (DRY_RUN ? '[SIMULATION]' : '[APPLICATION REELLE]') . ' ====');

$marques = $ONLY_BRAND ? [$ONLY_BRAND => ($BRAND_WHITELIST[$ONLY_BRAND] ?? '?')] : $BRAND_WHITELIST;
$total = 0;

foreach ($marques as $bid => $bname) {
    mh_log("--- Marque : $bname (#$bid) ---");
    $page = 1;
    do {
        $items = mh_api_get('ITEMS/', ['brand_id' => $bid, 'page' => $page]);
        if (!$items) break;
        foreach ($items as $item) {
            $res = mh_upsert($item, $bname);
            mh_log("  [{$item['id']}] $res");
            $total++;
            if ($LIMIT && $total >= $LIMIT) { mh_log("== Limite de test atteinte ($LIMIT) =="); break 3; }
        }
        $page++;
    } while (count($items) === 1000);   // page pleine -> il y a une suite
}

mh_log("==== TERMINÉ : $total produits traités ====");
