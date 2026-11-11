"""Segmentação RFM em Python — equivalente ao analise_rfm.R, para quem não tem R.

Motivo: o projeto em R exige o R instalado. Este script entrega o mesmo
resultado (mesmas notas por quintil e mesmos 7 segmentos + "Sem compras")
usando só pandas, e é o que os testes automatizados executam.

Saída: dados/rfm_clientes.csv e dados/resumo_segmentos.csv
(gravados em dados/python/ para não sobrescrever a saída oficial do R)

Como rodar (a partir desta pasta): python gerar_rfm.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SAIDA = Path("dados/python")
SAIDA.mkdir(parents=True, exist_ok=True)
DATA_REF = pd.Timestamp("2025-12-31")

transacoes = pd.read_csv("dados/fato_transacoes.csv", parse_dates=["Data"])
clientes = pd.read_csv("dados/dim_cliente.csv")
clientes = clientes.rename(columns={"Segmento": "Segmento_Cliente"})

# ------------------------------------------------------- 1) R, F e M
rfm = (transacoes.groupby("id_cliente")
       .agg(Ultima_Compra=("Data", "max"),
            Frequencia=("Valor", "size"),
            Valor_Total=("Valor", "sum"),
            Gerente=("Gerente", "first"))
       .reset_index())
rfm["Valor_Total"] = rfm["Valor_Total"].round(2)
rfm["Recencia_Dias"] = (DATA_REF - rfm["Ultima_Compra"]).dt.days
rfm["Ticket_Medio"] = (rfm["Valor_Total"] / rfm["Frequencia"]).round(2)


# --------------------------------------------- 2) Notas de 1 a 5 (quintis)
def nota_quintil(serie: pd.Series, inverter: bool = False) -> pd.Series:
    """Mesma fórmula do script em R: ceiling(5 * rank / n), empates com a média."""
    nota = np.ceil(5 * serie.rank(method="average") / len(serie)).astype(int).clip(1, 5)
    return (6 - nota) if inverter else nota


rfm["R"] = nota_quintil(rfm["Recencia_Dias"], inverter=True)   # menos dias = melhor
rfm["F"] = nota_quintil(rfm["Frequencia"])
rfm["M"] = nota_quintil(rfm["Valor_Total"])
rfm["Score_RFM"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)


# ------------------------------------------------- 3) Regras de segmento
def segmentar(r: int, f: int, m: int) -> str:
    """A ordem é a mesma do script em R: a regra mais abaixo prevalece."""
    segmento = "Precisam de Atenção"
    if r <= 2 and f <= 2:
        segmento = "Hibernando"
    if r >= 4 and f <= 2:
        segmento = "Novos e Promissores"
    if r <= 2 and f >= 3:
        segmento = "Em Risco"
    if r <= 2 and m >= 4:
        segmento = "Grandes Valores em Risco"
    if r >= 3 and f >= 4:
        segmento = "Fiéis"
    if r >= 4 and f >= 4 and m >= 4:
        segmento = "Campeões"
    return segmento


rfm["Segmento_RFM"] = [segmentar(r, f, m) for r, f, m in zip(rfm["R"], rfm["F"], rfm["M"])]

# clientes do cadastro que não compraram no ano
sem_compra = clientes.loc[~clientes["id_cliente"].isin(rfm["id_cliente"]), ["id_cliente"]].copy()
sem_compra = sem_compra.assign(Segmento_RFM="Sem compras em 2025", Recencia_Dias=np.nan,
                               Frequencia=0, Valor_Total=0.0)
base = pd.concat([rfm, sem_compra], ignore_index=True)

# ---------------------------------------------------------- 4) Resumo
resumo = (base.groupby("Segmento_RFM")
          .agg(Clientes=("id_cliente", "nunique"),
               Valor_Total=("Valor_Total", "sum"),
               Recencia_Media_Dias=("Recencia_Dias", "mean"),
               Frequencia_Media=("Frequencia", "mean"))
          .reset_index())
resumo["Pct_Clientes"] = (resumo["Clientes"] / resumo["Clientes"].sum() * 100).round(1)
resumo["Pct_Valor"] = (resumo["Valor_Total"] / resumo["Valor_Total"].sum() * 100).round(1)
resumo["Valor_Medio_Cliente"] = (resumo["Valor_Total"] / resumo["Clientes"]).round(2)
resumo["Recencia_Media_Dias"] = resumo["Recencia_Media_Dias"].round(0)
resumo["Frequencia_Media"] = resumo["Frequencia_Media"].round(1)
resumo["Valor_Total"] = resumo["Valor_Total"].round(2)
resumo = resumo.sort_values("Valor_Total", ascending=False)

base.to_csv(SAIDA / "rfm_clientes.csv", index=False)
resumo.to_csv(SAIDA / "resumo_segmentos.csv", index=False)

print(f"Clientes segmentados: {len(base)} | valor total: R$ {base['Valor_Total'].sum():,.2f}")
print(resumo[["Segmento_RFM", "Clientes", "Pct_Clientes", "Pct_Valor"]].to_string(index=False))
print(f"\nSaída em {SAIDA}/")
