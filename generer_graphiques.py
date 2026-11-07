#!/usr/bin/env python3
"""Trace trois graphiques à partir de data/ecarts_par_produit.csv (données fictives).

Sorties dans captures/ :
  cascade_effets.png     : décomposition de l'écart annuel de marge (volume, prix, coût, total)
  ecarts_mensuels.png    : effets par mois, avec l'écart total en trait
  ecart_par_produit.png  : effets par produit

Convention : un écart favorable est positif.
"""
import csv
import os
from collections import defaultdict
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE: str = os.path.dirname(os.path.abspath(__file__))
EFFETS: List[str] = ["effet_volume", "effet_prix", "effet_cout"]
LIBELLES: Dict[str, str] = {"effet_volume": "Volume", "effet_prix": "Prix", "effet_cout": "Coût"}
COULEURS: Dict[str, str] = {"effet_volume": "#2F5D8A", "effet_prix": "#D98324", "effet_cout": "#4C8C6B"}
MOIS: List[str] = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]


def charger(path: str) -> List[Dict[str, float]]:
    with open(path, newline="", encoding="utf-8") as handle:
        return [{k: (v if k == "produit" else float(v)) for k, v in row.items()} for row in csv.DictReader(handle)]


def somme_par(rows: List[Dict[str, float]], cle: str) -> Dict[object, Dict[str, float]]:
    out: Dict[object, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in rows:
        for champ in EFFETS + ["ecart_total"]:
            out[row[cle]][champ] += row[champ]
    return out


def style(ax: "plt.Axes") -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.axhline(0, color="#555555", linewidth=0.8)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v / 1000:,.0f} k€".replace(",", " "))


def cascade(rows: List[Dict[str, float]], out: str) -> None:
    total = {c: sum(r[c] for r in rows) for c in EFFETS}
    ecart = sum(r["ecart_total"] for r in rows)
    labels = [LIBELLES[c] for c in EFFETS] + ["Écart total"]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    base = 0.0
    for i, c in enumerate(EFFETS):
        ax.bar(i, total[c], bottom=base, color=COULEURS[c])
        ax.text(i, base + total[c] + 600, f"{total[c]:+,.0f} €".replace(",", " "), ha="center", fontsize=9)
        base += total[c]
    ax.bar(len(EFFETS), ecart, color="#333333")
    ax.text(len(EFFETS), ecart + 600, f"{ecart:+,.0f} €".replace(",", " "), ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(range(len(labels)), labels)
    ax.set_title("Écart annuel de marge : budget vs réalisé (données fictives)", fontsize=11, loc="left")
    style(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def mensuel(rows: List[Dict[str, float]], out: str) -> None:
    par_mois = somme_par(rows, "mois")
    mois = sorted(par_mois)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    pos_base = [0.0] * len(mois)
    neg_base = [0.0] * len(mois)
    for c in EFFETS:
        vals = [par_mois[m][c] for m in mois]
        bottoms = [pos_base[i] if v >= 0 else neg_base[i] for i, v in enumerate(vals)]
        ax.bar(range(len(mois)), vals, bottom=bottoms, color=COULEURS[c], label=LIBELLES[c])
        for i, v in enumerate(vals):
            if v >= 0:
                pos_base[i] += v
            else:
                neg_base[i] += v
    ax.plot(range(len(mois)), [par_mois[m]["ecart_total"] for m in mois], color="#111111", marker="o", linewidth=1.4, label="Écart total")
    ax.set_xticks(range(len(mois)), [MOIS[int(m) - 1] for m in mois])
    ax.set_title("Effets mensuels sur la marge (données fictives)", fontsize=11, loc="left")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1), fontsize=9)
    style(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def par_produit(rows: List[Dict[str, float]], out: str) -> None:
    par_prod = somme_par(rows, "produit")
    produits = sorted(par_prod)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    width = 0.25
    for j, c in enumerate(EFFETS):
        ax.bar([i + (j - 1) * width for i in range(len(produits))], [par_prod[p][c] for p in produits],
               width=width, color=COULEURS[c], label=LIBELLES[c])
    ax.set_xticks(range(len(produits)), produits)
    ax.set_title("Effets annuels par produit (données fictives)", fontsize=11, loc="left")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=9)
    style(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main() -> None:
    rows = charger(os.path.join(HERE, "data", "ecarts_par_produit.csv"))
    dossier = os.path.join(HERE, "captures")
    os.makedirs(dossier, exist_ok=True)
    cascade(rows, os.path.join(dossier, "cascade_effets.png"))
    mensuel(rows, os.path.join(dossier, "ecarts_mensuels.png"))
    par_produit(rows, os.path.join(dossier, "ecart_par_produit.png"))
    for produit, vals in sorted(somme_par(rows, "produit").items()):
        print(f"{produit:>15} : écart {vals['ecart_total']:>10,.0f} € (volume {vals['effet_volume']:,.0f}, prix {vals['effet_prix']:,.0f}, coût {vals['effet_cout']:,.0f})")
    mois = somme_par(rows, "mois")
    pire = min(mois, key=lambda m: mois[m]["ecart_total"])
    meilleur = max(mois, key=lambda m: mois[m]["ecart_total"])
    print(f"Mois le plus défavorable : {MOIS[int(pire) - 1]} ({mois[pire]['ecart_total']:,.0f} €) ; le plus favorable : {MOIS[int(meilleur) - 1]} ({mois[meilleur]['ecart_total']:,.0f} €)")


if __name__ == "__main__":
    main()
