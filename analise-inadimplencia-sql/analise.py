"""Executa as consultas de consultas.sql e gera gráficos."""
import re
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = sqlite3.connect("dados/credito.db")
texto = open("consultas.sql", encoding="utf-8").read()
consultas = [c.strip() for c in re.split(r";\s*\n", texto) if "SELECT" in c or "WITH" in c]
nomes = ["visao_geral", "por_produto", "por_score", "safra_mensal", "ranking_produto_score", "concentracao"]
r = {n: pd.read_sql(re.sub(r"(?m)^--.*\n", "", c), con) for n, c in zip(nomes, consultas)}
for n, t in r.items():
    print(f"\n== {n} ==\n{t.to_string(index=False)}")
    t.to_csv(f"dados/resultado_{n}.csv", index=False)

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 11})
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
ax[0].bar(r["por_produto"]["produto"], r["por_produto"]["inad_pct"], color="#1f77b4")
ax[0].set_title("Inadimplência > 90 dias por produto (%)"); ax[0].tick_params(axis="x", rotation=20)
ax[1].bar(r["por_score"]["faixa_score"], r["por_score"]["inad_pct"], color="#d62728")
ax[1].set_title("Inadimplência por faixa de score (%)")
fig.tight_layout(); fig.savefig("graficos/inadimplencia_produto_score.png", dpi=150); plt.close()

s = r["safra_mensal"]
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(s["mes"], s["inad_pct"], marker="o", alpha=.5, label="Mensal")
ax.plot(s["mes"], s["media_movel_3m"], lw=2.5, label="Média móvel 3m")
ax.set_title("Inadimplência por safra de contratação (%)"); ax.legend(); plt.xticks(rotation=45)
fig.tight_layout(); fig.savefig("graficos/inadimplencia_safra.png", dpi=150); plt.close()
