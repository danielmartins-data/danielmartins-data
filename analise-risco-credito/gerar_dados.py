"""Gera a base de clientes com churn observado (dados FICTÍCIOS).

Mesma carteira do projeto analise-churn-clientes (3.000 clientes de um banco),
regravada aqui para que este projeto rode sozinho: quem clonar o repositório
não precisa executar outro projeto antes.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 3000

segmento = rng.choice(["Varejo", "Prime", "Exclusive"], n, p=[.6, .28, .12])
meses = rng.integers(1, 200, n)
qtd_produtos = rng.choice([1, 2, 3, 4, 5], n, p=[.34, .27, .18, .13, .08])
usa_app = rng.binomial(1, np.where(segmento == "Varejo", .55, .78), n)
reclamacoes = rng.poisson(np.where(segmento == "Varejo", .5, .28), n)
saldo = np.round(rng.lognormal(8.6, .75, n), 2)

# efeito real (log-odds): cada fator aumenta o risco; o saldo reduz
risco = (-3.10 + 1.05 * (qtd_produtos <= 2) + 1.20 * (usa_app == 0)
         + 0.75 * reclamacoes + 0.95 * (meses < 12) - 0.35 * (saldo - 5000) / 8000
         + 0.15 * (segmento == "Varejo"))
churn = rng.binomial(1, 1 / (1 + np.exp(-risco)))

df = pd.DataFrame({
    "id_cliente": np.arange(1, n + 1),
    "segmento": segmento,
    "meses_relacionamento": meses,
    "qtd_produtos": qtd_produtos,
    "usa_app": usa_app,
    "reclamacoes_12m": reclamacoes,
    "saldo_medio": saldo,
    "churn": churn,
})
df.to_csv("dados/clientes.csv", index=False)
print(f"{len(df)} clientes | churn observado: {df.churn.mean():.1%}")
