# 🤝 Como contribuir / como este repositório é organizado

Este é um repositório de portfólio pessoal, mas ele segue as mesmas regras de um projeto de equipe — é assim que ele é mantido.

## 📐 Padrão de cada projeto

Todo projeto em uma pasta própria segue a mesma estrutura:

```
nome-do-projeto/
├── README.md            # pergunta de negócio, resumo executivo, método, como rodar
├── requirements.txt     # dependências do projeto
├── gerar_dados.py       # gera a base sintética (seed fixa)
├── analise.py | etl.py  # o trabalho analítico
├── dados/               # entrada e saída em CSV/SQLite
└── graficos/            # visualizações
```

Regras que o CI verifica automaticamente (`testes/test_projetos_estrutura.py`):

1. README com título, resumo executivo, método/como rodar e aviso de **dados sintéticos**.
2. `requirements.txt` presente.
3. O projeto aparece no README principal.

## 🧪 Testes

```bash
pip install -r requirements.txt
pip install pytest
pytest -q
```

- `testes/conftest.py` fornece a fixture `rodar_projeto`, que executa cada análise na própria pasta (como o README manda).
- Cada projeto tem um teste que valida **as saídas**, não só "se rodou": somas, unicidade de chave, intervalos de confiança, monotonicidade da coorte, regras de qualidade.
- `testes/test_projetos_estrutura.py` protege a vitrine: se um README perder o resumo ou o aviso de dados sintéticos, o CI reprova.

## 🔀 Fluxo de trabalho (git)

```bash
git checkout -b feat/nome-curto
# ... alterações ...
git add .
git commit -m "feat: descreve o que mudou"
git push -u origin feat/nome-curto
# abre o Pull Request e espera o CI ficar verde
```

Convenção de commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`.

## 🧭 Princípios deste portfólio

- **Reprodutível:** seed fixa, dependências declaradas, um comando para rodar.
- **Honesto:** dados sintéticos avisados; quando um modelo simples ganha do complexo, o README diz isso.
- **Orientado a decisão:** todo projeto termina em recomendação de negócio.
- **Auditável:** o pipeline registra o que mudou em cada etapa (`log_etl.json`).
