-- ═══════════════════════════════════════════════════════════════════════════
--  PATCH — 90 produits PDF déjà importés sans catégorie ni stock
--
--  Problèmes corrigés :
--    1. Stock = 0  →  mettre à 5 pour les produits sans déclinaison
--    2. id_category_default = 0  →  assigner la bonne catégorie PS
--    3. ps_category_product manquant  →  insérer la ligne de liaison
--    4. Produits non visibles en front-end  →  forcer active=1
--
--  PRÉREQUIS :
--    • Avoir créé dans l'admin PS les catégories :
--        Lingerie Intime  →  Soutiens-Gorge & Parures
--                         →  Corps & Désirs
--                         →  Corsets & Architecture
--        Nuits & Désirs   →  Nuisettes & Déshabillés
--                         →  Pyjamas & Loungewear
--        Style & Silhouette → Robes & Tenues
--                           → Bas & Collants
--        Grandes Grâces
--    • Adapter @id_cat_* ci-dessous avec les vrais id_category de votre PS
--      (SELECT id_category, name FROM ps_category_lang WHERE id_lang=1)
--
--  UTILISATION :
--    mysql -u [user] -p [db_name] < patch_90_produits.sql
-- ═══════════════════════════════════════════════════════════════════════════

-- ── 0. Récupérer les id_category (adapter ces valeurs selon votre PS) ──────
--  Exécuter d'abord pour connaître vos ids :
--  SELECT id_category, name FROM ps_category_lang WHERE id_lang=1 ORDER BY id_category;

-- Variables de référence — ADAPTER ICI
SET @id_cat_soutiens   = (SELECT c.id_category FROM ps_category c
                           JOIN ps_category_lang l ON l.id_category=c.id_category
                           WHERE l.name='Soutiens-Gorge & Parures' AND l.id_lang=1 LIMIT 1);
SET @id_cat_corps      = (SELECT c.id_category FROM ps_category c
                           JOIN ps_category_lang l ON l.id_category=c.id_category
                           WHERE l.name='Corps & Désirs' AND l.id_lang=1 LIMIT 1);
SET @id_cat_corsets    = (SELECT c.id_category FROM ps_category c
                           JOIN ps_category_lang l ON l.id_category=c.id_category
                           WHERE l.name='Corsets & Architecture' AND l.id_lang=1 LIMIT 1);
SET @id_cat_nuisettes  = (SELECT c.id_category FROM ps_category c
                           JOIN ps_category_lang l ON l.id_category=c.id_category
                           WHERE l.name='Nuisettes & Déshabillés' AND l.id_lang=1 LIMIT 1);
SET @id_cat_pyjamas    = (SELECT c.id_category FROM ps_category c
                           JOIN ps_category_lang l ON l.id_category=c.id_category
                           WHERE l.name='Pyjamas & Loungewear' AND l.id_lang=1 LIMIT 1);
SET @id_cat_robes      = (SELECT c.id_category FROM ps_category c
                           JOIN ps_category_lang l ON l.id_category=c.id_category
                           WHERE l.name='Robes & Tenues' AND l.id_lang=1 LIMIT 1);
SET @id_cat_collants   = (SELECT c.id_category FROM ps_category c
                           JOIN ps_category_lang l ON l.id_category=c.id_category
                           WHERE l.name='Bas & Collants' AND l.id_lang=1 LIMIT 1);

-- Afficher pour vérification
SELECT 'Soutiens-Gorge & Parures' AS categorie, @id_cat_soutiens  AS id_category
UNION SELECT 'Corps & Désirs',         @id_cat_corps
UNION SELECT 'Corsets & Architecture', @id_cat_corsets
UNION SELECT 'Nuisettes & Déshabillés',@id_cat_nuisettes
UNION SELECT 'Pyjamas & Loungewear',   @id_cat_pyjamas
UNION SELECT 'Robes & Tenues',         @id_cat_robes
UNION SELECT 'Bas & Collants',         @id_cat_collants;

-- ── 1. Stock = 5 pour tous les produits PDF sans déclinaison ─────────────
UPDATE ps_stock_available sa
JOIN   ps_product p ON p.id_product = sa.id_product
SET    sa.quantity = 5
WHERE  p.reference LIKE 'PDF-%'
  AND  sa.id_product_attribute = 0
  AND  sa.quantity = 0;

-- ── 2. Forcer active=1 dans ps_product et ps_product_shop ─────────────────
UPDATE ps_product      SET active=1 WHERE reference LIKE 'PDF-%';
UPDATE ps_product_shop SET active=1
WHERE id_product IN (SELECT id_product FROM ps_product WHERE reference LIKE 'PDF-%')
  AND id_shop=1;

-- ═══════════════════════════════════════════════════════════════════════════
--  3. Assigner catégorie par groupe de références
--     Chaque bloc : UPDATE id_category_default + INSERT ps_category_product
-- ═══════════════════════════════════════════════════════════════════════════

-- ── Cat 1 : Strings → Corps & Désirs ─────────────────────────────────────
UPDATE ps_product SET id_category_default=@id_cat_corps
WHERE reference IN ('PDF-227532','PDF-217428','PDF-219480','PDF-221476','PDF-219481',
                    'PDF-225187','PDF-222578','PDF-226371','PDF-226377','PDF-179216');
