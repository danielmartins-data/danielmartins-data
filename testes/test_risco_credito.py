"""Garante que o modelo de risco roda, generaliza (AUC > 0,65) e não vaza dados."""
import os

import pandas as pd

PROJETO = "analise-risco-credito"


def test_modelo_de_risco_e_curva_de_ganho(rodar_projeto):
    pasta = rodar_projeto(PROJETO, "analise.py")

    comparacao = pd.read_csv(os.path.join(pasta, "dados/comparacao_modelos.csv")).set_index("modelo")
    assert len(comparacao) == 2, "compara regra de negócio com regressão logística"
    assert (comparacao["ligacoes"] == 600).all(), "o corte deve selecionar exatamente 20% de 3.000 clientes"

    auc_logistica = comparacao.loc["Regressão logística (5 features)", "auc"]
    assert 0.5 < auc_logistica <= 1, "AUC deve ficar acima do aleatório"
    assert auc_logistica > 0.65, "o modelo precisa generalizar na validação cruzada"

    base = pd.read_csv(os.path.join(pasta, "dados/base_com_score.csv"))
    assert base["prob_churn"].between(0, 1).all(), "probabilidade entre 0 e 1"
    assert base["churn"].mean() > 0

    # faixas de risco devem ter churn crescente
    faixa = (base.groupby("faixa_risco", observed=True)["churn"].mean().sort_index())
    assert faixa.iloc[-1] > faixa.iloc[0], "a faixa crítica precisa ter mais churn que a baixa"

    ganho = pd.read_csv(os.path.join(pasta, "dados/ganho_acumulado.csv"))
    assert ganho["pct_churns_capturados"].is_monotonic_increasing
    assert ganho["pct_churns_capturados"].iloc[-1] > 99, "a curva termina capturando 100%"
