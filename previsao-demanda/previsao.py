"""Previsão de demanda diária: baseline sazonal, Holt-Winters e validação temporal.

Entrada : dados/demanda_diaria.csv  (dados SINTÉTICOS, gerados por gerar_dados.py)
Saídas  : dados/previsao_30dias.csv, dados/metricas_modelos.csv
          graficos/historico.png, graficos/previsao_30dias.png,
          graficos/comparacao_modelos.png

Métodos (só pandas, numpy e matplotlib — nada de caixa-preta):
1. Baseline sazonal: média do mesmo dia da semana nas últimas 8 semanas.
2. Holt-Winters aditivo (tendência + sazonalidade semanal de 7 dias), com
   alpha, beta e gamma escolhidos por busca em grade na validação interna.
3. Validação temporal: treina até 30/11/2025 e mede o erro em dezembro/2025.
4. Métricas: MAE, RMSE, MAPE e WAPE (as duas últimas são as do negócio).
5. Intervalo de previsão de 95% a partir do desvio dos resíduos.

Como rodar (a partir desta pasta): python previsao.py
"""
import itertools

import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

serie = pd.read_csv("dados/demanda_diaria.csv", parse_dates=["data"]).set_index("data")["pedidos"].astype(float)
print(f"Histórico: {serie.index.min():%d/%m/%Y} a {serie.index.max():%d/%m/%Y} ({len(serie)} dias)")

CORTE = pd.Timestamp("2025-11-30")
treino, teste = serie[serie.index <= CORTE], serie[serie.index > CORTE]
HORIZONTE = len(teste)
print(f"Treino: {len(treino)} dias | Teste: {HORIZONTE} dias")


# ------------------------------------------------------- 1) Baseline sazonal
def baseline_sazonal(hist: pd.Series, passos: int) -> np.ndarray:
    """Média do mesmo dia da semana nas últimas 8 semanas, repetida à frente."""
    janela = hist.iloc[-56:]
    por_dia = janela.groupby(janela.index.day_of_week).mean()
    proximos = pd.date_range(hist.index[-1] + pd.Timedelta(days=1), periods=passos)
    return por_dia.reindex(proximos.day_of_week).to_numpy()


# ---------------------------------------------- 2) Holt-Winters aditivo (7)
def _holt_winters(hist: np.ndarray, passos: int, alpha: float, beta: float,
                  gamma: float, m: int = 7) -> np.ndarray:
    nivel = hist[:m].mean()
    tendencia = (hist[m:2 * m].mean() - hist[:m].mean()) / m
    sazon = list(hist[:m] - nivel)
    for i in range(m, len(hist)):
        v = hist[i]
        nivel_anterior = nivel
        nivel = alpha * (v - sazon[i - m]) + (1 - alpha) * (nivel + tendencia)
        tendencia = beta * (nivel - nivel_anterior) + (1 - beta) * tendencia
        sazon.append(gamma * (v - nivel) + (1 - gamma) * sazon[i - m])
    return np.array([nivel + (k + 1) * tendencia + sazon[len(hist) - m + (k % m)]
                     for k in range(passos)])


def holt_winters(hist: pd.Series, passos: int) -> tuple[np.ndarray, dict]:
    """Ajusta alpha, beta e gamma por busca em grade na validação interna.

    A escolha dos parâmetros olha só os últimos 28 dias do próprio histórico
    de treino, nunca o período de teste: assim a avaliação continua honesta.
    """
    valores = hist.to_numpy()
    corte = len(valores) - 28
    interno_treino, interno_val = valores[:corte], valores[corte:]
    melhor, melhor_erro = (0.3, 0.05, 0.2), np.inf
    for alpha, beta, gamma in itertools.product([0.1, 0.2, 0.3, 0.5], [0.01, 0.05, 0.1], [0.1, 0.2, 0.4]):
        prev = _holt_winters(interno_treino, len(interno_val), alpha, beta, gamma)
        erro = float(np.mean(np.abs(prev - interno_val)))
        if erro < melhor_erro:
            melhor, melhor_erro = (alpha, beta, gamma), erro
    alpha, beta, gamma = melhor
    return (_holt_winters(valores, passos, alpha, beta, gamma),
            {"alpha": alpha, "beta": beta, "gamma": gamma})


