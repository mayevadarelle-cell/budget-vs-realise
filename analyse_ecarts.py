#!/usr/bin/env python3
"""Décompose l'écart de marge budget vs réalisé en effets volume, prix et coût (données fictives).

Convention (écart favorable > 0) :
  effet volume = (vol_reel - vol_budget) x marge_unitaire_budget
  effet prix   = (prix_reel - prix_budget) x vol_reel
  effet coût   = (cout_budget - cout_reel) x vol_reel
La somme des trois effets égale l'écart total de marge ; un contrôle l'assert.
Sortie : data/ecarts_par_produit.csv (à importer dans Power BI / Excel).
"""
import csv
import os
from typing import Dict, List

HERE: str = os.path.dirname(os.path.abspath(__file__))
TOLERANCE: float = 0.01


def load_rows(path: str) -> List[Dict[str, float]]:
    with open(path, newline="", encoding="utf-8") as handle:
        return [{k: (v if k == "produit" else float(v)) for k, v in row.items()} for row in csv.DictReader(handle)]


def decompose(row: Dict[str, float]) -> Dict[str, float]:
    marge_unitaire_budget = row["prix_budget"] - row["cout_unitaire_budget"]
    marge_budget = row["volume_budget"] * marge_unitaire_budget
    marge_reelle = row["volume_reel"] * (row["prix_reel"] - row["cout_unitaire_reel"])
    effet_volume = (row["volume_reel"] - row["volume_budget"]) * marge_unitaire_budget
    effet_prix = (row["prix_reel"] - row["prix_budget"]) * row["volume_reel"]
    effet_cout = (row["cout_unitaire_budget"] - row["cout_unitaire_reel"]) * row["volume_reel"]
    assert abs((marge_reelle - marge_budget) - (effet_volume + effet_prix + effet_cout)) < TOLERANCE, "décomposition incohérente"
    return {"marge_budget": marge_budget, "marge_reelle": marge_reelle, "ecart_total": marge_reelle - marge_budget,
            "effet_volume": effet_volume, "effet_prix": effet_prix, "effet_cout": effet_cout}


def main() -> None:
    rows = load_rows(os.path.join(HERE, "data", "budget_vs_realise.csv"))
    results = [{"mois": int(r["mois"]), "produit": r["produit"], **{k: round(v, 2) for k, v in decompose(r).items()}} for r in rows]
    out = os.path.join(HERE, "data", "ecarts_par_produit.csv")
    with open(out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    for key in ("marge_budget", "marge_reelle", "ecart_total", "effet_volume", "effet_prix", "effet_cout"):
        print(f"{key:>13} : {sum(r[key] for r in results):>14,.0f} €")


if __name__ == "__main__":
    main()
