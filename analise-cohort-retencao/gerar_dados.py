"""Gera a base sintética de assinantes de um serviço (dados FICTÍCIOS).

Cada linha é um cliente com a data de entrada (cohort) e a data de saída
(cancelamento). Quem tem data_saida vazia continua ativo.
A probabilidade de cancelar depende do plano, do canal de aquisição e do
tempo de casa, para que a análise de coorte encontre um padrão real.
"""
from datetime import date, timedelta

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

INICIO = date(2024, 1, 1)
MESES = 24
planos = {"Básico": 39.9, "Pro": 79.9, "Premium": 149.9}
canais = {"Orgânico": 0.9, "Indicação": 0.75, "Pago": 1.35, "Parceria": 1.1}

linhas = []
for mes in range(MESES):
    ano, m = divmod(INICIO.month - 1 + mes, 12)
    inicio_mes = date(INICIO.year + ano, m + 1, 1)
    base = int(rng.normal(240, 30)) + mes * 6          # crescimento gradual
    for _ in range(max(base, 60)):
        plano = rng.choice(list(planos), p=[0.45, 0.38, 0.17])
        canal = rng.choice(list(canais), p=[0.35, 0.15, 0.35, 0.15])
        entrada = inicio_mes + timedelta(days=int(rng.integers(0, 28)))
        # risco mensal de churn: base x plano x canal, caindo com o tempo de casa
        risco_base = 0.055 * (1.25 if plano == "Básico" else 0.85 if plano == "Pro" else 0.55)
        risco_base *= canais[canal]
        meses_ativo = 0
        for t in range(MESES * 2):
            risco = risco_base * (1.6 if t == 0 else 1.0 if t < 3 else 0.7)
            if rng.random() < risco:
                break
            meses_ativo += 1
        saida = entrada + timedelta(days=30 * meses_ativo + int(rng.integers(0, 25)))
        if saida > date(2025, 12, 31):
            saida = None
        linhas.append({
            "id_cliente": f"C{len(linhas) + 1:05d}",
            "data_entrada": entrada.isoformat(),
            "data_saida": saida.isoformat() if saida else "",
            "plano": plano,
            "mensalidade": planos[plano],
            "canal_aquisicao": canal,
            "uf": rng.choice(["SP", "RJ", "MG", "PR", "RS", "BA", "PE", "SC"], p=[.34, .16, .12, .08, .08, .08, .07, .07]),
        })

df = pd.DataFrame(linhas)
df.to_csv("dados/assinantes.csv", index=False)
print(f"{len(df)} assinantes gerados | ativos: {(df['data_saida'] == '').sum()} | cancelados: {(df['data_saida'] != '').sum()}")
