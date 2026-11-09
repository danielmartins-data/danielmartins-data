# Análise de Vendas e Metas | Power BI

Dashboard em Power BI para acompanhar receita, margem, atingimento de metas e carteira de clientes de uma operação comercial B2B de meios de pagamento e serviços financeiros.

> Os dados são **fictícios**, gerados por script (`scripts/gerar_dados.py`) apenas para fins de estudo e portfólio.

## Por que este projeto

Vendas consultivas, gestão de carteira e acompanhamento de metas são o dia a dia de uma área comercial. Aqui traduzo esse contexto em perguntas de negócio respondidas com dados: quem bate a meta, quais produtos geram margem, onde está a receita e como a carteira evolui.

## Perguntas de negócio

1. Qual a evolução da receita e da margem, e quanto cresceu de 2024 para 2025?
2. Quais vendedores e regiões atingem a meta?
3. Quais produtos e categorias têm melhor margem?
4. Qual a concentração da receita nos maiores clientes?
5. Os descontos estão reduzindo a margem?

## Ferramentas e técnicas

- **Power BI Desktop**: Power Query, modelagem em esquema estrela, DAX e visuais interativos
- **DAX**: medidas de receita, margem, ticket médio, atingimento de meta, YoY e acumulado no ano (ver [`docs/medidas_dax.md`](docs/medidas_dax.md))
- **Python**: geração da base fictícia, com semente fixa para reprodutibilidade

## Modelo de dados

Esquema estrela com a tabela fato `fVendas` e as dimensões `dClientes`, `dProdutos`, `dVendedores` e `dCalendario`, além da tabela de metas `fMetas`.

![Modelo de dados](images/modelo.png)

## Dashboard

| Visão Executiva | Metas e Desempenho | Clientes e Produtos |
|---|---|---|
| ![](images/pagina1.png) | ![](images/pagina2.png) | ![](images/pagina3.png) |

## Principais insights

> Preencha depois de montar o dashboard, com números reais da sua base. Exemplo de formato:
>
> - A receita cresceu **X%** em 2025 vs 2024, puxada por **[categoria]**.
> - **[N] de 6** vendedores bateram a meta em 2025; a região **[região]** teve o maior crescimento.
> - Os 10 maiores clientes concentram **X%** da receita.
> - Produtos com desconto médio acima de **X%** tiveram margem **Y p.p.** menor.

## Como reproduzir

```bash
git clone https://github.com/danielmartins-data/danielmartins-date.git
cd danielmartins-date/powerbi-analise-vendas
python scripts/gerar_dados.py     # opcional: os CSVs já estão em /data
```

Abra `powerbi/Dashboard_Vendas.pbix` no Power BI Desktop (em construção). Se o caminho dos CSVs mudar, ajuste a fonte em Transformar dados → Configurações da fonte de dados.

## Estrutura da pasta

```
├── data/            # CSVs (vendas, clientes, produtos, vendedores, metas)
├── docs/            # medidas DAX e roteiro de construção
├── images/          # prints do modelo e das páginas do dashboard
├── powerbi/         # arquivo .pbix
├── scripts/         # gerador da base fictícia
└── README.md
```

## Autor

**Daniel Martins**: 24 anos de experiência comercial e de relacionamento no setor financeiro, em formação em Análise e Desenvolvimento de Sistemas, com cursos de Power BI e modelagem de dados.
[LinkedIn](https://www.linkedin.com/in/danielfernandomartins)
