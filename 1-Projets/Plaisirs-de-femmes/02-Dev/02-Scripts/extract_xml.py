#!/usr/bin/env python3
# extract_xml.py
import xml.etree.ElementTree as ET
import csv, re

XML_FILE = "products_ver2__sizesFR.xml"
OUT_CSV  = "catalogue_complet.csv"
REF_PREFIX = "MH"

def prose_seule(html):
    html = re.split(r"<div class=['\"]prod_data", html, 1)[0]  # coupe le tableau des tailles
    html = re.split(r"<table", html, 1)[0]                      # filet de sécurité
    return re.sub(r"\s+", " ", html).strip()

with open(OUT_CSV, "w", newline="", encoding="utf-8") as out:
    w = csv.writer(out)
    w.writerow(["reference", "nom", "couleur", "type", "texte_source"])
    n = 0
    for _, el in ET.iterparse(XML_FILE, events=("end",)):
        if el.tag != "product":
            continue
        pid = el.get("id")                          # <-- l'id est un ATTRIBUT
        desc_el = el.find("description")
        if pid and desc_el is not None and (desc_el.text or "").strip():
            w.writerow([
                REF_PREFIX + pid,
                (el.findtext("name")  or "").strip(),
                (el.findtext("color") or "").strip(),
                (el.findtext("type")  or "").strip(),
                prose_seule(desc_el.text),
            ])
            n += 1
        el.clear()                                  # libère la mémoire sur 200 Mo
    print(f"{n} fiches extraites -> {OUT_CSV}")