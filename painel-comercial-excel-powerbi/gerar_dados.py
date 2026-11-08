"""Gera dados SINTÉTICOS (fictícios) de metas x realizado de uma equipe comercial (2025)
e as tabelas no formato de modelo estrela para o Power BI. Seed fixa => reproduzível."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(2025)

gerentes = {  # nome: (região, fator de desempenho)
    "Ana Souza": ("Sudeste", 1.08), "Bruno Lima": ("Sudeste", 0.97),
    "Carla Mendes": ("Sul", 1.03), "Diego Rocha": ("Sul", 0.88),
    "Elisa Prado": ("Nordeste", 1.12), "Fábio Torres": ("Nordeste", 0.94),
    "Gabriela Nunes": ("Centro-Oeste", 1.00), "Heitor Alves": ("Norte", 0.91),
}
produtos = {"Crédito": 120_000, "Seguros": 60_000, "Cartões": 80_000, "Consórcios": 100_000}
sazonal = np.array([0.95, 0.9, 1.0, 1.0, 1.02, 1.0, 1.03, 1.0, 1.0, 1.05, 1.12, 1.2])

linhas = []
for mes in range(12):
    data = pd.Timestamp(2025, mes + 1, 1)
    for g, (reg, fator) in gerentes.items():
        for p, base in produtos.items():
            meta = round(base * (1 + 0.01 * mes) * rng.uniform(0.9, 1.1), -2)
            real = round(meta * fator * sazonal[mes] * rng.normal(1, 0.08), -2)
            linhas.append((data.date(), g, reg, p, meta, real))

fato = pd.DataFrame(linhas, columns=["Mes", "Gerente", "Regiao", "Produto", "Meta", "Realizado"])
fato.to_csv("dados/vendas_metas.csv", index=False)

# Modelo estrela para Power BI
fato[["Mes", "Gerente", "Produto", "Meta", "Realizado"]].to_csv("dados/fato_vendas.csv", index=False)
pd.DataFrame([(g, r) for g, (r, _) in gerentes.items()], columns=["Gerente", "Regiao"]).to_csv("dados/dim_gerente.csv", index=False)
pd.DataFrame({"Produto": list(produtos), "Ordem": range(1, 5)}).to_csv("dados/dim_produto.csv", index=False)
cal = pd.DataFrame({"Data": pd.date_range("2025-01-01", "2025-12-31")})
cal["Ano"] = cal.Data.dt.year
cal["MesNum"] = cal.Data.dt.month
cal["Mes"] = cal.Data.dt.strftime("%b")
cal["Trimestre"] = "T" + cal.Data.dt.quarter.astype(str)
cal.to_csv("dados/dim_calendario.csv", index=False)

print(len(fato), "linhas | meta total:", fato.Meta.sum(), "| realizado:", fato.Realizado.sum(),
      "| ating.: %.1f%%" % (100 * fato.Realizado.sum() / fato.Meta.sum()))