UPDATE ps_product_shop SET id_category_default=@id_cat_corps
WHERE id_shop=1 AND id_product IN (
    SELECT id_product FROM ps_product
    WHERE reference IN ('PDF-227532','PDF-217428','PDF-219480','PDF-221476','PDF-219481',
                        'PDF-225187','PDF-222578','PDF-226371','PDF-226377','PDF-179216'));
INSERT IGNORE INTO ps_category_product (id_category, id_product, position)
SELECT @id_cat_corps, id_product, 0 FROM ps_product
WHERE reference IN ('PDF-227532','PDF-217428','PDF-219480','PDF-221476','PDF-219481',
                    'PDF-225187','PDF-222578','PDF-226371','PDF-226377','PDF-179216');

-- ── Cat 2 : Soutiens-Gorge → Soutiens-Gorge & Parures ────────────────────
UPDATE ps_product SET id_category_default=@id_cat_soutiens
WHERE reference IN ('PDF-203243','PDF-227481','PDF-227504','PDF-227960',
                    'PDF-198762','PDF-206638','PDF-206639','PDF-201074',
                    'PDF-213658','PDF-208965');
UPDATE ps_product_shop SET id_category_default=@id_cat_soutiens
WHERE id_shop=1 AND id_product IN (
    SELECT id_product FROM ps_product
    WHERE reference IN ('PDF-203243','PDF-227481','PDF-227504','PDF-227960',
                        'PDF-198762','PDF-206638','PDF-206639','PDF-201074',
                        'PDF-213658','PDF-208965'));
INSERT IGNORE INTO ps_category_product (id_category, id_product, position)
SELECT @id_cat_soutiens, id_product, 0 FROM ps_product
WHERE reference IN ('PDF-203243','PDF-227481','PDF-227504','PDF-227960',
                    'PDF-198762','PDF-206638','PDF-206639','PDF-201074',
                    'PDF-213658','PDF-208965');

-- ── Cat 3 & 4 : Bodies, Bustiers, Ensembles Sexy → Corsets & Architecture ─
UPDATE ps_product SET id_category_default=@id_cat_corsets
WHERE reference IN ('PDF-149949','PDF-144174','PDF-182304','PDF-188964','PDF-188965',
                    'PDF-169973','PDF-184827','PDF-172363','PDF-145215','PDF-200807',
                    'PDF-161758','PDF-158920','PDF-195250','PDF-195251','PDF-195252',
                    'PDF-206259','PDF-206207','PDF-206273','PDF-206218','PDF-145572');
UPDATE ps_product_shop SET id_category_default=@id_cat_corsets
WHERE id_shop=1 AND id_product IN (
    SELECT id_product FROM ps_product
    WHERE reference IN ('PDF-149949','PDF-144174','PDF-182304','PDF-188964','PDF-188965',
                        'PDF-169973','PDF-184827','PDF-172363','PDF-145215','PDF-200807',
                        'PDF-161758','PDF-158920','PDF-195250','PDF-195251','PDF-195252',
                        'PDF-206259','PDF-206207','PDF-206273','PDF-206218','PDF-145572'));
INSERT IGNORE INTO ps_category_product (id_category, id_product, position)
SELECT @id_cat_corsets, id_product, 0 FROM ps_product
WHERE reference IN ('PDF-149949','PDF-144174','PDF-182304','PDF-188964','PDF-188965',
                    'PDF-169973','PDF-184827','PDF-172363','PDF-145215','PDF-200807',
                    'PDF-161758','PDF-158920','PDF-195250','PDF-195251','PDF-195252',
                    'PDF-206259','PDF-206207','PDF-206273','PDF-206218','PDF-145572');

-- ── Cat 5 : Nuisettes & Peignoirs → Nuisettes & Déshabillés ──────────────
UPDATE ps_product SET id_category_default=@id_cat_nuisettes
WHERE reference IN ('PDF-152079','PDF-199374','PDF-154833','PDF-182944','PDF-183055',
                    'PDF-182945','PDF-157931','PDF-228498','PDF-219070','PDF-206258');
UPDATE ps_product_shop SET id_category_default=@id_cat_nuisettes
WHERE id_shop=1 AND id_product IN (
    SELECT id_product FROM ps_product
    WHERE reference IN ('PDF-152079','PDF-199374','PDF-154833','PDF-182944','PDF-183055',
                        'PDF-182945','PDF-157931','PDF-228498','PDF-219070','PDF-206258'));
INSERT IGNORE INTO ps_category_product (id_category, id_product, position)
SELECT @id_cat_nuisettes, id_product, 0 FROM ps_product
WHERE reference IN ('PDF-152079','PDF-199374','PDF-154833','PDF-182944','PDF-183055',
                    'PDF-182945','PDF-157931','PDF-228498','PDF-219070','PDF-206258');

