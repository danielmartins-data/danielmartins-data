"""Testes de apresentação: garantem que a vitrine renderiza sem quebrar no GitHub.

Um README com imagem quebrada ou link morto é o primeiro "não" de um recrutador.
Estes testes checam o que dá para checar sem abrir o navegador.
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _readme() -> str:
    return open(os.path.join(RAIZ, "README.md"), encoding="utf-8").read()


def test_todo_link_interno_existe():
    texto = _readme()
    links = re.findall(r"\]\((\./[^)#]+)\)", texto) + re.findall(r'src="(\./[^"]+)"', texto)
    assert links, "o README precisa de links para os projetos"
    quebrados = [l for l in set(links) if not os.path.exists(os.path.join(RAIZ, l[2:]))]
    assert not quebrados, f"links/imagens quebrados no README: {quebrados}"


def test_todo_projeto_tem_cartao_com_imagem():
    texto = _readme()
    pastas = [p for p in os.listdir(RAIZ)
              if not p.startswith(".")
              and os.path.isdir(os.path.join(RAIZ, p))
              and os.path.exists(os.path.join(RAIZ, p, "README.md"))]
    sem_cartao = [p for p in pastas if f"tree/main/{p}" not in texto]
    assert not sem_cartao, f"projetos sem cartão no README: {sem_cartao}"


def test_imagens_dos_projetos_existem():
    texto = _readme()
    imagens = re.findall(r'src="\./([^"]+\.(?:png|svg))"', texto)
    assert len(imagens) >= 10, "cada projeto deve mostrar uma imagem"
    faltando = [i for i in imagens if not os.path.exists(os.path.join(RAIZ, i))]
    assert not faltando, f"imagens ausentes: {faltando}"


def test_readme_tem_os_blocos_de_convencimento():
    texto = _readme()
    for bloco in ["Em 30 segundos", "Portfólio em destaque", "Para quem está avaliando",
                  "Por que me contratar", "Como rodar e testar"]:
        assert bloco in texto, f"falta o bloco '{bloco}' no README"
