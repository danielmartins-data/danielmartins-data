"""Score de risco de churn: regra explicável x regressão logística.

Entrada : dados/clientes.csv  (dados SINTÉTICOS, gerados por gerar_dados.py)
Saídas  : dados/base_com_score.csv
          dados/comparacao_modelos.csv
          dados/ganho_acumulado.csv
          dados/coeficientes.csv
          graficos/curva_roc.png, graficos/ganho_acumulado.png,
          graficos/churn_por_score.png

O que este projeto demonstra:
1. Regressão logística implementada do zero (gradiente descendente), com
   features padronizadas — sem sklearn, para mostrar que o conceito está claro.
2. Validação cruzada estratificada em 5 folds, sem vazamento de dados.
3. Métricas de classificação: AUC, KS, acurácia, precisão, recall e F1 no
   ponto de corte escolhido pelo negócio (aqui, os 20% de maior risco).
4. Curva de ganho acumulado: quantos churns a equipe encontra ligando para
   apenas 20% da base — a métrica que o gestor realmente usa.

Como rodar (a partir desta pasta): python analise.py
"""
import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

SEMENTE = 42
rng = np.random.default_rng(SEMENTE)

df = pd.read_csv("dados/clientes.csv")
print(f"Clientes: {len(df):,}".replace(",", ".") + f" | churn observado: {df.churn.mean():.1%}")

# ---------------------------------------------------------- 1) Features
df["sem_app"] = (df["usa_app"] == 0).astype(int)
df["poucos_produtos"] = (df["qtd_produtos"] <= 2).astype(int)
df["cliente_novo"] = (df["meses_relacionamento"] < 12).astype(int)
df["saldo_log"] = np.log1p(df["saldo_medio"])

FEATURES = ["poucos_produtos", "sem_app", "reclamacoes_12m", "cliente_novo", "saldo_log"]
X = df[FEATURES].to_numpy(dtype=float)
y = df["churn"].to_numpy(dtype=float)



# ------------------------------------- 2) Regressão logística do zero
def sigmoide(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))


def treinar(Xtr, ytr, epocas=3000, taxa=0.25, l2=0.01):
    w = np.zeros(Xtr.shape[1])
    b = 0.0
    for _ in range(epocas):
        p = sigmoide(Xtr @ w + b)
        erro = p - ytr
        w -= taxa * (Xtr.T @ erro / len(ytr) + l2 * w)
        b -= taxa * erro.mean()
    return w, b


def prever(Xte, w, b):
    return sigmoide(Xte @ w + b)


# ------------------------------------------- 3) Validação cruzada 5 folds
def folds_estratificados(y, k=5, semente=SEMENTE):
    gerador = np.random.default_rng(semente)
    indices = np.arange(len(y))
    dobras = [[] for _ in range(k)]
    for classe in (0, 1):
        idx = indices[y == classe]
        gerador.shuffle(idx)
        for i, parte in enumerate(np.array_split(idx, k)):
            dobras[i].extend(parte.tolist())
    return [np.array(d) for d in dobras]


