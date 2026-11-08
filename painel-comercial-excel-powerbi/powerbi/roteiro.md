# Roteiro: montar o painel no Power BI Desktop

Tempo estimado: 40 a 60 minutos. Os arquivos de dados já estão prontos em `../dados/` (modelo estrela).

> **Transparência:** nesta pasta estão os dados, o modelo e as medidas DAX. O arquivo `.pbix` é montado no Power BI Desktop (gratuito, só para Windows). As medidas foram escritas para o modelo descrito abaixo.

## 1. Importar os dados
1. **Página Inicial → Obter dados → Texto/CSV** e importe os 4 arquivos de `dados/`:
   `fato_vendas.csv`, `dim_gerente.csv`, `dim_produto.csv`, `dim_calendario.csv`.
2. No Power Query, confira os tipos: `Mes` e `Data` como **Data**; `Meta` e `Realizado` como **Número decimal fixo**.

## 2. Modelo (modelo estrela)
Relacionamentos (todos **muitos para um**, filtro de dimensão para fato):

| Fato | Dimensão |
|---|---|
| `fato_vendas[Mes]` | `dim_calendario[Data]` |
| `fato_vendas[Gerente]` | `dim_gerente[Gerente]` |
| `fato_vendas[Produto]` | `dim_produto[Produto]` |

Marque `dim_calendario` como **tabela de datas** (Ferramentas de tabela → Marcar como tabela de datas → coluna `Data`).
Em `dim_calendario`, classifique a coluna `Mes` por `MesNum` (Classificar por coluna).

## 3. Medidas
Crie a tabela `_Medidas` (Inserir dados, tabela vazia) e cole as medidas de `medidas.dax`, uma por vez.
Formate: `% Atingimento`, `Variação MoM %` e `% Atingimento YTD` como porcentagem; `Meta Total`, `Realizado Total` e `Gap vs Meta` como moeda (R$).

## 4. Layout sugerido (1 página)
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

## 5. Acabamento
- Título claro, cores consistentes (azul para meta, vermelho/laranja para realizado) e fonte legível.
- Alinhe os visuais e reduza o excesso de elementos: um painel limpo vale mais que um cheio.
- Renomeie a página para "Painel Comercial".

## 6. Publicar no GitHub
1. Salve como `powerbi/painel_comercial.pbix` e envie para o repositório (arquivos `.pbix` podem ser enviados normalmente).
2. Tire um print e salve em `imagens/painel_powerbi.png`.
3. No README principal, acrescente a imagem na seção de resultados.
4. Opcional: publique no Power BI Service e coloque o link.

## 7. Perguntas que o painel responde
- Quem está acima e abaixo da meta, e por quanto?
- Em que meses a equipe ficou abaixo do esperado?
- Qual produto está puxando o resultado para cima ou para baixo?
- O acumulado do ano está no ritmo da meta?
