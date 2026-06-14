#!/usr/bin/env python3
"""
generer_descriptions.py — Génération automatique des descriptions produit
via LM Studio (API compatible OpenAI) et Gemma 4.

Usage :
    python generer_descriptions.py fichier_descriptions.csv

Options :
    --port PORT        Port LM Studio (défaut : 1234)
    --output FICHIER   CSV de sortie (défaut : *_avec_descriptions.csv)
    --resume           Reprendre là où on s'est arrêté (skip les produits déjà traités)
    --delay SECONDES   Pause entre chaque appel (défaut : 1)

Le script lit le CSV généré par top10_xml.py (colonnes : Reference, Nom commercial,
Type, Couleur, Marque, Composition, Description fournisseur) et appelle LM Studio
produit par produit pour générer [COURTE] et [LONGUE].

Sortie : CSV avec colonnes Reference, Nom commercial, Description courte, Description longue.
"""

import csv
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error


# ── Configuration ────────────────────────────────────────────────────────────

DEFAULT_PORT = 1234
DEFAULT_DELAY = 1  # secondes entre chaque appel
MAX_RETRIES = 3
RETRY_DELAY = 5

SYSTEM_PROMPT = "Tu es rédactrice pour une boutique de lingerie et mode féminine haut de gamme. Tu écris avec élégance mais de façon concrète et accessible. Pas de métaphores excessives, pas de prose trop romanesque. Le ton est chic et sensuel, comme un magazine de mode haut de gamme."

USER_TEMPLATE = """Voici deux exemples :

Produit : Soutien-Gorge Push-Up en Dentelle Noir
[COURTE]
Dentelle fine sur peau nue, galbe naturel rehaussé sans en faire trop. Le genre de push-up que l'on porte pour soi.
[LONGUE]
La dentelle noire dessine un décolleté subtil, de ceux que l'on devine sans les exposer. Les armatures maintiennent avec fermeté, les coussinets amovibles permettent de doser l'effet selon l'envie du jour. Le nœud de satin au centre apporte une touche de féminité assumée. C'est une pièce pensée pour le quotidien autant que pour les soirs où l'on choisit ses dessous avec intention.

Produit : Ballerines en Daim Beige
[COURTE]
Du daim souple, une ligne épurée, et cette sensation d'enfiler quelque chose qui va de soi. L'élégance au naturel.
[LONGUE]
Le daim beige épouse le pied avec cette souplesse que seules les matières nobles savent donner. La bride sur le cou-de-pied assure le maintien sans serrer, la pointe légèrement allongée affine la silhouette. On les associe à une robe fluide comme à un jean brut, et le résultat reste le même : une allure nette, sans effort apparent. Le genre de ballerines que l'on cherche longtemps et que l'on ne quitte plus.

Maintenant écris [COURTE] et [LONGUE] pour ce produit.
IMPORTANT : [COURTE] = 2 phrases seulement. [LONGUE] = 4 à 6 phrases seulement, un seul paragraphe.
Ton chic et sensuel, concret, comme un magazine de mode. Pas de métaphores excessives. Interdits : "parfait", "idéal", "offrir", "sublimer", "mettre en valeur", listes à puces, émojis. Ne mentionne pas la marque.

Produit : {nom}
Couleur : {couleur}
Matière : {composition}
Détails : {description}

[COURTE]"""


# ── Appel API LM Studio ─────────────────────────────────────────────────────

def appeler_lmstudio(prompt_user, port=DEFAULT_PORT, retries=MAX_RETRIES):
    """Appelle l'API LM Studio et retourne la réponse texte."""
    url = f"http://localhost:{port}/v1/chat/completions"
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_user},
        ],
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 512,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.3,
        "stream": False,
    }

    data = json.dumps(payload).encode('utf-8')

    for tentative in range(retries):
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=600) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError) as e:
            print(f"    ⚠ Tentative {tentative + 1}/{retries} échouée : {e}")
            if tentative < retries - 1:
                time.sleep(RETRY_DELAY)
            else:
                return None


def parser_reponse(texte):
    """Extrait [COURTE] et [LONGUE] de la réponse Gemma."""
    courte = ''
    longue = ''

    if not texte:
        return courte, longue

    # Stratégie 1 : markers explicites [COURTE]/[LONGUE] ou **Courte**/**Longue**
    pat_courte = r'(?:\[COURTE\]|\*{0,2}Courte\s*:?\*{0,2})\s*\n?(.*?)(?=\[LONGUE\]|\*{0,2}Longue\s*:?\*{0,2}|---|\Z)'
    pat_longue = r'(?:\[LONGUE\]|\*{0,2}Longue\s*:?\*{0,2})\s*\n?(.*?)(?=\[COURTE\]|\*{0,2}Courte\s*:?\*{0,2}|\Z)'

    match_courte = re.search(pat_courte, texte, re.DOTALL | re.IGNORECASE)
    match_longue = re.search(pat_longue, texte, re.DOTALL | re.IGNORECASE)

    # Stratégie 2 : si pas trouvé, chercher le pattern Mistral — **Titre** puis blocs *texte* séparés par ---
    if not match_courte or not match_longue or (not match_courte.group(1).strip() and not match_longue.group(1).strip()):
        # Extraire tous les blocs de texte entre astérisques ou après ---
        blocs = re.split(r'\n---\n|\n-{3,}\n', texte)
        if len(blocs) >= 2:
            # Premier bloc = courte, deuxième = longue
            b1 = re.sub(r'\*{1,2}[^*]+\*{1,2}\s*\n', '', blocs[0], count=1)  # retirer le titre **...**
            b2 = re.sub(r'\*{1,2}[^*]+\*{1,2}\s*\n', '', blocs[1], count=1)
            courte = re.sub(r'^\*|\*$', '', b1.strip()).strip()
            longue = re.sub(r'^\*|\*$', '', b2.strip()).strip()
            return courte, longue
        elif len(blocs) == 1:
            # Pas de ---, chercher deux paragraphes séparés par double saut de ligne
            paragraphes = [p.strip() for p in re.split(r'\n\s*\n', texte) if p.strip() and not p.strip().startswith('**')]
            if len(paragraphes) >= 2:
                courte = re.sub(r'\*+', '', paragraphes[0]).strip()
                longue = re.sub(r'\*+', '', '\n'.join(paragraphes[1:])).strip()
                return courte, longue

    if match_courte:
        courte = match_courte.group(1).strip()
    if match_longue:
        longue = match_longue.group(1).strip()

    # Nettoyer les astérisques, puces et formatage markdown parasite
    for char in ['*', '•', '–']:
        courte = courte.strip(char).strip()
        longue = longue.strip(char).strip()
    courte = re.sub(r'\*+', '', courte).strip()
    longue = re.sub(r'\*+', '', longue).strip()

    # Tronquer proprement au dernier point si trop long
    if len(courte) > 300:
        coupe = courte[:300].rsplit('.', 1)
        courte = coupe[0] + '.' if len(coupe) > 1 else courte[:297] + '…'
    if len(longue) > 800:
        coupe = longue[:800].rsplit('.', 1)
        longue = coupe[0] + '.' if len(coupe) > 1 else longue[:797] + '…'

    return courte, longue


