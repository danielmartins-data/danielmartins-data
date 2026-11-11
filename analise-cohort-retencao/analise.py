"""Análise de coorte (retenção) de assinantes: SQL + matriz de retenção + LTV.

Entrada : dados/assinantes.csv   (dados SINTÉTICOS, gerados por gerar_dados.py)
Saídas  : dados/cohort_retencao.csv   matriz cohort x mês (valores em %)
          dados/cohort_tamanho.csv    quantos clientes entraram em cada cohort
          dados/retencao_por_plano.csv
          dados/retencao_por_canal.csv
          dados/resumo_ltv.csv
          graficos/*.png

Como rodar (a partir desta pasta):  python analise.py
"""
import sqlite3

import matplotlib
import pandas as pd

import matplotlib.pyplot as plt

matplotlib.use("Agg")

DATA_REF = "2025-12-31"   # data de referência da análise (fim do histórico)

# ---------------------------------------------------------------- 1) Dados
assinantes = pd.read_csv("dados/assinantes.csv", parse_dates=["data_entrada", "data_saida"])
print(f"Assinantes: {len(assinantes):,}".replace(",", "."))

con = sqlite3.connect(":memory:")
assinantes.assign(
    data_entrada=assinantes["data_entrada"].dt.strftime("%Y-%m-%d"),
    data_saida=assinantes["data_saida"].dt.strftime("%Y-%m-%d"),
).to_sql("assinantes", con, index=False)


def q(sql: str, **params) -> pd.DataFrame:
    return pd.read_sql(sql, con, params=params)


# ------------------------------------------------- 2) SQL: tamanho da coorte
tamanho = q(
    """
    SELECT strftime('%Y-%m', data_entrada) AS cohort,
           COUNT(*)                       AS clientes
    FROM assinantes
    GROUP BY cohort
    ORDER BY cohort
    """
)

# ------------------------------- 3) SQL: retenção por mês de vida (cohort x M)
# Um cliente está ativo no mês M se ainda não tinha cancelado no fim daquele mês.
# Só entram as coortes que já tiveram tempo de completar o mês M (senão a
# retenção subiria artificialmente nos meses recentes).
retencao = q(
    """
    WITH base AS (
        -- vida do cliente em dias inteiros desde o 1º dia do mês de entrada
        SELECT id_cliente,
               strftime('%Y-%m', data_entrada) AS cohort,
               CAST(julianday(:ref) - julianday(date(strftime('%Y-%m-01', data_entrada))) AS INT) AS dias_vida,
               data_saida
        FROM assinantes
    ),
    grade AS (
        -- para cada cliente, os meses de vida que ele já teve tempo de completar
        SELECT b.cohort, b.id_cliente, m.mes, b.dias_vida, b.data_saida
        FROM base b
        JOIN (SELECT DISTINCT dias_vida / 30 AS mes FROM base) m
          ON m.mes * 30 <= b.dias_vida
    )
    SELECT g.cohort,
           g.mes,
           COUNT(*)                                                          AS clientes,
           ROUND(100.0 * SUM(CASE WHEN g.data_saida IS NULL
                                   OR julianday(g.data_saida)
                                      > julianday(date(date(g.cohort || '-01'), '+'
                                          || ((g.mes + 1) * 30) || ' days'))
                                  THEN 1 ELSE 0 END) / COUNT(*), 1)       AS retencao_pct
    FROM grade g
    GROUP BY g.cohort, g.mes
    ORDER BY g.cohort, g.mes
    """,
    ref=DATA_REF,
)

matriz = retencao.pivot(index="cohort", columns="mes", values="retencao_pct")
matriz = matriz.reindex(sorted(matriz.index))
matriz.to_csv("dados/cohort_retencao.csv")
tamanho.to_csv("dados/cohort_tamanho.csv", index=False)

print("\n== Retenção média por mês de vida ==")
print(retencao.groupby("mes")["retencao_pct"].mean().round(1).head(12).to_string())

