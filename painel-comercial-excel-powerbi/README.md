# 📈 Painel Comercial: Meta x Realizado (Excel + Power BI)

Projeto básico de **BI comercial**: acompanhar o atingimento de metas de uma equipe de gerentes, por produto, gerente e mês. Entregue em **Excel** (painel pronto e funcional) e **Power BI** (modelo de dados, medidas DAX e roteiro).

> ⚠️ **Os dados são sintéticos (fictícios)**, gerados por `gerar_dados.py` com seed fixa. Não representam nenhuma empresa real.

![Painel em Excel](imagens/painel_excel.png)

## 🎯 Perguntas respondidas

1. A equipe bateu a meta? Quem está acima e abaixo?
2. Como o resultado evolui mês a mês?
3. Qual produto sustenta (ou puxa para baixo) o atingimento?

## 🧰 Ferramentas

Excel (Tabela, SUMIFS, INDEX/MATCH, COUNTIF, validação de dados, formatação condicional, gráficos) · Power BI (modelo estrela, DAX, time intelligence) · Python (geração dos dados)

## 📗 Parte 1: Excel (pronto)

Arquivo: [`excel/painel_comercial.xlsx`](excel/painel_comercial.xlsx)

- **Aba Dados:** 384 linhas em uma Tabela do Excel (mês, gerente, região, produto, meta, realizado).
- **Aba Painel:** lista suspensa de produto (B3) que atualiza KPIs, tabelas e gráficos; cores por atingimento (verde ≥ 100%, amarelo 90-99,9%, vermelho < 90%).
- **Tudo por fórmula** (89 fórmulas, nenhum erro): os totais foram conferidos contra o cálculo independente em Python, inclusive com o filtro de produto.

## 📙 Parte 2: Power BI

Pasta: [`powerbi/`](powerbi)

- **Modelo estrela:** `fato_vendas` + `dim_gerente`, `dim_produto` e `dim_calendario` (em `dados/`).
- **Medidas DAX** em [`medidas.dax`](powerbi/medidas.dax): meta, realizado, % atingimento, gap, mês anterior, variação MoM, acumulado no ano (YTD), ranking de gerentes, status e cor para formatação condicional.
- **Roteiro** em [`roteiro.md`](powerbi/roteiro.md): passo a passo para montar o painel no Power BI Desktop, com layout sugerido.
- *Status:* o arquivo `.pbix` ainda será adicionado.

## 🔎 Principais resultados (dados sintéticos)

- **Equipe:** R$ 37,05 milhões realizados sobre R$ 36,49 milhões de meta (**101,5%**).
- **Gerentes:** 5 de 8 bateram a meta; melhor atingimento **113,1%** (Elisa Prado), menor **89,8%** (Diego Rocha).
- **Meses:** Fevereiro foi o pior (89,3%) e dezembro o melhor (**121,1%**), com forte alta no fim do ano.
- **Produtos:** todos entre 101% e 102%, ou seja, o desvio está nas pessoas e nos meses, não no mix.

## 💡 Recomendações (exemplo)

- Acompanhar de perto os gerentes abaixo de 95% e entender se o problema é carteira, território ou execução.
- Reforçar o primeiro trimestre, que fechou em 93,3% da meta (contra 112,3% no quarto).
- Replicar as práticas dos gerentes acima de 110%.

## ▶️ Como reproduzir

```bash
pip install pandas numpy openpyxl
python gerar_dados.py    # gera dados/*.csv (inclui o modelo estrela)
python criar_excel.py    # gera excel/painel_comercial.xlsx
```

## 📁 Estrutura

```
painel-comercial-excel-powerbi/
├── dados/        # vendas_metas.csv (base única) e tabelas do modelo estrela
├── excel/        # painel_comercial.xlsx
├── powerbi/      # medidas.dax e roteiro.md
├── imagens/      # prints do painel
├── gerar_dados.py
└── criar_excel.py
```

---
Feito por **Daniel Fernando Martins** · [LinkedIn](https://www.linkedin.com/in/danielfernandomartins)
