"""Testes de "vitrine": garantem que todo projeto publicado está apresentável.

Um recrutador abre o repositório e espera encontrar, em cada pasta de projeto,
um README com pergunta de negócio, resultado e instruções de execução. Se algo
faltar, o CI avisa antes de qualquer entrevista.
"""
import os
import re

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJETOS = [
    "analise-churn-clientes",
    "analise-cohort-retencao",
    "analise-inadimplencia-sql",
    "analise-teste-ab",
    "analise-vendas",
    "painel-comercial-excel-powerbi",
    "pipeline-etl-dashboard",
    "previsao-demanda",
    "segmentacao-rfm-r-tableau",
]


@pytest.mark.parametrize("projeto", PROJETOS)
def test_readme_do_projeto_tem_o_que_recrutador_procura(projeto):
    caminho = os.path.join(RAIZ, projeto, "README.md")
    assert os.path.exists(caminho), f"{projeto} precisa de README.md"

    texto = open(caminho, encoding="utf-8").read()
    assert texto.startswith("# "), f"{projeto}: o README começa com um título H1"
    assert len(texto) > 800, f"{projeto}: README curto demais para convencer alguém"

    minusculo = texto.lower()
    assert "sintétic" in minusculo or "fictíc" in minusculo, \
        f"{projeto}: precisa avisar que os dados são sintéticos"
    assert re.search(r"## .*(resumo|resultado)", minusculo), \
        f"{projeto}: precisa de uma seção de resultado/resumo executivo"
    assert re.search(r"## .*(como rodar|estrutura|método|metodologia)", minusculo), \
        f"{projeto}: precisa explicar método ou como rodar"


def test_readme_principal_aponta_para_todos_os_projetos():
    texto = open(os.path.join(RAIZ, "README.md"), encoding="utf-8").read()
    faltando = [p for p in PROJETOS if p not in texto]
    assert not faltando, f"o README principal não cita: {faltando}"


def test_todos_os_projetos_tem_requirements():
    faltando = [p for p in PROJETOS if not os.path.exists(os.path.join(RAIZ, p, "requirements.txt"))]
    assert not faltando, f"projetos sem requirements.txt: {faltando}"
