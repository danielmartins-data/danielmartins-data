"""Garante que o painel em Excel é gerado com as abas esperadas."""
import os

import pytest
import pandas as pd

openpyxl = pytest.importorskip("openpyxl", reason="openpyxl é necessário para ler o .xlsx")

PROJETO = "painel-comercial-excel-powerbi"


def test_painel_excel_e_gerado(rodar_projeto):
    pasta = rodar_projeto(PROJETO, "criar_excel.py")

    caminho = os.path.join(pasta, "excel/painel_comercial.xlsx")
    assert os.path.exists(caminho), "o arquivo do painel deve ser criado"

    wb = openpyxl.load_workbook(caminho)
    assert len(wb.sheetnames) >= 2, "o painel tem pelo menos dados e a aba do painel"


def test_modelo_estrela_concilia_com_transacoes():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dados = os.path.join(raiz, PROJETO, "dados")
    fato = pd.read_csv(os.path.join(dados, "fato_vendas.csv"), parse_dates=["Mes"])
    trans = pd.read_csv(os.path.join(dados, "fato_transacoes.csv"), parse_dates=["Data"])
    clientes = pd.read_csv(os.path.join(dados, "dim_cliente.csv"))

    fato["mes_ref"] = fato["Mes"].dt.to_period("M").astype(str)
    trans["mes_ref"] = trans["Data"].dt.to_period("M").astype(str)
    esperado = fato.groupby(["mes_ref", "Gerente", "Produto"])["Realizado"].sum().sort_index()
    observado = trans.groupby(["mes_ref", "Gerente", "Produto"])["Valor"].sum().sort_index()
    pd.testing.assert_series_equal(esperado, observado, check_names=False, check_exact=False, rtol=0, atol=0.02)

    assert clientes["id_cliente"].is_unique
    assert set(trans["id_cliente"]).issubset(set(clientes["id_cliente"]))
