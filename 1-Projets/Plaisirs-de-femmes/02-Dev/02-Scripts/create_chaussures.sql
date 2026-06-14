-- ============================================================
-- Création univers Chaussures + 10 sous-catégories
-- PrestaShop 8.2.6 — préfixe ps_ — id_shop 1 — id_lang 1 (fr)
-- À exécuter dans phpMyAdmin
-- ============================================================

-- 1. Univers parent : Chaussures (ID 71)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (71, 2, 1, 2, 0, 0, 1, NOW(), NOW(), 7, 0);

INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (71, 1, 1, 'Chaussures', 'L''univers chaussures — des escarpins aux sneakers, chaque pas compte.', '', 'chaussures', 'Chaussures Femme', 'chaussures,femme,escarpins,bottes,sandales', 'Collection chaussures femme — escarpins, bottes, sandales, ballerines et sneakers.');

INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`)
VALUES (71, 1, 7);

-- 2. Sous-catégories (IDs 72–81)

-- Bottes & Boots (72)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (72, 71, 1, 3, 0, 0, 1, NOW(), NOW(), 0, 0);
INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (72, 1, 1, 'Bottes & Boots', 'Du cuir souple aux finitions travaillées, des bottes et boots qui traversent les saisons avec caractère.', '', 'bottes-boots', 'Bottes & Boots Femme | Plaisirs de Femmes', 'bottes femme,boots femme,bottes cuir,bottines', 'Bottes et boots femme en cuir et daim. Bottines, boots plates et à talons pour toutes les saisons.');
INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`) VALUES (72, 1, 0);

-- Cuissardes (73)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (73, 71, 1, 3, 0, 0, 1, NOW(), NOW(), 1, 0);
INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (73, 1, 1, 'Cuissardes', 'La cuissarde affirme une silhouette. Au-dessus du genou, elle redessine la jambe avec une assurance tranquille.', '', 'cuissardes', 'Cuissardes Femme | Plaisirs de Femmes', 'cuissardes femme,bottes hautes,cuissardes talon', 'Cuissardes femme — bottes hautes au-dessus du genou, en cuir, daim et stretch.');
INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`) VALUES (73, 1, 1);

-- Sandales & Mules (74)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (74, 71, 1, 3, 0, 0, 1, NOW(), NOW(), 2, 0);
INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (74, 1, 1, 'Sandales & Mules', 'Pieds libres, pas légers. Sandales à brides et mules ouvertes pour les journées où la chaleur dicte sa loi.', '', 'sandales-mules', 'Sandales & Mules Femme | Plaisirs de Femmes', 'sandales femme,mules femme,sandales été,sandales plates', 'Sandales et mules femme — plates, à talons ou compensées pour l''été et les beaux jours.');
INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`) VALUES (74, 1, 2);

-- Sneakers (75)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (75, 71, 1, 3, 0, 0, 1, NOW(), NOW(), 3, 0);
INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (75, 1, 1, 'Sneakers', 'Le confort sans concession. Des sneakers qui se portent du matin au soir, de la ville au week-end.', '', 'sneakers', 'Sneakers Femme | Plaisirs de Femmes', 'sneakers femme,baskets femme,chaussures sport femme', 'Sneakers et baskets femme — chaussures de sport et lifestyle pour un confort quotidien.');
INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`) VALUES (75, 1, 3);

-- Mocassins & Lords (76)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (76, 71, 1, 3, 0, 0, 1, NOW(), NOW(), 4, 0);
INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (76, 1, 1, 'Mocassins & Lords', 'L''élégance empruntée au vestiaire masculin. Mocassins et lords en cuir, portés pieds nus ou avec des chaussettes invisibles.', '', 'mocassins-lords', 'Mocassins & Lords Femme | Plaisirs de Femmes', 'mocassins femme,loafers femme,chaussures cuir femme', 'Mocassins et lords femme en cuir — loafers classiques et revisités pour un style affirmé.');
INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`) VALUES (76, 1, 4);

-- Ballerines (77)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (77, 71, 1, 3, 0, 0, 1, NOW(), NOW(), 5, 0);
INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (77, 1, 1, 'Ballerines', 'La grâce à fleur de sol. Ballerines plates et souples, du classique uni au modèle orné.', '', 'ballerines', 'Ballerines Femme | Plaisirs de Femmes', 'ballerines femme,ballerines plates,ballerines cuir', 'Ballerines femme — chaussures plates en cuir, daim et tissu pour un confort féminin au quotidien.');
INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`) VALUES (77, 1, 5);

-- Chaussons (78)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (78, 71, 1, 3, 0, 0, 1, NOW(), NOW(), 6, 0);
INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (78, 1, 1, 'Chaussons', 'Le luxe discret de rentrer chez soi. Chaussons doublés, mules d''intérieur et pantoufles soignées.', '', 'chaussons', 'Chaussons Femme | Plaisirs de Femmes', 'chaussons femme,pantoufles femme,mules intérieur', 'Chaussons et pantoufles femme — mules d''intérieur doublées et confortables pour la maison.');
INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`) VALUES (78, 1, 6);

-- Escarpins (79)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (79, 71, 1, 3, 0, 0, 1, NOW(), NOW(), 7, 0);
INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (79, 1, 1, 'Escarpins', 'Le classique absolu. Escarpins à bout pointu ou rond, talon moyen, pour les occasions qui comptent.', '', 'escarpins', 'Escarpins Femme | Plaisirs de Femmes', 'escarpins femme,escarpins talon,chaussures habillées', 'Escarpins femme — chaussures à talons classiques et élégantes pour toutes les occasions.');
INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`) VALUES (79, 1, 7);

-- Talons Aiguilles (80)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (80, 71, 1, 3, 0, 0, 1, NOW(), NOW(), 8, 0);
INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (80, 1, 1, 'Talons Aiguilles', 'La verticale assumée. Talons fins et hauts perchés pour les soirées où l''on ne fait pas les choses à moitié.', '', 'talons-aiguilles', 'Talons Aiguilles Femme | Plaisirs de Femmes', 'talons aiguilles,stilettos femme,escarpins hauts', 'Talons aiguilles et stilettos femme — escarpins à talons fins et hauts pour les grandes occasions.');
INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`) VALUES (80, 1, 8);

-- Talons Bloc (81)
INSERT INTO `ps_category` (`id_category`, `id_parent`, `id_shop_default`, `level_depth`, `nleft`, `nright`, `active`, `date_add`, `date_upd`, `position`, `is_root_category`)
VALUES (81, 71, 1, 3, 0, 0, 1, NOW(), NOW(), 9, 0);
INSERT INTO `ps_category_lang` (`id_category`, `id_shop`, `id_lang`, `name`, `description`, `additional_description`, `link_rewrite`, `meta_title`, `meta_keywords`, `meta_description`)
VALUES (81, 1, 1, 'Talons Bloc', 'La hauteur sans le vertige. Talons larges et stables, pour celles qui veulent l''allure sans sacrifier la marche.', '', 'talons-bloc', 'Talons Bloc Femme | Plaisirs de Femmes', 'talons bloc femme,escarpins talon large,chaussures talon stable', 'Talons bloc femme — escarpins et sandales à talon large et stable, confort et élégance.');
INSERT INTO `ps_category_shop` (`id_category`, `id_shop`, `position`) VALUES (81, 1, 9);

-- 3. Vider le cache PS après exécution :
-- Backoffice → Paramètres avancés → Performance → Vider le cache
