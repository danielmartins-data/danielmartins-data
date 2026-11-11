"""Garante que o teste A/B roda e que o cálculo estatístico está correto."""
import os

import pandas as pd

PROJETO = "analise-teste-ab"


def test_resultado_do_teste_ab(rodar_projeto):
    pasta = rodar_projeto(PROJETO, "analise.py")

    resultado = pd.read_csv(os.path.join(pasta, "dados/resultado_teste.csv")).iloc[0]
    assert resultado["visitantes_A"] > 1000 and resultado["visitantes_B"] > 1000
    assert 0 <= resultado["conversao_A_pct"] <= 100
    assert 0 <= resultado["p_valor"] <= 1, "p-valor sempre entre 0 e 1"
    assert resultado["significante_5pct"] in ("sim", "não")
    assert (resultado["significante_5pct"] == "sim") == (resultado["p_valor"] < 0.05)
    assert resultado["amostra_necessaria_por_grupo"] > 0