# ── Pipeline principal ───────────────────────────────────────────────────────

def run(csv_input, port=DEFAULT_PORT, output=None, resume=False, delay=DEFAULT_DELAY):
    if not output:
        base = os.path.splitext(csv_input)[0]
        output = base + '_avec_descriptions.csv'

    # Charger les produits
    produits = []
    with open(csv_input, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            produits.append(row)

    print(f"\n📂 Source : {csv_input}")
    print(f"📝 Produits à traiter : {len(produits)}")
    print(f"🔌 LM Studio : localhost:{port}")

    # Mode reprise : charger les références déjà traitées
    deja_traites = set()
    if resume and os.path.exists(output):
        with open(output, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                deja_traites.add(row.get('Reference', ''))
        print(f"🔄 Reprise : {len(deja_traites)} produits déjà traités, on continue")

    # Ouvrir le fichier de sortie
    mode = 'a' if resume and deja_traites else 'w'
    OUT_HEADER = ['Reference', 'Nom commercial', 'Description courte', 'Description longue']

    with open(output, mode, encoding='utf-8-sig', newline='') as fout:
        writer = csv.writer(fout, delimiter=';', quoting=csv.QUOTE_ALL)
        if mode == 'w':
            writer.writerow(OUT_HEADER)

        traites = 0
        erreurs = 0

        for i, p in enumerate(produits):
            ref = p.get('Reference', '')

            if ref in deja_traites:
                continue

            nom = p.get('Nom commercial', '')
            print(f"\n  [{i + 1}/{len(produits)}] {ref} — {nom}")

            # Construire le prompt
            prompt = USER_TEMPLATE.format(
                nom=nom,
                type=p.get('Type', ''),
                couleur=p.get('Couleur', ''),
                marque=p.get('Marque', ''),
                composition=p.get('Composition', '') or 'Non disponible',
                description=p.get('Description fournisseur', ''),
            )

            # Appeler LM Studio
            t0 = time.time()
            reponse = appeler_lmstudio(prompt, port=port)
            duree = time.time() - t0

            if reponse:
                courte, longue = parser_reponse(reponse)
                if courte or longue:
                    writer.writerow([ref, nom, courte, longue])
                    fout.flush()  # Écrire immédiatement en cas de crash
                    traites += 1
                    print(f"    ✅ OK ({len(courte)} + {len(longue)} car.) — {duree:.0f}s")
                else:
                    writer.writerow([ref, nom, '', ''])
                    fout.flush()
                    erreurs += 1
                    print(f"    ❌ Parsing échoué — réponse brute sauvée dans le log")
                    # Log de debug
                    with open(output + '.log', 'a', encoding='utf-8') as flog:
                        flog.write(f"\n{'='*60}\n{ref} — {nom}\n{reponse}\n")
            else:
                writer.writerow([ref, nom, '', ''])
                fout.flush()
                erreurs += 1
                print(f"    ❌ Pas de réponse de LM Studio ({duree:.0f}s)")

            # Pause entre les appels
            if delay > 0 and i < len(produits) - 1:
                time.sleep(delay)

    print(f"\n{'─' * 60}")
    print(f"  ✅ Traités : {traites}")
    print(f"  ❌ Erreurs : {erreurs}")
    print(f"  📝 Fichier : {output}")

    if erreurs > 0:
        print(f"\n  💡 Relancer avec --resume pour retraiter les erreurs")

    return output


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    port = DEFAULT_PORT
    output = None
    resume = False
    delay = DEFAULT_DELAY
    positional = []

    i = 0
    while i < len(args):
        if args[i] == '--port' and i + 1 < len(args):
            port = int(args[i + 1]); i += 2
        elif args[i] == '--output' and i + 1 < len(args):
            output = args[i + 1]; i += 2
        elif args[i] == '--delay' and i + 1 < len(args):
            delay = float(args[i + 1]); i += 2
        elif args[i] == '--resume':
            resume = True; i += 1
        else:
            positional.append(args[i]); i += 1

    source = positional[0]
    if not os.path.exists(source):
        print(f"ERREUR : fichier introuvable → {source}")
        sys.exit(1)

    run(source, port=port, output=output, resume=resume, delay=delay)
