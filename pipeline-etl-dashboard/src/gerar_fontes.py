"""Gera as três fontes "sujas" de um pipeline de e-commerce (dados FICTÍCIOS).

Simula o que um analista recebe na vida real:
- vendas_2025.csv  : exportação do ERP, com duplicatas, valores nulos,
                     datas em dois formatos, produtos com nome errado e
                     valores negativos (devoluções lançadas errado).
- clientes.csv     : cadastro com CPF mascarado, e-mails inválidos e
                     duplicidade de cliente.
- metas.csv        : metas mensais por região.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(2025)

regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
produtos = {"NOTEBOOK PRO 14": "Notebook Pro 14", "notebook pro 14": "Notebook Pro 14",
            "CADEIRA ERGONOMICA": "Cadeira Ergonômica", "cadeira ergonômica": "Cadeira Ergonômica",
            "MONITOR 27": "Monitor 27\"", "monitor 27\"": "Monitor 27\"",
            "TECLADO MECANICO": "Teclado Mecânico", "MOUSE SEM FIO": "Mouse Sem Fio"}
precos = {"Notebook Pro 14": 4890.0, "Cadeira Ergonômica": 1290.0, "Monitor 27\"": 1749.0,
          "Teclado Mecânico": 389.0, "Mouse Sem Fio": 149.0}

linhas = []
for i in range(4200):
    mes = int(rng.integers(1, 13))
    dia = int(rng.integers(1, 29))
    produto_bruto = str(rng.choice(list(produtos)))
    produto = produtos[produto_bruto]
    qtd = int(rng.choice([1, 1, 1, 2, 2, 3], p=[.45, .2, .15, .1, .07, .03]))
    preco = precos[produto] * float(rng.choice([1.0, 1.0, 0.9, 0.85], p=[.7, .15, .1, .05]))
    data = f"{dia:02d}/{mes:02d}/2025" if i % 4 == 0 else f"2025-{mes:02d}-{dia:02d}"
    regiao = str(rng.choice(regioes, p=[.33, .24, .2, .13, .10]))
    cliente = f"C{int(rng.integers(1, 900)):04d}"
    linhas.append({
        "id_pedido": f"P{i + 1:05d}",
        "data": data,
        "cliente_id": cliente if rng.random() > 0.03 else "",
        "produto": produto_bruto,
        "quantidade": qtd if rng.random() > 0.02 else "",
        "preco_unitario": f"{preco:.2f}" if rng.random() > 0.04 else "",
        "regiao": regiao if rng.random() > 0.05 else "",
        "canal": str(rng.choice(["Site", "App", "Loja", "Televendas"], p=[.4, .3, .2, .1])),
    })

vendas = pd.DataFrame(linhas)
# duplicatas de exportação (mesmo pedido duas vezes)
vendas = pd.concat([vendas, vendas.sample(90, random_state=1)], ignore_index=True)
# devoluções lançadas como quantidade negativa
vendas.loc[vendas.sample(25, random_state=2).index, "quantidade"] = -1
vendas = vendas.sample(frac=1, random_state=3).reset_index(drop=True)
vendas.to_csv("dados/vendas_2025.csv", index=False)

clientes = pd.DataFrame({
    "cliente_id": [f"C{i:04d}" for i in range(1, 901)],
    "nome": [f"Cliente {i:03d}" for i in range(1, 901)],
    "email": [f"cliente{i:03d}@exemplo.com.br" if rng.random() > .06 else f"cliente{i:03d}@" for i in range(1, 901)],
    "uf": rng.choice(["SP", "RJ", "MG", "PR", "RS", "BA", "PE", "GO", "AM"], 900),
    "data_cadastro": pd.to_datetime(rng.integers(1577836800, 1735603200, 900), unit="s").date.astype(str),
})
clientes = pd.concat([clientes, clientes.sample(40, random_state=4)], ignore_index=True)
clientes.to_csv("dados/clientes.csv", index=False)

metas = pd.DataFrame({
    "mes": [f"2025-{m:02d}" for m in range(1, 13) for _ in regioes],
    "regiao": regioes * 12,
    "meta_receita": [round(float(rng.normal(150_000, 12_000)), 2) for _ in range(60)],
})
metas.to_csv("dados/metas.csv", index=False)

print(f"vendas_2025.csv: {len(vendas)} linhas (sujas) | clientes.csv: {len(clientes)} | metas.csv: {len(metas)}")
