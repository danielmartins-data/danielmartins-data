# 📈 Painel Comercial: Meta x Realizado (Excel + Power BI)

Projeto de **BI comercial**: acompanhar o atingimento de metas de uma equipe de gerentes, por produto, gerente e mês, e entender a **carteira de clientes** por trás do resultado. Entregue em **Excel** (painel pronto e funcional) e **Power BI** (modelo estrela com duas tabelas fato, medidas DAX e roteiro de 2 páginas).

> ⚠️ **Os dados são sintéticos (fictícios)**, gerados por `gerar_dados.py` com seed fixa. Não representam nenhuma empresa real. As transações por cliente (`gerar_transacoes.py`) são abertas a partir do realizado e **somam exatamente o mesmo valor**, então Excel e Power BI contam a mesma história.

![Painel em Excel](imagens/painel_excel.png)

## 🎯 Perguntas respondidas

1. A equipe bateu a meta? Quem está acima e abaixo?
2. Como o resultado evolui mês a mês?
3. Qual produto sustenta (ou puxa para baixo) o atingimento?
4. Quanto da carteira está ativa e quão concentrado é o resultado nos maiores clientes?
5. Quais segmentos e regiões de clientes sustentam o realizado?

## 🧰 Ferramentas

Excel (Tabela, SUMIFS, INDEX/MATCH, COUNTIF, validação de dados, formatação condicional, gráficos) · Power BI (modelo estrela, DAX, time intelligence) · Python (geração dos dados)

## 📗 Parte 1: Excel (pronto)

Arquivo: [`excel/painel_comercial.xlsx`](excel/painel_comercial.xlsx)

- **Aba Dados:** 384 linhas em uma Tabela do Excel (mês, gerente, região, produto, meta, realizado).
- **Aba Painel:** lista suspensa de produto (B3) que atualiza KPIs, tabelas e gráficos; cores por atingimento (verde ≥ 100%, amarelo 90-99,9%, vermelho < 90%).
- **Tudo por fórmula** (89 fórmulas, nenhum erro): os totais foram conferidos contra o cálculo independente em Python, inclusive com o filtro de produto.

## 📙 Parte 2: Power BI

Pasta: [`powerbi/`](powerbi)

- **Modelo estrela com duas fatos:** `fato_vendas` (meta e realizado por mês, gerente e produto) e `fato_transacoes` (realizado aberto em operações por cliente), compartilhando `dim_gerente`, `dim_produto` e `dim_calendario`, mais `dim_cliente` (em `dados/`).
- **Medidas DAX** em [`medidas.dax`](powerbi/medidas.dax): meta, realizado, % atingimento, gap, mês anterior, variação MoM, acumulado no ano (YTD), ranking de gerentes, status e cor para formatação condicional; e, para a carteira, ticket médio, clientes ativos, concentração Top 10, ranking de clientes e uma medida de conferência entre as duas fatos.
- **Roteiro** em [`roteiro.md`](powerbi/roteiro.md): passo a passo para montar o painel no Power BI Desktop, com layout das 2 páginas (Painel Comercial e Carteira de Clientes).
- *Status:* o arquivo `.pbix` ainda será adicionado.

## 🔎 Principais resultados (dados sintéticos)

- **Equipe:** R$ 37,05 milhões realizados sobre R$ 36,49 milhões de meta (**101,5%**).
- **Gerentes:** 5 de 8 bateram a meta; melhor atingimento **113,1%** (Elisa Prado), menor **89,8%** (Diego Rocha).
- **Meses:** Fevereiro foi o pior (89,3%) e dezembro o melhor (**121,1%**), com forte alta no fim do ano.
- **Produtos:** todos entre 101% e 102%, ou seja, o desvio está nas pessoas e nos meses, não no mix.
- **Carteira:** 1.531 transações de 299 clientes (268 ativos no ano, **89,6%**), ticket médio de cerca de R$ 24,2 mil.
- **Concentração:** os 10 maiores clientes respondem por **20,7%** do realizado e os 20% maiores por **57,0%**.
- **Segmentos:** Alimentação lidera (22,1%) e Educação fecha a lista (13,3%); por região, Sudeste (26,0%) e Nordeste (25,6%) vão praticamente lado a lado.

## 💡 Recomendações (exemplo)

- Acompanhar de perto os gerentes abaixo de 95% e entender se o problema é carteira, território ou execução.
- Reforçar o primeiro trimestre, que fechou em 93,3% da meta (contra 112,3% no quarto).
- Replicar as práticas dos gerentes acima de 110%.
- Com 57% do valor em 20% dos clientes, criar um plano de relacionamento para esse grupo e acompanhar o risco de perda.

## ▶️ Como reproduzir

```bash
pip install pandas numpy openpyxl
python gerar_dados.py    # gera dados/*.csv (inclui o modelo estrela)
python gerar_transacoes.py  # gera dim_cliente.csv e fato_transacoes.csv (soma = realizado)
python criar_excel.py    # gera excel/painel_comercial.xlsx
```

## 📁 Estrutura

```
painel-comercial-excel-powerbi/
├── dados/        # vendas_metas.csv (base única), fatos e dimensões do modelo estrela
├── excel/        # painel_comercial.xlsx
├── powerbi/      # medidas.dax e roteiro.md
├── imagens/      # prints do painel
├── gerar_dados.py        # metas x realizado e modelo estrela
├── gerar_transacoes.py   # clientes e transações (reconciliadas com o realizado)
└── criar_excel.py
```

---
Feito por **Daniel Fernando Martins** · [LinkedIn](https://www.linkedin.com/in/danielfernandomartins)
