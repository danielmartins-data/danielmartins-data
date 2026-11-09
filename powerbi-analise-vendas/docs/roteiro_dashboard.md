# Roteiro de construção do dashboard

Tempo estimado: 3 a 5 horas na primeira vez.

## 1. Importar e tratar (Power Query)

1. Obter dados → Texto/CSV → importe os 5 arquivos da pasta `data/`.
2. Renomeie as consultas: `fVendas`, `fMetas`, `dClientes`, `dProdutos`, `dVendedores`.
3. Confira os tipos: `data` como Data, `receita`/`custo` como Número Decimal Fixo, `desconto_pct` como Porcentagem.
4. Remova linhas duplicadas e confira se não há nulos (a base é sintética e limpa, mas deixe esse passo registrado).
5. Em `fVendas`, crie a coluna `Lucro` = `receita - custo` (opcional, já existe a medida Margem Bruta).

## 2. Modelo (esquema estrela)

| Relação | Tipo |
|---|---|
| dCalendario[Date] → fVendas[data] | 1:N |
| dClientes[id_cliente] → fVendas[id_cliente] | 1:N |
| dProdutos[id_produto] → fVendas[id_produto] | 1:N |
| dVendedores[id_vendedor] → fVendas[id_vendedor] | 1:N |
| dVendedores[id_vendedor] → fMetas[id_vendedor] | 1:N |

Para ligar `fMetas` ao calendário, crie em `fMetas` a coluna `DataMeta = DATE([ano], [mes], 1)` e relacione com `dCalendario[Date]`, ou use `Ano` e `Mes` nos visuais de meta.

Tire um print da visão de modelo para colocar no README.

## 3. Páginas do relatório

### Página 1: Visão Executiva
- Cartões: Receita, Margem %, Ticket Médio, Clientes Ativos, Atingimento %, Crescimento YoY %.
- Linha: Receita por mês, com Receita Ano Anterior como segunda linha.
- Barras: Receita por Categoria de produto.
- Mapa ou barras: Receita por Região.
- Segmentações: Ano, Trimestre, Região.

### Página 2: Metas e Desempenho do Time
- Tabela de vendedores: Receita, Meta, Atingimento %, Gap para Meta (com formatação condicional).
- Barras: Atingimento % por vendedor.
- Linha: Receita Acumulada no Ano vs Meta.

### Página 3: Clientes e Produtos
- Barras: Top 10 clientes por Receita.
- Rosca ou barras: Receita por Segmento e por Porte.
- Matriz: Produto × Trimestre com Receita e Margem %.
- Dispersão: Desconto Médio % × Margem % por produto.

## 4. Perguntas que o dashboard deve responder

Escreva as respostas no README, na seção "Principais insights". Isso é o que mais mostra raciocínio analítico:

1. Qual categoria tem a maior margem? E qual vende mais?
2. Quais vendedores bateram a meta em 2025?
3. Qual região cresceu mais de 2024 para 2025?
4. Qual a concentração de receita nos 10 maiores clientes?
5. Descontos maiores estão corroendo a margem de algum produto?

## 5. Boas práticas de design

- Máximo de 3 a 4 cores, mesma paleta em todas as páginas.
- Títulos claros em cada visual e unidade nos eixos.
- Alinhe os visuais na grade e deixe espaço entre eles.
- Dê um nome sugestivo a cada página e adicione botões de navegação.

## 6. Publicar no GitHub

1. Salve o arquivo como `Dashboard_Vendas.pbix` na pasta `powerbi/`.
2. Exporte as páginas em PNG (Arquivo → Exportar → PDF e depois imagens, ou print de tela) e salve em `images/`.
3. Atualize o README com as imagens e os insights.
4. `git add . && git commit -m "Projeto Power BI de análise de vendas" && git push`.
