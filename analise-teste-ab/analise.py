"""Teste A/B de conversão: quem ganhou, por quanto, e isso é estatisticamente real?

Entrada : dados/experimento.csv   (dados SINTÉTICOS, gerados por gerar_dados.py)
Saídas  : dados/resumo_por_grupo.csv, dados/resultado_teste.csv
          graficos/conversao_por_grupo.png, graficos/conversao_diaria.png,
          graficos/ganho_acumulado.png

Métodos: teste z para duas proporções, intervalo de confiança de 95% para o
lift absoluto, tamanho de amostra necessário e ganho estimado em receita.
Sem dependências além de pandas, numpy e matplotlib.

Como rodar (a partir desta pasta): python analise.py
"""
import math

import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

ALFA = 0.05
Z_ALFA_2 = 1.959963985          # 1,96: 95% de confiança (bilateral)
Z_BETA_80 = 0.841621234         # poder de 80%

df = pd.read_csv("dados/experimento.csv", parse_dates=["data"])

# --------------------------------------------------- 1) Resumo por grupo
resumo = (df.groupby("grupo")[["visitantes", "pedidos", "receita"]].sum()
            .assign(taxa_conversao=lambda d: d["pedidos"] / d["visitantes"],
                    ticket_medio=lambda d: d["receita"] / d["pedidos"],
                    receita_por_visitante=lambda d: d["receita"] / d["visitantes"]))
print("== Resumo por grupo ==")
print(resumo.assign(taxa_conversao=lambda d: (d.taxa_conversao * 100).round(2),
                    ticket_medio=lambda d: d.ticket_medio.round(2),
                    receita_por_visitante=lambda d: d.receita_por_visitante.round(2)).to_string())
resumo.round(6).to_csv("dados/resumo_por_grupo.csv")

n_a, x_a = resumo.loc["A", ["visitantes", "pedidos"]]
n_b, x_b = resumo.loc["B", ["visitantes", "pedidos"]]
p_a, p_b = x_a / n_a, x_b / n_b

# ------------------------------ 2) Teste z para duas proporções (bilateral)
p_pool = (x_a + x_b) / (n_a + n_b)
erro_padrao = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
z = (p_b - p_a) / erro_padrao
p_valor = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))   # cauda normal

lift_abs = p_b - p_a
lift_rel = lift_abs / p_a
ic_baixo = lift_abs - Z_ALFA_2 * math.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
ic_alto = lift_abs + Z_ALFA_2 * math.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)

# ------------------------- 3) Tamanho de amostra para detectar esse efeito
# n = 2 * (z_alfa/2 + z_beta)^2 * p(1-p) / efeito^2   (por grupo)
p_medio = (p_a + p_b) / 2
n_necessario = math.ceil(2 * (Z_ALFA_2 + Z_BETA_80) ** 2 * p_medio * (1 - p_medio) / lift_abs ** 2)

# ------------------------------------- 4) Impacto estimado em receita/ano
receita_por_visitante_a = resumo.loc["A", "receita_por_visitante"]
receita_por_visitante_b = resumo.loc["B", "receita_por_visitante"]
visitantes_ano = int(resumo["visitantes"].sum() / df["data"].dt.date.nunique() * 365)
ganho_ano = (receita_por_visitante_b - receita_por_visitante_a) * visitantes_ano

resultado = pd.DataFrame([{
    "grupo_controle": "A", "grupo_teste": "B",
    "visitantes_A": int(n_a), "visitantes_B": int(n_b),
    "conversao_A_pct": round(p_a * 100, 2), "conversao_B_pct": round(p_b * 100, 2),
    "lift_absoluto_pct": round(lift_abs * 100, 2),
    "lift_relativo_pct": round(lift_rel * 100, 1),
    "z": round(z, 3), "p_valor": round(p_valor, 5),
    "ic95_lift_pct": f"[{ic_baixo * 100:.2f}; {ic_alto * 100:.2f}]",
    "significante_5pct": "sim" if p_valor < ALFA else "não",
    "amostra_necessaria_por_grupo": n_necessario,
    "ganho_estimado_receita_ano": round(ganho_ano, 2),
    "visitantes_por_ano_projetados": visitantes_ano,
}])
resultado.to_csv("dados/resultado_teste.csv", index=False)
print("\n== Resultado do teste ==")
print(resultado.T.to_string(header=False))

# ------------------------------------------------- 5) Conversão diária
diaria = (df.groupby(["data", "grupo"])[["visitantes", "pedidos"]].sum()
            .assign(taxa=lambda d: d["pedidos"] / d["visitantes"] * 100)
            .reset_index())
piv = diaria.pivot(index="data", columns="grupo", values="taxa")

# ------------------------------------ 6) Ganho acumulado (visão sequencial)
cum = (df.sort_values("data").groupby("grupo")[["visitantes", "pedidos"]].cumsum())
cum["grupo"] = df.sort_values("data")["grupo"].values
cum["data"] = df.sort_values("data")["data"].values
acum = (cum.groupby(["data", "grupo"])[["visitantes", "pedidos"]].last()
           .assign(taxa=lambda d: d["pedidos"] / d["visitantes"] * 100)
           .reset_index()
           .pivot(index="data", columns="grupo", values="taxa"))

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})

fig, ax = plt.subplots(figsize=(6.5, 4.2))
barras = ax.bar(["A (controle)", "B (nova página)"], [p_a * 100, p_b * 100], color=["#8c8c8c", "#1f77b4"])
for b, v in zip(barras, [p_a * 100, p_b * 100]):
    ax.text(b.get_x() + b.get_width() / 2, v + .08, f"{v:.2f}%", ha="center", fontweight="bold")
ax.set_ylabel("taxa de conversão (%)"); ax.set_ylim(0, max(p_a, p_b) * 100 * 1.25)
ax.set_title(f"Conversão: A {p_a:.2%} x B {p_b:.2%} (p = {p_valor:.4f})")
fig.tight_layout(); fig.savefig("graficos/conversao_por_grupo.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(piv.index, piv["A"], marker="o", ms=4, label="A (controle)", color="#8c8c8c")
ax.plot(piv.index, piv["B"], marker="o", ms=4, label="B (nova página)", color="#1f77b4")
ax.axhline(p_a * 100, color="#8c8c8c", ls=":", lw=1)
ax.axhline(p_b * 100, color="#1f77b4", ls=":", lw=1)
ax.set_title("Conversão diária por grupo (%)"); ax.set_ylabel("%"); ax.legend()
plt.xticks(rotation=45)
fig.tight_layout(); fig.savefig("graficos/conversao_diaria.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(acum.index, acum["A"], lw=2, label="A (controle)", color="#8c8c8c")
ax.plot(acum.index, acum["B"], lw=2, label="B (nova página)", color="#1f77b4")
ax.set_title("Conversão acumulada: o teste fica estável com o tempo")
ax.set_ylabel("% acumulado"); ax.legend()
plt.xticks(rotation=45)
fig.tight_layout(); fig.savefig("graficos/ganho_acumulado.png", dpi=150); plt.close()

print("\nArquivos gravados em dados/ e graficos/.")
