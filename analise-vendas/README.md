# 📊 Análise de Vendas 2025 (Python + SQL)

Projeto básico de análise de dados, do dado bruto ao insight: **limpeza → consultas SQL → gráficos → conclusões**.

> ⚠️ **Os dados são sintéticos (fictícios)**, gerados por `gerar_dados.py` com seed fixa. Foram criados só para demonstrar o método e não representam nenhuma empresa real.

## 🎯 Perguntas respondidas

1. Quanto a empresa faturou e qual o ticket médio?
2. Como a receita se comporta ao longo do ano?
3. Quais regiões, produtos e canais mais contribuem?

## 🧰 Ferramentas

Python (pandas, matplotlib) · SQL (SQLite) · CSV

## 🔄 Etapas

| Etapa | O que foi feito |
|---|---|
| Limpeza | Remoção de 15 pedidos duplicados e tratamento de 25 regiões vazias ("Não informada") |
| Feature | Criação da coluna `receita = quantidade × preço unitário` |
| SQL | 5 consultas com `GROUP BY`, funções de agregação e subquery (ver `consultas.sql`) |
| Visualização | 3 gráficos em `graficos/` |

## 🔎 Principais resultados

- **Receita total:** R$ 4,10 milhões em 2.119 pedidos, com **ticket médio de R$ 1.933**.
- **Concentração de produto:** Notebooks respondem por cerca de **61% da receita** (R$ 2,49 mi), embora representem só 711 das 6.247 unidades vendidas.
- **Região:** Sudeste lidera com **36%** da receita; Norte é a menor, com **5,6%**.
- **Sazonalidade:** novembro e dezembro somam **21%** do faturamento do ano.
- **Canais:** o Online tem mais pedidos (1.049), mas o **menor ticket médio** (R$ 1.696). Loja física e Televendas ficam acima de R$ 2.150.

## 💡 Recomendações (exemplo)

- Reduzir a dependência de Notebooks com campanhas de acessórios (combos).
- Testar ofertas de maior valor no canal Online para elevar o ticket.
- Planejar estoque e equipe antes de novembro e dezembro.

## ▶️ Como executar

```bash
pip install -r requirements.txt
python gerar_dados.py   # gera dados/vendas_bruto.csv
python analise.py       # limpa, consulta e gera os gráficos
```

## 📁 Estrutura

```
analise-vendas/
├── dados/            # vendas_bruto.csv e vendas_limpo.csv
├── graficos/         # PNGs gerados
├── consultas.sql     # consultas SQL
├── gerar_dados.py    # geração dos dados sintéticos
├── analise.py        # limpeza, SQL e gráficos
└── requirements.txt
```

## 📈 Imagem

![Receita mensal](graficos/receita_mensal.png)

---
Feito por **Daniel Fernando Martins** · [LinkedIn](https://www.linkedin.com/in/danielfernandomartins)
