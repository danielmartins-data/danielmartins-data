"""Garante que as consultas SQL rodam e que os indicadores são consistentes."""
import os

import pandas as pd

PROJETO = "analise-inadimplencia-sql"


def test_consultas_sql_de_inadimplencia(rodar_projeto):
    pasta = rodar_projeto(PROJETO, "analise.py")

    geral = pd.read_csv(os.path.join(pasta, "dados/resultado_visao_geral.csv")).iloc[0]
    assert geral["contratos"] > 0
    assert 0 <= geral["inad_contratos_pct"] <= 100
    assert 0 <= geral["inad_valor_pct"] <= 100

    safra = pd.read_csv(os.path.join(pasta, "dados/resultado_safra_mensal.csv"))
    assert safra["media_movel_3m"].notna().all(), "média móvel não pode ter nulos"
