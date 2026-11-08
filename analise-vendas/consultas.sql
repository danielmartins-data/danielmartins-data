-- Consultas SQL usadas na análise (SQLite). Tabela: vendas

-- 1) Receita total e ticket médio
SELECT ROUND(SUM(receita), 2) AS receita_total,
       ROUND(AVG(receita), 2) AS ticket_medio,
       COUNT(*)               AS pedidos
FROM vendas;

-- 2) Receita por mês
SELECT strftime('%Y-%m', data) AS mes,
       ROUND(SUM(receita), 2)  AS receita
FROM vendas
GROUP BY mes
ORDER BY mes;

-- 3) Receita e participação por região
SELECT regiao,
       ROUND(SUM(receita), 2) AS receita,
       ROUND(100.0 * SUM(receita) / (SELECT SUM(receita) FROM vendas), 1) AS pct
FROM vendas
GROUP BY regiao
ORDER BY receita DESC;

-- 4) Top produtos por receita
SELECT produto,
       SUM(quantidade)        AS unidades,
       ROUND(SUM(receita), 2) AS receita
FROM vendas
GROUP BY produto
ORDER BY receita DESC;

-- 5) Receita por canal
SELECT canal,
       COUNT(*)               AS pedidos,
       ROUND(SUM(receita), 2) AS receita,
       ROUND(AVG(receita), 2) AS ticket_medio
FROM vendas
GROUP BY canal
ORDER BY receita DESC;
