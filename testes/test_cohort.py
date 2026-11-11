"""Garante que a análise de coorte roda e que a matriz de retenção é coerente."""
import os

import pandas as pd

PROJETO = "analise-cohort-retencao"


def test_matriz_de_coorte_e_ltv(rodar_projeto):
    pasta = rodar_projeto(PROJETO, "analise.py")

    matriz = pd.read_csv(os.path.join(pasta, "dados/cohort_retencao.csv"), index_col=0)
    assert matriz.shape[0] >= 12, "deve haver pelo menos 12 coortes mensais"
    assert matriz.iloc[:, 0].dropna().between(75, 100).all(), \
        "no mês 0 a retenção é alta (o cliente pode sair dentro do primeiro mês)"

    # a retenção não pode aumentar com o tempo dentro de uma coorte
    for _, linha in matriz.iterrows():
        valores = linha.dropna().to_numpy()
        assert (valores[1:] <= valores[:-1] + 0.01).all(), "retenção deve ser monotônica"

    ltv = pd.read_csv(os.path.join(pasta, "dados/resumo_ltv.csv"))
    assert (ltv["ltv_estimado"] > 0).all()
    assert ltv["vida_media_meses"].between(1, 36).all()
