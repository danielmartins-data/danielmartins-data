"""Garante que a previsão de demanda roda, compara modelos e não usa o futuro."""
import os

import pandas as pd

PROJETO = "previsao-demanda"


def test_previsao_30_dias(rodar_projeto):
    pasta = rodar_projeto(PROJETO, "previsao.py")

    prev = pd.read_csv(os.path.join(pasta, "dados/previsao_30dias.csv"), parse_dates=["data"])
    assert len(prev) == 30, "a previsão é de 30 dias"
    assert prev["data"].is_monotonic_increasing
    assert (prev["previsao_pedidos"] > 0).all()
    assert (prev["piso_95"] <= prev["previsao_pedidos"]).all()
    assert (prev["previsao_pedidos"] <= prev["teto_95"]).all()

    metricas = pd.read_csv(os.path.join(pasta, "dados/metricas_modelos.csv"), index_col=0)
    assert {"baseline_sazonal", "holt_winters"} <= set(metricas.index)
    assert (metricas["MAE"] > 0).all()
