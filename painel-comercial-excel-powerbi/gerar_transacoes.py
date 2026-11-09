"""Gera a camada de CLIENTES e TRANSAÇÕES (dados SINTÉTICOS) a partir do fato_vendas.csv.

Cada linha de fato_vendas (mês x gerente x produto) é aberta em várias transações de clientes
da carteira daquele gerente. A soma das transações é IGUAL ao Realizado, então o Excel e o
painel de meta x realizado continuam batendo. Seed fixa => reproduzível.

Rodar DEPOIS de gerar_dados.py:  python gerar_transacoes.py
"""
import calendar

import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

fato = pd.read_csv("dados/fato_vendas.csv", parse_dates=["Mes"])
dim_ger = pd.read_csv("dados/dim_gerente.csv")

# ---------- Dimensão de clientes (carteira de cada gerente) ----------
segmentos = ["Varejo", "Alimentação", "Serviços", "Saúde", "Educação", "Indústria"]
portes = ["MEI", "Pequena", "Média"]
ufs = {
    "Sudeste": ["SP", "RJ", "MG", "ES"], "Sul": ["PR", "SC", "RS"],
    "Nordeste": ["BA", "PE", "CE", "RN"], "Centro-Oeste": ["GO", "DF", "MT"],
    "Norte": ["PA", "AM"],
}

clientes, carteira = [], {}
cid = 0
for _, g in dim_ger.iterrows():
    n = int(rng.integers(34, 42))  # tamanho da carteira
    ids = []
    for _ in range(n):
        cid += 1
        ids.append(cid)
        clientes.append((
            cid, f"Cliente {cid:03d}", rng.choice(segmentos),
            rng.choice(portes, p=[0.4, 0.4, 0.2]), g.Regiao, rng.choice(ufs[g.Regiao]),
        ))
    carteira[g.Gerente] = np.array(ids)

dim_cliente = pd.DataFrame(
    clientes, columns=["id_cliente", "Cliente", "Segmento", "Porte", "Regiao", "UF"]
)

# peso de cada cliente (poucos clientes grandes e muitos pequenos => concentração realista)
peso = {i: rng.lognormal(0, 0.9) for i in dim_cliente.id_cliente}

# ---------- Fato de transações ----------
linhas = []
for _, r in fato.iterrows():
    n = int(rng.integers(2, 7))
    ids = carteira[r.Gerente]
    p = np.array([peso[i] for i in ids])
    escolhidos = rng.choice(ids, size=n, replace=True, p=p / p.sum())
    cotas = rng.dirichlet(np.full(n, 2.0))
    valores = np.round(cotas * r.Realizado, 2)
    valores[-1] = round(r.Realizado - valores[:-1].sum(), 2)  # fecha exatamente o realizado
    ultimo_dia = calendar.monthrange(r.Mes.year, r.Mes.month)[1]
    for cli, v in zip(escolhidos, valores):
        dia = int(rng.integers(1, ultimo_dia + 1))
        linhas.append((r.Mes.replace(day=dia).date(), r.Gerente, r.Produto, int(cli), float(v)))

trans = pd.DataFrame(linhas, columns=["Data", "Gerente", "Produto", "id_cliente", "Valor"])
trans = trans.sort_values(["Data", "Gerente", "Produto"]).reset_index(drop=True)
trans.insert(0, "id_transacao", range(1, len(trans) + 1))

# ---------- Conferência: transações == realizado ----------
assert (trans.Valor > 0).all(), "valor de transação não positivo"
chk = trans.assign(Mes=pd.to_datetime(trans.Data).dt.to_period("M").dt.to_timestamp())
soma = chk.groupby(["Mes", "Gerente", "Produto"]).Valor.sum().round(2)
base = fato.set_index(["Mes", "Gerente", "Produto"]).Realizado.round(2)
dif = (soma - base).abs().max()
assert dif < 0.005, f"transações não batem com o realizado (dif máx {dif})"

dim_cliente.to_csv("dados/dim_cliente.csv", index=False)
trans.to_csv("dados/fato_transacoes.csv", index=False)

print(f"{len(trans)} transações | {len(dim_cliente)} clientes | total R$ {trans.Valor.sum():,.2f}"
      f" | realizado R$ {fato.Realizado.sum():,.2f} | dif máx por célula: {dif:.4f}")
