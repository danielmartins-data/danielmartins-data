"""Garante que a análise de churn roda e que o score de risco fica no intervalo 0-3."""
import os

import pandas as pd

PROJETO = "analise-churn-clientes"


def test_score_de_risco_de_churn(rodar_projeto):
    pasta = rodar_projeto(PROJETO, "analise.py")

    risco = pd.read_csv(os.path.join(pasta, "dados/clientes_com_risco.csv"))
    assert not risco.empty
    assert risco["score_risco"].between(0, 3).all(), "o score vai de 0 a 3 pontos"
    assert risco["churn"].isin([0, 1]).all(), "churn deve ser binário"
    assert 0 < risco["churn"].mean() < 1, "o churn geral deve ficar entre 0% e 100%"
