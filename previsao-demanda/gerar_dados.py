"""Gera a série histórica de demanda diária (dados FICTÍCIOS).

Loja de e-commerce: vendas diárias de 2024-01-01 a 2025-12-31 com
tendência de crescimento, sazonalidade semanal (fim de semana forte),
sazonalidade anual (Natal/Black Friday) e ruído.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(11)

datas = pd.date_range("2024-01-01", "2025-12-31", freq="D")
t = np.arange(len(datas))

tendencia = 180 + 0.11 * t                                   # crescimento ~0,11 pedido/dia
semana = np.where(datas.day_of_week >= 5, 1.28, 1.0)           # sáb/dom +28%
ano = 1 + 0.35 * np.exp(-((datas.day_of_year - 355) / 18) ** 2)  # pico de fim de ano
mes = np.select(
    [datas.month.isin([1, 2]), datas.month.isin([5, 6]), datas.month.isin([11])],
    [0.88, 0.94, 1.18],
    default=1.0,
)
ruido = rng.normal(1, 0.07, len(datas))

pedidos = np.maximum((tendencia * semana * ano * mes * ruido).round(), 20)

df = pd.DataFrame({"data": datas.date.astype(str), "pedidos": pedidos.astype(int)})
df.to_csv("dados/demanda_diaria.csv", index=False)
print(f"{len(df)} dias | média {df['pedidos'].mean():.0f} pedidos/dia | último dia {df['pedidos'].iloc[-1]}")
