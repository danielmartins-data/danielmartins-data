"""Garante que o painel em Excel é gerado com as abas esperadas."""
import os

import pytest

openpyxl = pytest.importorskip("openpyxl", reason="openpyxl é necessário para ler o .xlsx")

PROJETO = "painel-comercial-excel-powerbi"


def test_painel_excel_e_gerado(rodar_projeto):
    pasta = rodar_projeto(PROJETO, "criar_excel.py")

    caminho = os.path.join(pasta, "excel/painel_comercial.xlsx")
    assert os.path.exists(caminho), "o arquivo do painel deve ser criado"

    wb = openpyxl.load_workbook(caminho)
    assert len(wb.sheetnames) >= 2, "o painel tem pelo menos dados e a aba do painel"