-- ── Cat 6 : Pyjamas → Pyjamas & Loungewear ───────────────────────────────
UPDATE ps_product SET id_category_default=@id_cat_pyjamas
WHERE reference IN ('PDF-223027','PDF-187096','PDF-196109','PDF-196111','PDF-196112',
                    'PDF-187521','PDF-213326','PDF-184831','PDF-221470','PDF-169495');
UPDATE ps_product_shop SET id_category_default=@id_cat_pyjamas
WHERE id_shop=1 AND id_product IN (
    SELECT id_product FROM ps_product
    WHERE reference IN ('PDF-223027','PDF-187096','PDF-196109','PDF-196111','PDF-196112',
                        'PDF-187521','PDF-213326','PDF-184831','PDF-221470','PDF-169495'));
INSERT IGNORE INTO ps_category_product (id_category, id_product, position)
SELECT @id_cat_pyjamas, id_product, 0 FROM ps_product
WHERE reference IN ('PDF-223027','PDF-187096','PDF-196109','PDF-196111','PDF-196112',
                    'PDF-187521','PDF-213326','PDF-184831','PDF-221470','PDF-169495');

-- ── Cat 7 : Culottes & Shortys → Corps & Désirs ──────────────────────────
UPDATE ps_product SET id_category_default=@id_cat_corps
WHERE reference IN ('PDF-174575','PDF-222340','PDF-222341','PDF-216104','PDF-198253',
                    'PDF-206641','PDF-212647','PDF-228908','PDF-226738','PDF-174576');
UPDATE ps_product_shop SET id_category_default=@id_cat_corps
WHERE id_shop=1 AND id_product IN (
    SELECT id_product FROM ps_product
    WHERE reference IN ('PDF-174575','PDF-222340','PDF-222341','PDF-216104','PDF-198253',
                        'PDF-206641','PDF-212647','PDF-228908','PDF-226738','PDF-174576'));
INSERT IGNORE INTO ps_category_product (id_category, id_product, position)
SELECT @id_cat_corps, id_product, 0 FROM ps_product
WHERE reference IN ('PDF-174575','PDF-222340','PDF-222341','PDF-216104','PDF-198253',
                    'PDF-206641','PDF-212647','PDF-228908','PDF-226738','PDF-174576');

-- ── Cat 8 : Bas & Collants ────────────────────────────────────────────────
UPDATE ps_product SET id_category_default=@id_cat_collants
WHERE reference IN ('PDF-34375','PDF-112522','PDF-206162','PDF-220367','PDF-150285',
                    'PDF-162774','PDF-140510','PDF-150276','PDF-206324','PDF-143715');
UPDATE ps_product_shop SET id_category_default=@id_cat_collants
WHERE id_shop=1 AND id_product IN (
    SELECT id_product FROM ps_product
    WHERE reference IN ('PDF-34375','PDF-112522','PDF-206162','PDF-220367','PDF-150285',
                        'PDF-162774','PDF-140510','PDF-150276','PDF-206324','PDF-143715'));
INSERT IGNORE INTO ps_category_product (id_category, id_product, position)
SELECT @id_cat_collants, id_product, 0 FROM ps_product
WHERE reference IN ('PDF-34375','PDF-112522','PDF-206162','PDF-220367','PDF-150285',
                    'PDF-162774','PDF-140510','PDF-150276','PDF-206324','PDF-143715');

-- ── Cat 9 : Robes → Robes & Tenues ───────────────────────────────────────
UPDATE ps_product SET id_category_default=@id_cat_robes
WHERE reference IN ('PDF-184600','PDF-187964','PDF-184598','PDF-184599',
                    'PDF-177888','PDF-179047','PDF-190992','PDF-152837',
                    'PDF-179048','PDF-190993');
UPDATE ps_product_shop SET id_category_default=@id_cat_robes
WHERE id_shop=1 AND id_product IN (
    SELECT id_product FROM ps_product
    WHERE reference IN ('PDF-184600','PDF-187964','PDF-184598','PDF-184599',
                        'PDF-177888','PDF-179047','PDF-190992','PDF-152837',
                        'PDF-179048','PDF-190993'));
INSERT IGNORE INTO ps_category_product (id_category, id_product, position)
SELECT @id_cat_robes, id_product, 0 FROM ps_product
WHERE reference IN ('PDF-184600','PDF-187964','PDF-184598','PDF-184599',
                    'PDF-177888','PDF-179047','PDF-190992','PDF-152837',
                    'PDF-179048','PDF-190993');

-- ── 4. Vider le cache PS (optionnel — si accès fichier serveur) ───────────
--  Sur le serveur : php bin/console cache:clear  OU  supprimer var/cache/*

-- ── 5. Contrôle final ─────────────────────────────────────────────────────
SELECT
    COUNT(*)                                              AS total_PDF,
    SUM(p.active)                                         AS actifs,
    SUM(CASE WHEN p.id_category_default > 0 THEN 1 END)  AS avec_categorie,
    SUM(CASE WHEN sa.quantity > 0 THEN 1 END)             AS en_stock
FROM ps_product p
LEFT JOIN ps_stock_available sa
       ON sa.id_product=p.id_product AND sa.id_product_attribute=0
WHERE p.reference LIKE 'PDF-%';