def auc(real, prob):
    """AUC pela fórmula de Mann-Whitney (empates contam 0,5)."""
    ordem = np.argsort(prob)
    ranks = np.empty_like(ordem, dtype=float)
    ranks[ordem] = np.arange(1, len(prob) + 1)
    # empates recebem o rank médio
    _, inv, contagem = np.unique(prob, return_inverse=True, return_counts=True)
    soma = np.zeros(len(contagem))
    np.add.at(soma, inv, ranks)
    ranks = (soma / contagem)[inv]
    n_pos, n_neg = real.sum(), (1 - real).sum()
    return float((ranks[real == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def ks(real, prob):
    """KS = maior distância entre as curvas acumuladas de bons e maus."""
    ordem = np.argsort(-prob)
    real = real[ordem]
    pos_total, neg_total = real.sum(), (1 - real).sum()
    pos_acum = np.cumsum(real) / pos_total
    neg_acum = np.cumsum(1 - real) / neg_total
    return float(np.max(np.abs(pos_acum - neg_acum)))


prob_cv = np.zeros(len(y))
for dobra in folds_estratificados(y):
    treino = np.setdiff1d(np.arange(len(y)), dobra)
    media_fold = X[treino].mean(axis=0)
    desvio_fold = X[treino].std(axis=0) + 1e-9
    X_treino = (X[treino] - media_fold) / desvio_fold
    X_validacao = (X[dobra] - media_fold) / desvio_fold
    w, b = treinar(X_treino, y[treino])
    prob_cv[dobra] = prever(X_validacao, w, b)

auc_cv, ks_cv = auc(y, prob_cv), ks(y, prob_cv)

# ------------------------- 4) Comparação com o score de regras simples
regra = df["poucos_produtos"] + df["sem_app"] + (df["reclamacoes_12m"] >= 1).astype(int)
auc_regra, ks_regra = auc(y, regra.to_numpy(dtype=float)), ks(y, regra.to_numpy(dtype=float))

# -------------------------- 5) Métricas no corte de 20% de maior risco
def metricas_no_corte(real, score, fracao=0.20):
    n_corte = int(round(len(score) * fracao))
    corte = np.sort(score)[::-1][n_corte - 1]
    previsto = (score >= corte).astype(int)
    tp = int(((previsto == 1) & (real == 1)).sum())
    fp = int(((previsto == 1) & (real == 0)).sum())
    fn = int(((previsto == 0) & (real == 1)).sum())
    precisao = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precisao * recall / max(precisao + recall, 1e-9)
    acuracia = float((previsto == real).mean())
    return {"corte_top20pct": round(float(corte), 4), "precisao": round(precisao, 3),
            "recall": round(recall, 3), "f1": round(f1, 3), "acuracia": round(acuracia, 3),
            "churns_encontrados": tp, "ligacoes": int(previsto.sum())}


m_log, m_regra = metricas_no_corte(y, prob_cv), metricas_no_corte(y, regra.to_numpy(dtype=float))

comparacao = pd.DataFrame([
    {"modelo": "Score de regras (0-3 pontos)", "auc": round(auc_regra, 3), "ks": round(ks_regra, 3), **m_regra},
    {"modelo": "Regressão logística (5 features)", "auc": round(auc_cv, 3), "ks": round(ks_cv, 3), **m_log},
])
print("\n== Comparação (validação cruzada 5 folds) ==")
print(comparacao.to_string(index=False))
comparacao.to_csv("dados/comparacao_modelos.csv", index=False)

# ------------------------------------------- 6) Modelo final + coeficientes
media_final = X.mean(axis=0)
desvio_final = X.std(axis=0) + 1e-9
Xs_final = (X - media_final) / desvio_final
w_final, b_final = treinar(Xs_final, y)
coef = pd.DataFrame({"variavel": FEATURES, "coeficiente": np.round(w_final, 3),
                     "odds_ratio": np.round(np.exp(w_final), 2)}).sort_values("coeficiente", ascending=False)
coef.to_csv("dados/coeficientes.csv", index=False)
print("\n== Coeficientes (odds ratio) ==")
print(coef.to_string(index=False))

df["prob_churn"] = np.round(prob_cv, 4)
df["score_regras"] = regra
df["faixa_risco"] = pd.cut(prob_cv, [0, .1, .2, .35, .5, 1],
                           labels=["1 - Baixo", "2 - Moderado", "3 - Alto", "4 - Muito alto", "5 - Crítico"])
df.to_csv("dados/base_com_score.csv", index=False)

faixa = df.groupby("faixa_risco", observed=True).agg(
    clientes=("id_cliente", "size"), churn_pct=("churn", "mean")).reset_index()
faixa["churn_pct"] = (faixa["churn_pct"] * 100).round(1)
print("\n== Churn por faixa de risco ==")
print(faixa.to_string(index=False))

# --------------------------------------------- 7) Curva de ganho acumulado
ordem = np.argsort(-prob_cv)
real_ordenado = y[ordem]
populacao = np.arange(1, len(y) + 1) / len(y) * 100
ganho = np.cumsum(real_ordenado) / real_ordenado.sum() * 100
linha_base = populacao
pd.DataFrame({"pct_base_contatada": np.round(populacao, 2),
              "pct_churns_capturados": np.round(ganho, 2)}).iloc[::10].to_csv(
    "dados/ganho_acumulado.csv", index=False)

ganho_20 = float(ganho[int(len(y) * 0.20) - 1])

# -------------------------------------------------------------- 8) Gráficos
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})

fpr, tpr = [], []
for limite in np.linspace(1, 0, 200):
    previsto = prob_cv >= limite
    tp = ((previsto) & (y == 1)).sum()
    fp = ((previsto) & (y == 0)).sum()
    fpr.append(fp / (y == 0).sum()); tpr.append(tp / (y == 1).sum())

fig, ax = plt.subplots(figsize=(6, 5))
ax.plot(fpr, tpr, lw=2.5, color="#1f4e79", label=f"Regressão logística (AUC {auc_cv:.3f})")
ax.plot([0, 1], [0, 1], ls="--", color="#8c8c8c", label="Aleatório (AUC 0,500)")
ax.set_xlabel("falsos positivos"); ax.set_ylabel("verdadeiros positivos")
ax.set_title("Curva ROC — validação cruzada 5 folds"); ax.legend(loc="lower right")
fig.tight_layout(); fig.savefig("graficos/curva_roc.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(7.5, 4.6))
ax.plot(populacao, ganho, lw=2.5, color="#2ea043", label="Modelo")
ax.plot(populacao, linha_base, ls="--", color="#8c8c8c", label="Sem modelo (aleatório)")
ax.axvline(20, color="#d62728", ls=":", lw=1.5)
ax.annotate(f"20% da base = {ganho_20:.0f}% dos churns",
            xy=(20, ganho_20), xytext=(28, ganho_20 - 18),
            arrowprops=dict(arrowstyle="->", color="#d62728"), color="#d62728", fontsize=10)
ax.set_xlabel("% da base contatada"); ax.set_ylabel("% de churns capturados")
ax.set_title("Curva de ganho acumulado"); ax.legend(loc="lower right")
fig.tight_layout(); fig.savefig("graficos/ganho_acumulado.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.bar(faixa["faixa_risco"].astype(str), faixa["churn_pct"], color=["#2ea043", "#8fbf5f", "#f0a000", "#e05c00", "#d62728"])
for i, v in enumerate(faixa["churn_pct"]):
    ax.text(i, v + 0.8, f"{v:.1f}%", ha="center", fontweight="bold", fontsize=9)
ax.set_ylabel("churn observado (%)"); ax.set_ylim(0, max(faixa["churn_pct"]) * 1.25)
ax.set_title("Churn por faixa de risco do modelo")
fig.tight_layout(); fig.savefig("graficos/churn_por_score.png", dpi=150); plt.close()

print(f"\nAUC: {auc_cv:.3f} | KS: {ks_cv:.3f} | 20% da base captura {ganho_20:.0f}% dos churns")
print("Arquivos gravados em dados/ e graficos/.")
