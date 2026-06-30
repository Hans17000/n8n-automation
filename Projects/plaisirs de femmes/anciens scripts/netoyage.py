import re
import sys
import os
import pandas as pd

def fix_line(fields, num_columns, desc_index):
    if len(fields) == num_columns:
        return fields
    if len(fields) > num_columns:
        extra = len(fields) - num_columns
        before = fields[:desc_index]
        desc = ','.join(fields[desc_index:desc_index + extra + 1])
        after = fields[desc_index + extra + 1:]
        return before + [desc] + after
    return fields

def clean_html(text):
    if not isinstance(text, str):
        return text
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('\t', ' ')
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n ', '\n', text)
    text = text.strip()
    return text

def fix_encoding(text):
    if not isinstance(text, str):
        return text
    replacements = {
        'Pi?ces': 'Pièces',
        'pi?ces': 'pièces',
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

def nettoyer(input_file, output_file=None, desc_column='description'):
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_nettoyes{ext}"

    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        header = f.readline().rstrip('\n').split(';')
        num_columns = len(header)

        if desc_column not in header:
            print(f"ERREUR: colonne '{desc_column}' introuvable. Colonnes disponibles :")
            print(', '.join(header))
            sys.exit(1)

        desc_index = header.index(desc_column)
        print(f"Fichier : {input_file}")
        print(f"Colonnes detectees : {num_columns}")
        print(f"Colonne description : '{desc_column}' (index {desc_index})")

        for line_num, line in enumerate(f, start=2):
            line = line.rstrip('\n')
            if not line:
                continue
            fields = line.split(';')
            fields = fix_line(fields, num_columns, desc_index)
            if len(fields) != num_columns:
                print(f"  ATTENTION ligne {line_num}: {len(fields)} champs (non corrigeable)")
                continue
            rows.append(fields)

    df = pd.DataFrame(rows, columns=header)
    print(f"Lignes chargees : {len(df)}")

    df[desc_column] = df[desc_column].apply(clean_html)
    df[desc_column] = df[desc_column].apply(lambda t: t.replace(';', ',') if isinstance(t, str) else t)
    df[desc_column] = df[desc_column].apply(lambda t: t.replace('""', '"') if isinstance(t, str) else t)

    if 'path' in df.columns:
        df['path'] = df['path'].apply(fix_encoding)

    df.to_csv(output_file, sep=';', index=False, lineterminator='\n')

    remaining_html = df[desc_column].apply(lambda t: bool(re.search(r'<[^>]+>', t)) if isinstance(t, str) else False).sum()
    remaining_semicolons = df[desc_column].apply(lambda t: t.count(';') if isinstance(t, str) else 0).sum()
    print(f"\n--- Controle qualite ---")
    print(f"  HTML residuel : {remaining_html}")
    print(f"  Point-virgules restants : {remaining_semicolons}")
    print(f"\n[OK] -> {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python netoyage.py <fichier.csv> [fichier_sortie.csv] [nom_colonne_description]")
        print("  fichier_sortie.csv    : optionnel, defaut = <fichier>_nettoyes.csv")
        print("  nom_colonne_description : optionnel, defaut = 'description'")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    desc_col = sys.argv[3] if len(sys.argv) > 3 else 'description'

    nettoyer(input_file, output_file, desc_col)
