"""Gera um conjunto de dados SINTÉTICO de vendas (fictício) para o projeto.

Os dados não são de nenhuma empresa real. Seed fixa => resultado reproduzível.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 2000

produtos = {
    "Notebook": 3500, "Monitor": 900, "Teclado": 150,
    "Mouse": 80, "Headset": 250, "Webcam": 200,
}
regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
canais = ["Online", "Loja física", "Televendas"]

datas = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, N), unit="D")
prod = rng.choice(list(produtos), N, p=[0.12, 0.15, 0.22, 0.25, 0.15, 0.11])
preco = np.array([produtos[p] for p in prod]) * rng.uniform(0.9, 1.1, N)

df = pd.DataFrame({
    "id_pedido": np.arange(1, N + 1),
    "data": datas,
    "regiao": rng.choice(regioes, N, p=[0.38, 0.22, 0.2, 0.12, 0.08]),
    "canal": rng.choice(canais, N, p=[0.5, 0.35, 0.15]),
    "produto": prod,
    "quantidade": rng.integers(1, 6, N),
    "preco_unitario": preco.round(2),
})

# Sazonalidade: mais pedidos repetidos em nov/dez (Black Friday e Natal)
extra = df[df["data"].dt.month.isin([11, 12])].sample(frac=0.35, random_state=1).copy()
extra["id_pedido"] = np.arange(N + 1, N + 1 + len(extra))
df = pd.concat([df, extra]).sort_values("data").reset_index(drop=True)
df["id_pedido"] = np.arange(1, len(df) + 1)
df["data"] = df["data"].dt.date

# Sujeira proposital para demonstrar limpeza: duplicados e nulos
sujo = pd.concat([df, df.sample(15, random_state=3)])
sujo.loc[sujo.sample(25, random_state=5).index, "regiao"] = None
sujo.to_csv("dados/vendas_bruto.csv", index=False)
print(f"{len(sujo)} linhas geradas em dados/vendas_bruto.csv")
