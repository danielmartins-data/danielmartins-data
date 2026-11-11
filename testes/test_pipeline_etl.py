"""Garante que o pipeline ETL limpa a base e passa em todas as regras de qualidade."""
import json
import os

import pandas as pd

PROJETO = "pipeline-etl-dashboard"


def test_pipeline_etl_e_dashboard(rodar_projeto):
    pasta = rodar_projeto(PROJETO, os.path.join("src", "etl.py"))

    limpo = pd.read_csv(os.path.join(pasta, "dados/vendas_limpo.csv"))
    bruto = pd.read_csv(os.path.join(pasta, "dados/vendas_2025.csv"))

    assert len(limpo) < len(bruto), "o pipeline deve remover linhas inválidas"
    assert limpo["id_pedido"].is_unique, "não pode sobrar pedido duplicado"
    assert (limpo["quantidade"] > 0).all(), "quantidade negativa deve ser tratada"
    assert (limpo["preco_unitario"] > 0).all()
    assert limpo["produto"].nunique() == 5, "nomes de produto devem ser padronizados"

    qualidade = pd.read_csv(os.path.join(pasta, "dados/qualidade.csv"))
    assert qualidade["aprovada"].all(), "todas as regras de qualidade devem passar"

    log = json.load(open(os.path.join(pasta, "dados/log_etl.json"), encoding="utf-8"))
    assert log["kpis"]["linhas_limpas"] == len(limpo)
    assert log["kpis"]["receita_total"] > 0


def test_dashboard_e_gerado(rodar_projeto):
    pasta = rodar_projeto(PROJETO, os.path.join("src", "etl.py"))
    rodar_projeto(PROJETO, os.path.join("src", "gerar_dashboard.py"))

    html = open(os.path.join(pasta, "dashboard.html"), encoding="utf-8").read()
    assert "<svg" in html, "o dashboard deve ter gráficos SVG"
    assert "Dados sintéticos" in html, "o aviso de dados sintéticos é obrigatório"
    assert "Receita por região" in html
