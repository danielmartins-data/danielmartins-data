"""Gera o resultado de um teste A/B sintético (dados FICTÍCIOS).

Cenário: um e-commerce testa uma nova página de checkout (variante B) contra a
atual (controle A). Métricas: visita -> pedido (conversão) e receita.
O efeito real da variante B está embutido na geração (lift de +1,4 p.p. na
conversão) para que o teste estatístico tenha o que encontrar.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

VISITANTES_POR_DIA = 2200
DIAS = 21
TAXA_A = 0.0620          # conversão do controle
LIFT_B = 0.0140          # efeito verdadeiro da variante (1,4 ponto percentual)
TICKET_MEDIO = 187.00

linhas = []
inicio = pd.Timestamp("2026-03-02")
for dia in range(DIAS):
    data = inicio + pd.Timedelta(days=dia)
    for grupo, taxa in (("A", TAXA_A), ("B", TAXA_A + LIFT_B)):
        visitas = int(rng.normal(VISITANTES_POR_DIA / 2, 60))
        pedidos = int(rng.binomial(visitas, taxa))
        receita = float(np.sum(rng.lognormal(np.log(TICKET_MEDIO), 0.45, pedidos)))
        linhas.append({
            "data": data.date().isoformat(),
            "grupo": grupo,
            "visitantes": visitas,
            "pedidos": pedidos,
            "receita": round(receita, 2),
        })

df = pd.DataFrame(linhas)
df.to_csv("dados/experimento.csv", index=False)
print(f"{len(df)} linhas | visitantes: {df['visitantes'].sum():,} | pedidos: {df['pedidos'].sum():,}".replace(",", "."))
