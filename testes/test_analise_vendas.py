"""Garante que a análise de vendas roda de ponta a ponta e entrega os números esperados."""
import os

import pandas as pd

PROJETO = "analise-vendas"


def test_analise_de_vendas_gera_base_limpa(rodar_projeto, tmp_path, monkeypatch):
    pasta = rodar_projeto(PROJETO, "analise.py")

    limpo = pd.read_csv(os.path.join(pasta, "dados/vendas_limpo.csv"))
    assert not limpo.empty, "a base limpa não pode ficar vazia"
    assert limpo["id_pedido"].is_unique, "a limpeza deve remover pedidos duplicados"
    assert limpo["regiao"].notna().all(), "região vazia deve virar 'Não informada'"

    esperado = (limpo["quantidade"] * limpo["preco_unitario"]).round(2)
    assert esperado.equals(limpo["receita"]), "receita = quantidade x preço unitário"
