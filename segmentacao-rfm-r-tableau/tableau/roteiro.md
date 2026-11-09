# Roteiro: montar o dashboard RFM no Tableau

Tempo estimado: 1h30 a 2h. Use o **Tableau Public** (gratuito) ou o Tableau Desktop. Os dados já estão prontos em `../dados/`.

> **Transparência:** nesta pasta estão a base e o roteiro. O dashboard (`.twbx`) é montado no Tableau; o Tableau Public salva e publica na nuvem pública, então não coloque dados reais de clientes.

## 1. Conectar os dados
1. **Conectar → Arquivo de texto** e escolha `dados/rfm_clientes.csv` (1 linha por cliente, 299 linhas).
2. Confira os tipos: `Ultima_Compra` como **Data**; `Valor_Total` e `Ticket_Medio` como **Número**; `R`, `F`, `M` como **Dimensão** (clique com o botão direito → *Converter em dimensão*); `Score_RFM` como texto.
3. Opcional: conecte também `dados/resumo_segmentos.csv` como segunda fonte, só para conferir os números.

## 2. Campos calculados

```text
Cliente Ativo
IF [Frequencia] > 0 THEN 1 ELSE 0 END

Faixa de Recência
IF ISNULL([Recencia_Dias]) THEN "Sem compras"
ELSEIF [Recencia_Dias] <= 30  THEN "0-30 dias"
ELSEIF [Recencia_Dias] <= 90  THEN "31-90 dias"
ELSEIF [Recencia_Dias] <= 180 THEN "91-180 dias"
ELSE "Mais de 180 dias" END

% do Valor        (cálculo de tabela)
SUM([Valor_Total]) / TOTAL(SUM([Valor_Total]))

% dos Clientes    (cálculo de tabela)
COUNTD([id_cliente]) / TOTAL(COUNTD([id_cliente]))

Valor Médio por Cliente Ativo
SUM([Valor_Total]) / SUM([Cliente Ativo])
```

## 3. Cores dos segmentos
Mantenha a mesma cor em todos os gráficos (edite em *Cor → Editar cores*):

| Segmento | Cor sugerida |
|---|---|
| Campeões | Verde escuro |
| Fiéis | Azul |
| Novos e Promissores | Verde-água |
| Precisam de Atenção | Amarelo |
| Em Risco | Laranja |
| Grandes Valores em Risco | Vermelho |
| Hibernando | Cinza |
| Sem compras em 2025 | Cinza claro |

## 4. Planilhas (uma por gráfico)

| # | Planilha | Como montar |
|---|---|---|
| 1 | **KPIs** | Texto com `COUNTD(id_cliente)`, `SUM(Cliente Ativo)`, `SUM(Valor_Total)` e `Valor Médio por Cliente Ativo` |
| 2 | **Valor por segmento** | Mapa de árvore: Tamanho = `SUM(Valor_Total)`; Cor e Rótulo = `Segmento_RFM`; adicione `% do Valor` ao rótulo |
| 3 | **Clientes por segmento** | Barras horizontais: `Segmento_RFM` x `COUNTD(id_cliente)`, ordenado do maior para o menor, com `% dos Clientes` no rótulo |
| 4 | **Recência x Valor** | Dispersão: Colunas = `Recencia_Dias`, Linhas = `Valor_Total`, Detalhe = `Cliente`, Cor = `Segmento_RFM` |
| 5 | **Mapa de calor R x F** | Colunas = `F`, Linhas = `R`, Cor = `COUNTD(id_cliente)`, rótulo com a contagem |
| 6 | **Segmentos por gerente** | Barras empilhadas: `Gerente` x `COUNTD(id_cliente)`, Cor = `Segmento_RFM` (opcional) |

Na dispersão, use escala logarítmica no eixo do valor se os clientes grandes esmagarem o gráfico.

## 5. Dashboard
1. Novo dashboard, tamanho **fixo 1200 x 800** (ou automático).
2. Faixa de KPIs no topo; mapa de árvore e barras de clientes no meio; dispersão e mapa de calor embaixo.
3. Filtros no topo: `Regiao`, `Porte`, `Segmento_Cliente` e `Gerente` (*Aplicar a planilhas selecionadas*).
4. **Ação de filtro:** clicar num segmento do mapa de árvore filtra todo o resto (*Dashboard → Ações → Adicionar ação → Filtro*).
5. Título claro, legenda de cores única e sem excesso de elementos.

## 6. Publicar
1. **Arquivo → Salvar no Tableau Public** e dê um nome como "Segmentação RFM de Clientes".
2. Copie o link público e coloque no README (seção "Parte Tableau").
3. Salve um print do dashboard em `../imagens/dashboard_tableau.png` e referencie no README.
4. Se quiser, exporte também o `.twbx` e coloque em `tableau/`.

## 7. O que o dashboard deve mostrar
- Quanto do valor está concentrado nos Campeões e Fiéis?
- Quantos clientes e quanto valor estão em *Grandes Valores em Risco*?
- Quais gerentes têm mais clientes em risco ou hibernando?
- Quantos clientes do cadastro não compraram nada no ano?
