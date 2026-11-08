"""Análise descritiva de churn: quem sai, e o que tem em comum."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("dados/clientes.csv")
geral = df["churn"].mean()
print(f"Clientes: {len(df)} | Churn geral: {geral:.1%}")

def taxa(col):
    t = df.groupby(col)["churn"].agg(clientes="count", churn="mean").round(3)
    t["churn_pct"] = (t["churn"] * 100).round(1)
    return t.drop(columns="churn")

df["faixa_produtos"] = pd.cut(df["qtd_produtos"], [0, 1, 2, 3, 4, 10],
                              labels=["1", "2", "3", "4", "5+"])
df["faixa_tempo"] = pd.cut(df["meses_relacionamento"], [0, 12, 36, 84, 200],
                           labels=["até 1 ano", "1-3 anos", "3-7 anos", "7+ anos"])
df["reclamou"] = df["reclamacoes_12m"].clip(upper=2).map({0: "0", 1: "1", 2: "2+"})

cortes = {
    "segmento": "segmento", "qtd. de produtos": "faixa_produtos", "usa app": "usa_app",
    "reclamações (12m)": "reclamou", "tempo de relacionamento": "faixa_tempo",
}
res = {nome: taxa(col) for nome, col in cortes.items()}
for nome, t in res.items():
    print(f"\n== Churn por {nome} ==\n{t.to_string()}")

# Lista de prioridade: clientes ativos de maior risco (regra simples e explicável)
risco = ((df["qtd_produtos"] <= 2).astype(int) + (df["usa_app"] == 0).astype(int)
         + (df["reclamacoes_12m"] >= 1).astype(int))
df["score_risco"] = risco
print("\n== Churn por score de risco (0 a 3) ==")
sr = taxa("score_risco"); print(sr.to_string())
df.to_csv("dados/clientes_com_risco.csv", index=False)

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 11})
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), sharey=True)
for ax, nome in zip(axes, ["qtd. de produtos", "usa app", "reclamações (12m)"]):
    t = res[nome]
    ax.bar(t.index.astype(str), t["churn_pct"], color="#1f77b4")
    ax.axhline(geral * 100, color="gray", ls="--", lw=1)
    ax.set_title(f"Churn por {nome} (%)")
axes[0].set_ylabel("% de clientes que saíram")
fig.tight_layout(); fig.savefig("graficos/churn_por_fator.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(6.5, 4))
ax.bar(sr.index.astype(str), sr["churn_pct"], color="#d62728")
ax.set_title("Churn por score de risco (%)"); ax.set_xlabel("pontos de risco (0 a 3)")
fig.tight_layout(); fig.savefig("graficos/churn_por_score.png", dpi=150); plt.close()
