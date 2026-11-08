-- Definição: inadimplente = dias_atraso > 90.  Banco: SQLite, tabela: emprestimos

-- 1) Visão geral da carteira
SELECT COUNT(*)                                             AS contratos,
       ROUND(SUM(valor), 2)                                 AS carteira,
       ROUND(100.0 * AVG(dias_atraso > 90), 2)              AS inad_contratos_pct,
       ROUND(100.0 * SUM(CASE WHEN dias_atraso > 90 THEN valor END) / SUM(valor), 2) AS inad_valor_pct
FROM emprestimos;

-- 2) Inadimplência por produto
SELECT produto,
       COUNT(*)                                AS contratos,
       ROUND(SUM(valor), 2)                    AS carteira,
       ROUND(100.0 * AVG(dias_atraso > 90), 2) AS inad_pct
FROM emprestimos
GROUP BY produto
ORDER BY inad_pct DESC;

-- 3) Inadimplência por faixa de score
SELECT faixa_score,
       COUNT(*)                                AS contratos,
       ROUND(100.0 * AVG(dias_atraso > 90), 2) AS inad_pct
FROM emprestimos
GROUP BY faixa_score
ORDER BY inad_pct;

-- 4) Safra mensal com CTE e window function (média móvel de 3 meses)
WITH safra AS (
    SELECT strftime('%Y-%m', data_contratacao)      AS mes,
           COUNT(*)                                 AS contratos,
           100.0 * AVG(dias_atraso > 90)            AS inad_pct
    FROM emprestimos
    GROUP BY mes
)
SELECT mes, contratos,
       ROUND(inad_pct, 2) AS inad_pct,
       ROUND(AVG(inad_pct) OVER (ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS media_movel_3m
FROM safra
ORDER BY mes;

-- 5) Ranking: pior faixa de score dentro de cada produto (RANK + PARTITION BY)
WITH t AS (
    SELECT produto, faixa_score,
           COUNT(*) AS contratos,
           100.0 * AVG(dias_atraso > 90) AS inad_pct
    FROM emprestimos
    GROUP BY produto, faixa_score
)
SELECT produto, faixa_score, contratos, ROUND(inad_pct, 2) AS inad_pct,
       RANK() OVER (PARTITION BY produto ORDER BY inad_pct DESC) AS ranking
FROM t
ORDER BY produto, ranking;

-- 6) Concentração: quanto da carteira inadimplente vem dos 10% maiores contratos?
WITH inad AS (
    SELECT valor, NTILE(10) OVER (ORDER BY valor DESC) AS decil
    FROM emprestimos WHERE dias_atraso > 90
)
SELECT decil, COUNT(*) AS contratos, ROUND(SUM(valor), 2) AS valor_inadimplente,
       ROUND(100.0 * SUM(valor) / (SELECT SUM(valor) FROM inad), 1) AS pct_do_total
FROM inad
GROUP BY decil
ORDER BY decil;
