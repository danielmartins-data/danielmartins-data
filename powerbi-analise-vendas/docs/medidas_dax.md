# Medidas DAX

Crie uma tabela vazia chamada `_Medidas` (Página Inicial → Inserir Dados → tabela vazia) e guarde todas as medidas nela.

## Tabela Calendário

```dax
dCalendario =
ADDCOLUMNS(
    CALENDAR(DATE(2024, 1, 1), DATE(2025, 12, 31)),
    "Ano", YEAR([Date]),
    "Mes", MONTH([Date]),
    "NomeMes", FORMAT([Date], "mmm"),
    "AnoMes", FORMAT([Date], "yyyy-mm"),
    "Trimestre", "T" & QUARTER([Date])
)
```

Depois: marcar como tabela de datas e ordenar `NomeMes` por `Mes`.

## Medidas base

```dax
Receita = SUM(fVendas[receita])

Custo = SUM(fVendas[custo])

Margem Bruta = [Receita] - [Custo]

Margem % = DIVIDE([Margem Bruta], [Receita])

Qtd Vendas = COUNTROWS(fVendas)

Ticket Médio = DIVIDE([Receita], [Qtd Vendas])

Clientes Ativos = DISTINCTCOUNT(fVendas[id_cliente])

Desconto Médio % = AVERAGE(fVendas[desconto_pct])
```

## Meta e atingimento

```dax
Meta = SUM(fMetas[meta_receita])

Atingimento % = DIVIDE([Receita], [Meta])

Gap para Meta = [Receita] - [Meta]
```

## Inteligência de tempo

```dax
Receita Ano Anterior =
CALCULATE([Receita], SAMEPERIODLASTYEAR(dCalendario[Date]))

Crescimento YoY % =
DIVIDE([Receita] - [Receita Ano Anterior], [Receita Ano Anterior])

Receita Acumulada no Ano =
TOTALYTD([Receita], dCalendario[Date])
```

## Análise de carteira

```dax
Receita Total Geral =
CALCULATE([Receita], ALL(dClientes))

% do Total = DIVIDE([Receita], [Receita Total Geral])

Receita Top 10 Clientes =
CALCULATE(
    [Receita],
    TOPN(10, ALL(dClientes[id_cliente]), [Receita])
)
```

## Formatação condicional (dica)

Use `Atingimento %` para colorir cartões e tabelas: verde ≥ 100%, amarelo 85%–99%, vermelho < 85%.
