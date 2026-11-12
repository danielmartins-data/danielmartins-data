"""Configuração comum dos testes: cada projeto é executado na sua própria pasta."""
import os

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def rodar_projeto(monkeypatch):
    """Entra na pasta do projeto e executa o script de análise.

    Os scripts usam caminhos relativos (dados/, graficos/), então o teste roda
    exatamente como o README manda rodar: a partir da pasta do projeto.
    """

    def _rodar(pasta: str, script: str):
        caminho = os.path.join(RAIZ, pasta)
        monkeypatch.chdir(caminho)
        monkeypatch.syspath_prepend(caminho)
        with open(script, encoding="utf-8") as f:
            codigo = f.read()
        exec(compile(codigo, script, "exec"), {"__name__": "__main__"})
        return caminho

    return _rodar
