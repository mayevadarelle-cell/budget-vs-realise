#!/usr/bin/env python3
"""Génère un jeu de données FICTIF (budget vs réalisé 2025) pour une PME imaginaire.

Aucune donnée réelle : l'entreprise « Atelier Démo SAS » est inventée. Graine fixe => résultat reproductible.
Sortie : data/budget_vs_realise.csv (une ligne par mois x produit).
"""
import csv
import os
import random
from typing import Dict, List

HERE: str = os.path.dirname(os.path.abspath(__file__))
SEED: int = 2026
MONTHS: int = 12
PRODUCTS: Dict[str, Dict[str, float]] = {
    "Gamme Pro": {"prix": 120.0, "volume": 800, "cout_unitaire": 70.0},
    "Gamme Standard": {"prix": 60.0, "volume": 2000, "cout_unitaire": 38.0},
    "Services": {"prix": 90.0, "volume": 500, "cout_unitaire": 55.0},
}
PRICE_NOISE: float = 0.05
VOLUME_NOISE: float = 0.12
COST_NOISE: float = 0.06
SEASONALITY: List[float] = [0.9, 0.9, 1.0, 1.0, 1.05, 1.05, 0.9, 0.8, 1.1, 1.1, 1.15, 1.2]


def main() -> None:
    rng = random.Random(SEED)
    rows: List[Dict[str, object]] = []
    for month in range(1, MONTHS + 1):
        for name, base in PRODUCTS.items():
            volume_budget = round(base["volume"] * SEASONALITY[month - 1])
            volume_reel = round(volume_budget * (1 + rng.uniform(-VOLUME_NOISE, VOLUME_NOISE)))
            prix_reel = round(base["prix"] * (1 + rng.uniform(-PRICE_NOISE, PRICE_NOISE)), 2)
            cout_reel = round(base["cout_unitaire"] * (1 + rng.uniform(-COST_NOISE, COST_NOISE)), 2)
            rows.append({
                "mois": month, "produit": name,
                "volume_budget": volume_budget, "prix_budget": base["prix"], "cout_unitaire_budget": base["cout_unitaire"],
                "volume_reel": volume_reel, "prix_reel": prix_reel, "cout_unitaire_reel": cout_reel,
            })
    out = os.path.join(HERE, "data", "budget_vs_realise.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} lignes écrites dans {out}")


if __name__ == "__main__":
    main()
