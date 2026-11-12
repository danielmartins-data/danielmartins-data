"""Garante que a segmentação RFM roda (em Python) e reproduz os números do README.

O script oficial do projeto é em R e também roda em um job dedicado do GitHub Actions.
Este teste adicional executa a versão equivalente em Python para validar a paridade
numérica mesmo em ambientes sem R instalado.
"""
import os

import pandas as pd

PROJETO = "segmentacao-rfm-r-tableau"


def test_rfm_reproduz_resumo_do_readme(rodar_projeto):
    pasta = rodar_projeto(PROJETO, "gerar_rfm.py")

    resumo = pd.read_csv(os.path.join(pasta, "dados/python/resumo_segmentos.csv"))
    clientes = pd.read_csv(os.path.join(pasta, "dados/python/rfm_clientes.csv"))

    assert len(clientes) == 299, "a carteira tem 299 clientes"
    assert resumo["Clientes"].sum() == 299
    assert abs(resumo["Pct_Valor"].sum() - 100) < 1, "os percentuais de valor somam 100%"

    # números publicados no README
    campeoes = resumo.set_index("Segmento_RFM").loc["Campeões"]
    assert campeoes["Clientes"] == 55
    assert campeoes["Pct_Valor"] == 49.7

    valor_total = clientes["Valor_Total"].sum()
    assert abs(valor_total - 37_045_700) < 1, "o valor total deve bater com as transações"
