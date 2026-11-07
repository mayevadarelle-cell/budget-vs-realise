"""Tests de la décomposition volume / prix / coût (données fictives).

Lancer depuis le dossier du projet : python -m pytest tests/ -v
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from analyse_ecarts import decompose, load_rows  # noqa: E402

DATA = os.path.join(os.path.dirname(HERE), "data", "budget_vs_realise.csv")


def ligne(**kw):
    base = {"mois": 1.0, "produit": "Test", "volume_budget": 100.0, "prix_budget": 10.0, "cout_unitaire_budget": 6.0,
            "volume_reel": 100.0, "prix_reel": 10.0, "cout_unitaire_reel": 6.0}
    base.update(kw)
    return base


def test_exemple_calcule_a_la_main():
    # budget : 100 x (10 - 6) = 400 ; réel : 110 x (11 - 5,5) = 605 ; écart = 205
    res = decompose(ligne(volume_reel=110.0, prix_reel=11.0, cout_unitaire_reel=5.5))
    assert res["marge_budget"] == 400.0
    assert res["marge_reelle"] == 605.0
    assert res["effet_volume"] == 40.0   # (110 - 100) x 4
    assert res["effet_prix"] == 110.0    # (11 - 10) x 110
    assert res["effet_cout"] == 55.0     # (6 - 5,5) x 110
    assert res["ecart_total"] == 205.0


def test_aucun_ecart_quand_reel_egal_budget():
    res = decompose(ligne())
    assert res["ecart_total"] == res["effet_volume"] == res["effet_prix"] == res["effet_cout"] == 0.0


def test_signe_favorable_positif():
    assert decompose(ligne(prix_reel=11.0))["effet_prix"] > 0
    assert decompose(ligne(cout_unitaire_reel=7.0))["effet_cout"] < 0   # coût plus élevé : défavorable
    assert decompose(ligne(volume_reel=90.0))["effet_volume"] < 0


def test_jeu_de_donnees_complet_est_coherent():
    rows = load_rows(DATA)
    assert len(rows) == 36   # 3 produits x 12 mois
    for r in rows:
        res = decompose(r)
        assert abs(res["ecart_total"] - (res["effet_volume"] + res["effet_prix"] + res["effet_cout"])) < 0.01


def test_donnees_reproductibles():
    with open(DATA, newline="", encoding="utf-8") as handle:
        premiere = next(csv.DictReader(handle))
    assert premiere["produit"] == "Gamme Pro" and premiere["volume_budget"] == "720"
