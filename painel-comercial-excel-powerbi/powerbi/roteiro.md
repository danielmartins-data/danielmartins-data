# Roteiro: montar o painel no Power BI Desktop

Tempo estimado: 1h30 a 2h (2 páginas). Os arquivos de dados já estão prontos em `../dados/` (modelo estrela).

> **Transparência:** nesta pasta estão os dados, o modelo e as medidas DAX. O arquivo `.pbix` é montado no Power BI Desktop (gratuito, só para Windows). As medidas foram escritas para o modelo descrito abaixo.

## 1. Importar os dados
1. **Página Inicial → Obter dados → Texto/CSV** e importe os 6 arquivos de `dados/`:
   `fato_vendas.csv`, `fato_transacoes.csv`, `dim_gerente.csv`, `dim_produto.csv`, `dim_cliente.csv`, `dim_calendario.csv`.
2. No Power Query, confira os tipos: `Mes` e `Data` como **Data**; `Meta`, `Realizado` e `Valor` como **Número decimal fixo**.
3. Não precisa importar `vendas_metas.csv` (é a base única usada no Excel).

## 2. Modelo (modelo estrela)
Relacionamentos (todos **muitos para um**, filtro de dimensão para fato):

| Fato | Dimensão |
|---|---|
| `fato_vendas[Mes]` | `dim_calendario[Data]` |
| `fato_vendas[Gerente]` | `dim_gerente[Gerente]` |
| `fato_vendas[Produto]` | `dim_produto[Produto]` |
| `fato_transacoes[Data]` | `dim_calendario[Data]` |
| `fato_transacoes[Gerente]` | `dim_gerente[Gerente]` |
| `fato_transacoes[Produto]` | `dim_produto[Produto]` |
| `fato_transacoes[id_cliente]` | `dim_cliente[id_cliente]` |

`fato_vendas` guarda meta e realizado agregados (mês x gerente x produto); `fato_transacoes` abre o realizado em operações por cliente. As duas compartilham as mesmas dimensões e a soma bate: use a medida `Diferença vs Realizado` para conferir (deve dar 0). Não relacione as duas fatos entre si.

Marque `dim_calendario` como **tabela de datas** (Ferramentas de tabela → Marcar como tabela de datas → coluna `Data`).
Em `dim_calendario`, classifique a coluna `Mes` por `MesNum` (Classificar por coluna).

## 3. Medidas
Crie a tabela `_Medidas` (Inserir dados, tabela vazia) e cole as medidas de `medidas.dax`, uma por vez.
Formate: `% Atingimento`, `Variação MoM %` e `% Atingimento YTD` como porcentagem; `Meta Total`, `Realizado Total` e `Gap vs Meta` como moeda (R$).

## 4. Layout sugerido: página 1, "Painel Comercial"
| Área | Visual | Campos |
|---|---|---|
| Topo, esquerda | Segmentação (slicer) | `dim_produto[Produto]` |
| Topo | Segmentação | `dim_calendario[Trimestre]` |
| Linha de cartões | 4 cartões | `Meta Total`, `Realizado Total`, `% Atingimento`, `Gerentes na Meta (texto)` |
| Centro, esquerda | Colunas agrupadas | Eixo: `dim_gerente[Gerente]`; Valores: `Meta Total`, `Realizado Total` |
| Centro, direita | Linhas | Eixo: `dim_calendario[Mes]`; Valores: `Meta Total`, `Realizado Total` |
| Embaixo, esquerda | Tabela | `Gerente`, `Meta Total`, `Realizado Total`, `% Atingimento`, `Status`, `Ranking Gerente` |
| Embaixo, direita | Gráfico de rosca ou barras | `dim_produto[Produto]` x `Realizado Total` |

**Formatação condicional:** na tabela, coluna `Status` → Cor da fonte → Valor do campo → `Cor do Status`.

## 4.1 Página 2, "Carteira de Clientes"
| Área | Visual | Campos |
|---|---|---|
| Topo | Segmentações | `dim_gerente[Gerente]`, `dim_produto[Produto]`, `dim_calendario[Trimestre]` |
| Linha de cartões | 5 cartões | `Valor Transacionado`, `Clientes Ativos`, `% Clientes Ativos`, `Ticket Médio`, `% Concentração Top 10` |
| Centro, esquerda | Barras horizontais | Top 10 `dim_cliente[Cliente]` x `Valor Transacionado` (filtro Top N = 10) |
| Centro, direita | Rosca | `dim_cliente[Segmento]` x `Valor Transacionado` |
| Embaixo, esquerda | Colunas | `dim_cliente[Regiao]` x `Valor Transacionado` |
| Embaixo, direita | Tabela | `Cliente`, `Valor Transacionado`, `% do Total`, `Ranking Cliente` |

## 5. Acabamento
- Título claro, cores consistentes (azul para meta, vermelho/laranja para realizado) e fonte legível.
- Alinhe os visuais e reduza o excesso de elementos: um painel limpo vale mais que um cheio.
- Adicione botões de navegação entre as duas páginas.

## 6. Publicar no GitHub
1. Salve como `powerbi/painel_comercial.pbix` e envie para o repositório (arquivos `.pbix` podem ser enviados normalmente).
2. Tire um print de cada página e salve em `imagens/painel_powerbi_1.png` e `imagens/painel_powerbi_2.png`.
3. No README principal, acrescente a imagem na seção de resultados.
4. Opcional: publique no Power BI Service e coloque o link.

## 7. Perguntas que o painel responde
- Quem está acima e abaixo da meta, e por quanto?
- Em que meses a equipe ficou abaixo do esperado?
- Qual produto está puxando o resultado para cima ou para baixo?
- O acumulado do ano está no ritmo da meta?
- Quanto da carteira está ativa e quão concentrada é a receita nos maiores clientes?
- Quais segmentos e regiões sustentam o realizado?