# ------------------------------------- 4) Retenção por plano e por canal (M3)
por_plano = q(
    """
    SELECT plano,
           COUNT(*)                                    AS clientes,
           ROUND(100.0 * AVG(data_saida IS NULL), 1)   AS ativos_pct,
           ROUND(AVG(CASE WHEN data_saida IS NULL THEN
                 julianday(:ref) - julianday(data_entrada)
                 ELSE julianday(data_saida) - julianday(data_entrada) END) / 30.44, 1) AS vida_media_meses
    FROM assinantes
    GROUP BY plano
    ORDER BY vida_media_meses DESC
    """,
    ref=DATA_REF,
)
por_canal = q(
    """
    SELECT canal_aquisicao,
           COUNT(*)                                    AS clientes,
           ROUND(100.0 * AVG(data_saida IS NULL), 1)   AS ativos_pct,
           ROUND(AVG(CASE WHEN data_saida IS NULL THEN
                 julianday(:ref) - julianday(data_entrada)
                 ELSE julianday(data_saida) - julianday(data_entrada) END) / 30.44, 1) AS vida_media_meses
    FROM assinantes
    GROUP BY canal_aquisicao
    ORDER BY vida_media_meses DESC
    """,
    ref=DATA_REF,
)
print("\n== Por plano ==\n" + por_plano.to_string(index=False))
print("\n== Por canal de aquisição ==\n" + por_canal.to_string(index=False))
por_plano.to_csv("dados/retencao_por_plano.csv", index=False)
por_canal.to_csv("dados/retencao_por_canal.csv", index=False)

# ---------------------------------------------- 5) LTV simples por segmento
# LTV = mensalidade média x vida média (meses). Churn mensal = 1 / vida média.
ltv = q(
    """
    SELECT plano,
           canal_aquisicao,
           COUNT(*)                            AS clientes,
           ROUND(AVG(mensalidade), 2)          AS mensalidade_media,
           ROUND(AVG(CASE WHEN data_saida IS NULL THEN
                 julianday(:ref) - julianday(data_entrada)
                 ELSE julianday(data_saida) - julianday(data_entrada) END) / 30.44, 1) AS vida_media_meses
    FROM assinantes
    GROUP BY plano, canal_aquisicao
    HAVING COUNT(*) >= 100
    ORDER BY vida_media_meses DESC
    """,
    ref=DATA_REF,
)
ltv["churn_mensal_pct"] = (100 / ltv["vida_media_meses"]).round(1)
ltv["ltv_estimado"] = (ltv["mensalidade_media"] * ltv["vida_media_meses"]).round(2)
ltv.to_csv("dados/resumo_ltv.csv", index=False)
print("\n== LTV estimado por plano x canal ==\n" + ltv.to_string(index=False))

# ------------------------------------------------------------- 6) Gráficos
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})

fig, ax = plt.subplots(figsize=(11, 6))
dados = matriz.iloc[:, 1:13]   # mês 0 não entra: a retenção parte do mês 1
im = ax.imshow(dados.values, cmap="Blues", vmin=0, vmax=100, aspect="auto")
ax.set_xticks(range(dados.shape[1]), dados.columns)
ax.set_yticks(range(len(dados)), dados.index, fontsize=8)
for i in range(dados.shape[0]):
    for j in range(dados.shape[1]):
        v = dados.values[i, j]
        if pd.notna(v):
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7,
                    color="white" if v > 55 else "#1f3864")
ax.set_xlabel("meses desde a entrada"); ax.set_ylabel("cohort (mês de entrada)")
ax.set_title("Retenção por coorte: % de clientes ainda ativos no mês N")
fig.colorbar(im, ax=ax, shrink=.8, label="%")
fig.tight_layout(); fig.savefig("graficos/cohort_retencao.png", dpi=150); plt.close()

media = retencao.groupby("mes")["retencao_pct"].mean().head(12)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(media.index, media.values, marker="o", color="#1f77b4")
ax.set_title("Curva de retenção média (todos os planos)")
ax.set_xlabel("meses desde a entrada"); ax.set_ylabel("% ainda ativos"); ax.set_ylim(0, 100)
ax.grid(axis="y", alpha=.3)
fig.tight_layout(); fig.savefig("graficos/curva_retencao.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(por_canal["canal_aquisicao"], por_canal["vida_media_meses"], color="#0FA3B1")
ax.set_title("Vida média do cliente por canal de aquisição (meses)")
fig.tight_layout(); fig.savefig("graficos/vida_media_canal.png", dpi=150); plt.close()

print("\nArquivos gravados em dados/ e graficos/.")
