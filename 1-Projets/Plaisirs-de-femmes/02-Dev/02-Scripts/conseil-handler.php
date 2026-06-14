<?php
/**
 * ============================================================
 *  PLAISIRS DE FEMMES — Traitant du formulaire « Demander conseil »
 *  ------------------------------------------------------------
 *  Fichier : conseil-handler.php
 *  À DÉPOSER PAR FTP À LA RACINE DU SITE (à côté de index.php).
 *
 *  Rôle : reçoit le formulaire, le valide, le nettoie, et envoie
 *  chaque message à contact@plaisirs-de-femmes.fr.
 *
 *  >>> À PERSONNALISER (2 lignes ci-dessous) <<<
 *   - $page_retour : remplace XX par l'id réel de ta page CMS
 *     « Demander conseil » (ex. /content/15-demander-conseil).
 *   - $expediteur : laisse une adresse DE TON DOMAINE (important
 *     pour que le mail ne parte pas en spam — voir note en bas).
 * ============================================================
 */

// --- Réglages ---------------------------------------------------
$destinataire = 'contact@plaisirs-de-femmes.fr';
$expediteur   = 'contact@plaisirs-de-femmes.fr';     // adresse de TON domaine
$page_retour  = '/content/18-contact';        // <-- mets l'id réel

// --- Petites fonctions de sécurité ------------------------------
function pdf_clean($v)   { return trim(strip_tags((string)$v)); }
// supprime retours-chariot & sauts de ligne : empêche l'injection d'en-têtes mail
function pdf_noeol($v)   { return str_replace(array("\r", "\n", "%0a", "%0d", "%0A", "%0D"), '', (string)$v); }
function pdf_back($ok)   { global $page_retour; header('Location: '.$page_retour.'?ok='.($ok ? '1' : '0')); exit; }

// --- 1. Honeypot : si le champ piège est rempli, c'est un robot -
if (!empty($_POST['website'])) { pdf_back(true); } // on fait mine d'accepter, sans rien envoyer

// --- 2. On n'accepte que le POST -------------------------------
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { pdf_back(false); }

// --- 3. Récupération & nettoyage -------------------------------
$prenom  = pdf_clean($_POST['prenom']  ?? '');
$email   = pdf_noeol(pdf_clean($_POST['email'] ?? ''));
$objet   = pdf_noeol(pdf_clean($_POST['objet'] ?? ''));
$message = pdf_clean($_POST['message'] ?? '');

// --- 4. Validation ---------------------------------------------
if ($prenom === '' || !filter_var($email, FILTER_VALIDATE_EMAIL) || $message === '') {
    pdf_back(false);
}
// garde-fous de longueur (anti-abus)
if (mb_strlen($prenom) > 80 || mb_strlen($message) > 5000) { pdf_back(false); }

// --- 5. Construction du courriel -------------------------------
$sujet = 'Demande de conseil — '.($objet !== '' ? $objet : 'sans objet');
$corps =
    "Nouveau message depuis la page Conseil\n".
    "----------------------------------------\n".
    "Prénom  : ".$prenom."\n".
    "E-mail  : ".$email."\n".
    "Objet   : ".$objet."\n\n".
    "Message :\n".$message."\n";

// En-têtes : From sur ton domaine, Reply-To sur la cliente (tu réponds en un clic)
$entetes  = 'From: Plaisirs de Femmes <'.$expediteur.'>'."\r\n";
$entetes .= 'Reply-To: '.pdf_noeol($prenom).' <'.$email.'>'."\r\n";
$entetes .= 'Content-Type: text/plain; charset=UTF-8'."\r\n";
$entetes .= 'X-Mailer: PHP/PdF-Conseil'."\r\n";

// sujet encodé UTF-8 (accents)
$sujet_enc = '=?UTF-8?B?'.base64_encode($sujet).'?=';

// --- 6. Envoi ---------------------------------------------------
$envoye = @mail($destinataire, $sujet_enc, $corps, $entetes);

pdf_back($envoye);

/* ============================================================
 * NOTE DÉLIVRABILITÉ (à lire une fois) :
 * La fonction mail() de PHP fonctionne, mais selon l'hébergeur,
 * le message peut tomber dans les indésirables si ton domaine
 * n'a pas d'enregistrements SPF/DKIM corrects. Deux remèdes :
 *   1) Vérifier/ajouter SPF + DKIM pour plaisirs-de-femmes.fr
 *      (côté DNS de ton hébergeur) — recommandé de toute façon.
 *   2) Si besoin, je te fournis une variante qui envoie via SMTP
 *      (PHPMailer) avec tes identifiants de messagerie — à ne
 *      jamais mettre en clair ailleurs que dans ce fichier serveur.
 * ============================================================ */