# ------------------------------------------------------------ 3) Métricas
def metricas(real: np.ndarray, previsto: np.ndarray) -> dict:
    erro = real - previsto
    return {
        "MAE": float(np.mean(np.abs(erro))),
        "RMSE": float(np.sqrt(np.mean(erro ** 2))),
        "MAPE_pct": float(np.mean(np.abs(erro / real)) * 100),
        "WAPE_pct": float(np.abs(erro).sum() / real.sum() * 100),
    }


prev_base = baseline_sazonal(treino, HORIZONTE)
prev_hw, params = holt_winters(treino, HORIZONTE)

comparacao = pd.DataFrame({
    "baseline_sazonal": metricas(teste.to_numpy(), prev_base),
    "holt_winters": metricas(teste.to_numpy(), prev_hw),
}).T.round(2)
comparacao["parametros"] = ["-", f"alpha={params['alpha']} beta={params['beta']} gamma={params['gamma']}"]
print("\n== Comparação no período de teste (dez/2025) ==")
print(comparacao.to_string())
comparacao.to_csv("dados/metricas_modelos.csv")

# ------------------------------------------- 4) Previsão dos próximos 30 dias
PASSOS_FUTURO = 30
prev_final, params_final = holt_winters(serie, PASSOS_FUTURO)
futuro = pd.date_range(serie.index[-1] + pd.Timedelta(days=1), periods=PASSOS_FUTURO)

# resíduo do modelo: erro dentro do próprio histórico (últimos 28 dias)
ajuste_hist, _ = holt_winters(serie.iloc[:-28], 28)
residuo_padrao = float(np.std(serie.iloc[-28:].to_numpy() - ajuste_hist))

previsao = pd.DataFrame({
    "data": futuro,
    "previsao_pedidos": np.round(prev_final).astype(int),
    "piso_95": np.round(prev_final - 1.96 * residuo_padrao).clip(min=0).astype(int),
    "teto_95": np.round(prev_final + 1.96 * residuo_padrao).astype(int),
})
previsao.to_csv("dados/previsao_30dias.csv", index=False)
print(f"\n== Próximos 30 dias == total previsto: {previsao.previsao_pedidos.sum():,} pedidos".replace(",", "."))
print(previsao.head(7).to_string(index=False))

# ------------------------------------------------------------ 5) Gráficos
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(serie.index, serie.values, lw=.7, color="#1f4e79")
ax.plot(serie.index, serie.rolling(28).mean(), lw=2, color="#d62728", label="média móvel 28d")
ax.set_title("Demanda diária de pedidos (2024-2025)"); ax.legend()
fig.tight_layout(); fig.savefig("graficos/historico.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(11, 4.2))
ax.plot(teste.index, teste.values, marker="o", ms=4, label="real", color="#1f4e79")
ax.plot(teste.index, prev_base, ls="--", label="baseline sazonal", color="#8c8c8c")
ax.plot(teste.index, prev_hw, lw=2, label="Holt-Winters", color="#d62728")
ax.set_title("Validação: previsão x real em dezembro/2025"); ax.legend()
plt.xticks(rotation=45)
fig.tight_layout(); fig.savefig("graficos/comparacao_modelos.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(11, 4.2))
hist_recente = serie.iloc[-90:]
ax.plot(hist_recente.index, hist_recente.values, lw=1, color="#1f4e79", label="histórico")
ax.plot(previsao.data, previsao.previsao_pedidos, lw=2, color="#d62728", label="previsão")
ax.fill_between(previsao.data, previsao.piso_95, previsao.teto_95, color="#d62728", alpha=.18, label="intervalo 95%")
ax.set_title("Previsão dos próximos 30 dias"); ax.legend()
plt.xticks(rotation=45)
fig.tight_layout(); fig.savefig("graficos/previsao_30dias.png", dpi=150); plt.close()

print("\nArquivos gravados em dados/ e graficos/.")
