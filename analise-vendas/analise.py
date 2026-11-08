"""Limpeza, análise em SQL (SQLite) e gráficos das vendas sintéticas de 2025."""
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 1) Limpeza ---------------------------------------------------------------
df = pd.read_csv("dados/vendas_bruto.csv", parse_dates=["data"])
print(f"Linhas brutas: {len(df)}")
df = df.drop_duplicates(subset="id_pedido")
df["regiao"] = df["regiao"].fillna("Não informada")
df["receita"] = (df["quantidade"] * df["preco_unitario"]).round(2)
print(f"Linhas após limpeza: {len(df)}")
df.to_csv("dados/vendas_limpo.csv", index=False)

# 2) SQL -------------------------------------------------------------------
con = sqlite3.connect(":memory:")
df.assign(data=df["data"].dt.strftime("%Y-%m-%d")).to_sql("vendas", con, index=False)

def q(sql):
    return pd.read_sql(sql, con)

resumo = q("SELECT ROUND(SUM(receita),2) receita_total, ROUND(AVG(receita),2) ticket_medio, COUNT(*) pedidos FROM vendas")
mensal = q("SELECT strftime('%Y-%m', data) mes, ROUND(SUM(receita),2) receita FROM vendas GROUP BY mes ORDER BY mes")
regiao = q("""SELECT regiao, ROUND(SUM(receita),2) receita,
              ROUND(100.0*SUM(receita)/(SELECT SUM(receita) FROM vendas),1) pct
              FROM vendas GROUP BY regiao ORDER BY receita DESC""")
produto = q("SELECT produto, SUM(quantidade) unidades, ROUND(SUM(receita),2) receita FROM vendas GROUP BY produto ORDER BY receita DESC")
canal = q("SELECT canal, COUNT(*) pedidos, ROUND(SUM(receita),2) receita, ROUND(AVG(receita),2) ticket_medio FROM vendas GROUP BY canal ORDER BY receita DESC")

for nome, t in [("Resumo", resumo), ("Por região", regiao), ("Por produto", produto), ("Por canal", canal)]:
    print(f"\n== {nome} ==\n{t.to_string(index=False)}")

# 3) Gráficos --------------------------------------------------------------
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 11})
cor = "#1f77b4"

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(mensal["mes"], mensal["receita"] / 1e3, marker="o", color=cor)
ax.set_title("Receita mensal (R$ mil) - 2025")
ax.set_ylabel("R$ mil")
plt.xticks(rotation=45)
fig.tight_layout(); fig.savefig("graficos/receita_mensal.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(produto["produto"][::-1], produto["receita"][::-1] / 1e3, color=cor)
ax.set_title("Receita por produto (R$ mil)")
fig.tight_layout(); fig.savefig("graficos/receita_produto.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(regiao["regiao"], regiao["receita"] / 1e3, color=cor)
ax.set_title("Receita por região (R$ mil)")
fig.tight_layout(); fig.savefig("graficos/receita_regiao.png", dpi=150); plt.close()
