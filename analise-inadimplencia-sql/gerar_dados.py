"""Cria um banco SQLite SINTÉTICO (fictício) de empréstimos para praticar SQL analítico."""
import sqlite3
import numpy as np
import pandas as pd

rng = np.random.default_rng(11)
N = 4000

produto = rng.choice(["Consignado", "Crédito Pessoal", "Cartão", "Financiamento Veículo"], N,
                     p=[0.35, 0.30, 0.20, 0.15])
faixa_score = rng.choice(["A (alto)", "B", "C", "D (baixo)"], N, p=[0.25, 0.35, 0.28, 0.12])
valor = (rng.lognormal(8.8, 0.7, N) * np.select(
    [produto == "Financiamento Veículo", produto == "Consignado"], [6, 1.5], 1)).round(2)
data = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 330, N), unit="D")

base = {"Consignado": -3.6, "Crédito Pessoal": -2.2, "Cartão": -2.0, "Financiamento Veículo": -2.8}
risco = {"A (alto)": -1.2, "B": -0.2, "C": 0.7, "D (baixo)": 1.6}
z = np.array([base[p] + risco[f] for p, f in zip(produto, faixa_score)])
inad = rng.random(N) < 1 / (1 + np.exp(-z))
dias_atraso = np.where(inad, rng.integers(91, 400, N),
                       np.where(rng.random(N) < 0.2, rng.integers(1, 60, N), 0))

df = pd.DataFrame({
    "id_emprestimo": np.arange(1, N + 1),
    "data_contratacao": data.strftime("%Y-%m-%d"),
    "produto": produto,
    "faixa_score": faixa_score,
    "valor": valor,
    "dias_atraso": dias_atraso,
})
con = sqlite3.connect("dados/credito.db")
df.to_sql("emprestimos", con, if_exists="replace", index=False)
con.close()
df.to_csv("dados/emprestimos.csv", index=False)
print(f"{len(df)} empréstimos gravados em dados/credito.db")
