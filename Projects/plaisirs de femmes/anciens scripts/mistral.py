#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# generer_descriptions.py — réécrit en français les descriptions via Mistral (LM Studio)
import csv, json, time, os, sys, requests

# --- Configuration ---
API_URL    = "http://localhost:1234/v1/chat/completions"
INPUT_CSV  = "produits_a_decrire.csv"   # colonnes : reference, nom, couleur, composition, texte_source
OUTPUT_CSV = "descriptions.csv"         # colonnes produites : reference, description_courte, description_longue
TEMPERATURE = 0.7
PAUSE = 0.3
LIMIT = 20      # PILOTE : s'arrête après 20 fiches. Mettre 0 pour tout traiter.

SYSTEM_PROMPT = """Tu es rédacteur pour une maison de lingerie et d'art de vivre intime haut de gamme.
On te fournit la description d'un fournisseur en anglais, plus des attributs vérifiés
(coloris, composition). Ta mission : produire une description EN FRANÇAIS, dans la
voix de la maison — sensuelle, raffinée, tout en délicatesse.

Règles :
- Traduis ET réécris : le résultat est un texte français original, pas une traduction
  littérale. Aucune phrase ne calque la source (essentiel pour l'unicité Google).
- Fidélité stricte aux faits : matières, coloris, coupe, détails. N'invente aucun
  matériau, couleur ou caractéristique absent de la source ou des attributs.
- Intègre naturellement le coloris et la composition fournis.
- Casse de phrase française, pas de superlatifs creux, pas de vulgarité :
  la suggestion plutôt que la démonstration.
- Ignore toute donnée de taille ou tableau de mesures.
- description_courte : 1 à 2 phrases, max 160 caractères, sans HTML.
- description_longue : 3 à 5 phrases, 60 à 110 mots, HTML simple (<p>, <strong>).

Réponds STRICTEMENT en JSON, sans texte autour :
{"description_courte": "...", "description_longue": "..."}"""


def get_model_id():
    try:
        r = requests.get("http://localhost:1234/v1/models", timeout=10)
        return r.json()["data"][0]["id"]
    except Exception:
        return "local-model"


def construire_message(row):
    parts = [f"Description (EN) : {row.get('texte_source', '').strip()}"]
    if row.get("couleur"):     parts.append(f"Coloris : {row['couleur'].strip()}")
    if row.get("composition"): parts.append(f"Composition : {row['composition'].strip()}")
    return "\n".join(parts)


def generer(model_id, contenu):
    payload = {
        "model": model_id,
        "temperature": TEMPERATURE,
        "max_tokens": 400,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": contenu},
        ],
    }
    r = requests.post(API_URL, json=payload, timeout=120)
    r.raise_for_status()
    txt = r.json()["choices"][0]["message"]["content"].strip()
    d, f = txt.find("{"), txt.rfind("}")
    if d == -1 or f == -1:
        raise ValueError(f"Pas de JSON : {txt[:120]}")
    data = json.loads(txt[d:f + 1])
    courte = data["description_courte"].strip()[:250]   # garde-fou longueur
    return courte, data["description_longue"].strip()


def deja_traites():
    faits = set()
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                faits.add(row["reference"])
    return faits


def main():
    model_id = get_model_id()
    print(f"Modèle : {model_id}")
    faits = deja_traites()

    with open(INPUT_CSV, encoding="utf-8") as f:
        produits = list(csv.DictReader(f))

    nouveau = not os.path.exists(OUTPUT_CSV)
    traites = 0
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        if nouveau:
            w.writerow(["reference", "description_courte", "description_longue"])
        for i, row in enumerate(produits, 1):
            ref = (row.get("reference") or "").strip()
            if not ref or ref in faits:
                continue
            try:
                courte, longue = generer(model_id, construire_message(row))
                w.writerow([ref, courte, longue])
                out.flush()
                traites += 1
                print(f"[{i}/{len(produits)}] {ref} ✓")
            except Exception as e:
                print(f"[{i}/{len(produits)}] {ref} ✗ — {e}", file=sys.stderr)
            time.sleep(PAUSE)
            if LIMIT and traites >= LIMIT:
                print(f"== Pilote : {LIMIT} fiches, arrêt ==")
                break
    print("Terminé.")


if __name__ == "__main__":
    main()