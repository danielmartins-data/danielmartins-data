-- Consultas de negócio sobre a base já limpa pelo pipeline (tabela: vendas_limpo)
-- Banco: SQLite. Rode com:  sqlite3 dados/comercial.db < src/kpis.sql

-- 1) Receita, pedidos e ticket médio por mês
SELECT mes,
       COUNT(DISTINCT id_pedido)          AS pedidos,
       ROUND(SUM(receita), 2)             AS receita,
       ROUND(SUM(receita) / COUNT(DISTINCT id_pedido), 2) AS ticket_medio
FROM vendas_limpo
GROUP BY mes
ORDER BY mes;

-- 2) Atingimento da meta por região (a meta é mensal por região)
WITH realizado AS (
    SELECT regiao, SUM(receita) AS receita
    FROM vendas_limpo
    WHERE regiao <> 'Não informada'
    GROUP BY regiao
),
meta AS (
    SELECT regiao, SUM(meta_receita) AS meta
    FROM (SELECT DISTINCT mes, regiao, meta_receita FROM vendas_limpo)
    GROUP BY regiao
)
SELECT r.regiao,
       ROUND(r.receita, 2)                       AS receita,
       ROUND(m.meta, 2)                          AS meta,
       ROUND(100.0 * r.receita / m.meta, 1)      AS atingimento_pct
FROM realizado r
JOIN meta m USING (regiao)
ORDER BY atingimento_pct DESC;

-- 3) Ranking de produtos com participação na receita (window function)
SELECT produto,
       SUM(quantidade)                                                  AS unidades,
       ROUND(SUM(receita), 2)                                           AS receita,
       ROUND(100.0 * SUM(receita) / SUM(SUM(receita)) OVER (), 1)        AS participacao_pct,
       RANK() OVER (ORDER BY SUM(receita) DESC)                          AS posicao
FROM vendas_limpo
GROUP BY produto
ORDER BY receita DESC;

-- 4) Clientes que mais gastaram e quanto representam do total (regra 80/20)
WITH por_cliente AS (
    SELECT nome, SUM(receita) AS receita
    FROM vendas_limpo
    WHERE nome_cliente_valido IS NOT NULL   -- só pedidos com cadastro identificado
    GROUP BY nome
)
SELECT nome,
       ROUND(receita, 2)                                                            AS receita,
       ROUND(100.0 * receita / SUM(receita) OVER (), 1)                             AS pct_do_total,
       ROUND(100.0 * SUM(receita) OVER (ORDER BY receita DESC)
             / SUM(receita) OVER (), 1)                                             AS pct_acumulado
FROM por_cliente
ORDER BY receita DESC
LIMIT 20;

-- 5) Devoluções por produto (qualidade e impacto financeiro)
SELECT produto,
       COUNT(*)                                                  AS pedidos,
       SUM(devolucao)                                            AS devolucoes,
       ROUND(100.0 * AVG(devolucao), 2)                          AS taxa_devolucao_pct,
       ROUND(SUM(receita * devolucao), 2)                        AS receita_devolvida
FROM vendas_limpo
GROUP BY produto
ORDER BY taxa_devolucao_pct DESC;

-- 6) Receita por canal e por mês (tabela dinâmica em SQL)
SELECT canal,
       ROUND(SUM(CASE WHEN mes BETWEEN '2025-01' AND '2025-06' THEN receita END), 2) AS s1_2025,
       ROUND(SUM(CASE WHEN mes BETWEEN '2025-07' AND '2025-12' THEN receita END), 2) AS s2_2025,
       ROUND(SUM(receita), 2)                                                        AS total
FROM vendas_limpo
GROUP BY canal
ORDER BY total DESC;
