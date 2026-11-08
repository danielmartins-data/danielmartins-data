"""Gera base SINTÉTICA (fictícia) de clientes de um banco para análise de churn."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
N = 3000

segmento = rng.choice(["Varejo", "Prime", "Exclusive"], N, p=[0.65, 0.25, 0.10])
meses = rng.integers(1, 180, N)
produtos = np.clip(rng.poisson(2.2, N) + 1, 1, 7)
app = rng.random(N) < np.where(segmento == "Varejo", 0.55, 0.75)
reclam = rng.poisson(0.5, N)
saldo = (rng.lognormal(7.5, 1.0, N) * np.select(
    [segmento == "Varejo", segmento == "Prime"], [1, 3], 8)).round(2)

# Probabilidade de churn: cai com mais produtos, uso do app e tempo de casa; sobe com reclamações
z = (-0.4 - 0.45 * (produtos - 2) - 0.8 * app + 0.7 * reclam - 0.008 * meses)
p = 1 / (1 + np.exp(-z))
churn = rng.random(N) < p

df = pd.DataFrame({
    "id_cliente": np.arange(1, N + 1),
    "segmento": segmento,
    "meses_relacionamento": meses,
    "qtd_produtos": produtos,
    "usa_app": app.astype(int),
    "reclamacoes_12m": reclam,
    "saldo_medio": saldo,
    "churn": churn.astype(int),
})
df.to_csv("dados/clientes.csv", index=False)
print(f"{len(df)} clientes gerados | churn geral: {df.churn.mean():.1%}")
