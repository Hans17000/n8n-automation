---
name: refresh-tableau-de-bord-placements
description: Rafraîchit le tableau de bord des placements chaque samedi matin (cours Yahoo Finance frais).
---

Rafraîchis le tableau de bord des placements pour Omar.

**Étapes à exécuter :**

1. Lance le script de récupération des cours :
   `cd /sessions/serene-intelligent-newton/mnt/outputs && python3 fetch_v3.py`
   
   Ce script tire 5 ans d'historique depuis Yahoo Finance pour les positions de Omar : AUM5.DE (Amundi S&P 500 Swap), SXRV.DE (iShares Nasdaq 100), BTC-EUR, USDT-EUR, MYST-USD, plus le benchmark CW8.PA (MSCI World) et la paire EURUSD=X.

2. Reconstruis le classeur Excel :
   `cd /sessions/serene-intelligent-newton/mnt/outputs && python3 build_v2.py`

3. Recalcule les formules pour zéro erreur :
   `python3 /sessions/serene-intelligent-newton/mnt/.claude/skills/xlsx/scripts/recalc.py /sessions/serene-intelligent-newton/mnt/outputs/tableau_de_bord_placements.xlsx`

4. Copie le fichier final vers le dossier de l'utilisateur :
   `cp /sessions/serene-intelligent-newton/mnt/outputs/tableau_de_bord_placements.xlsx /sessions/serene-intelligent-newton/mnt/Placements/tableau_de_bord_placements_allege.xlsx`
   
   Si la copie échoue avec « Permission denied », c'est que le fichier est ouvert dans Excel. Dans ce cas, ajoute la date dans le nom : `tableau_de_bord_placements_YYYY-MM-DD.xlsx`.

5. **Reporte brièvement à Omar** dans le ton littéraire qu'il préfère (français narratif classique, phrases élaborées, ironie discrète, pas de listes à puces sauf si vraiment nécessaire) :
   - La nouvelle valeur totale du portefeuille
   - La performance globale (P&L EUR et %)
   - Le delta vs MSCI World (alpha)
   - Une remarque ou observation pertinente s'il y a un mouvement notable (>+5% ou <-5% sur la semaine, ou un événement dans la composition)
   - Un lien `computer://` vers le fichier mis à jour

**Si tout va bien, sois bref** — Omar a demandé un rafraîchissement hebdomadaire, pas un commentaire de marché long. Trois paragraphes courts suffisent.

**Si une erreur survient** (ticker délisté, API en panne, etc.), explique-la calmement et propose une action corrective. Ne paniquez pas l'utilisateur.