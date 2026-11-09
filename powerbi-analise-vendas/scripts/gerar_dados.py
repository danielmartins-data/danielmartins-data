"""
Gera a base fictícia usada no projeto de Power BI.
Todos os dados são sintéticos (semente fixa = resultado reproduzível).
Uso: python scripts/gerar_dados.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ---------- Dimensão: produtos ----------
produtos = [
    # id, produto, categoria, preço de lista, custo %
    (1, "Maquininha Smart", "Meios de Pagamento", 599.00, 0.55),
    (2, "Maquininha Mini", "Meios de Pagamento", 299.00, 0.55),
    (3, "Link de Pagamento", "Meios de Pagamento", 149.00, 0.30),
    (4, "Antecipação de Recebíveis", "Crédito", 1200.00, 0.40),
    (5, "Capital de Giro", "Crédito", 2500.00, 0.45),
    (6, "Conta Digital PJ", "Serviços Financeiros", 89.00, 0.25),
    (7, "Gestão de Vendas (CRM)", "Software", 249.00, 0.35),
    (8, "Seguro Empresarial", "Seguros", 480.00, 0.50),
]

# ---------- Dimensão: vendedores ----------
vendedores = [
    (1, "Ana Souza", "Sudeste"),
    (2, "Bruno Lima", "Sul"),
    (3, "Carla Mendes", "Nordeste"),
    (4, "Diego Alves", "Sudeste"),
    (5, "Elaine Rocha", "Centro-Oeste"),
    (6, "Felipe Costa", "Norte"),
]

# ---------- Dimensão: clientes ----------
segmentos = ["Varejo", "Alimentação", "Serviços", "Saúde", "Educação", "Indústria"]
portes = ["MEI", "Pequena", "Média"]
regioes = {
    "Sudeste": ["SP", "RJ", "MG", "ES"],
    "Sul": ["PR", "SC", "RS"],
    "Nordeste": ["BA", "PE", "CE", "RN"],
    "Centro-Oeste": ["GO", "DF", "MT"],
    "Norte": ["PA", "AM"],
}
pesos_regiao = {"Sudeste": 45, "Sul": 20, "Nordeste": 18, "Centro-Oeste": 10, "Norte": 7}

clientes = []
for i in range(1, 301):
    regiao = random.choices(list(pesos_regiao), weights=pesos_regiao.values())[0]
    clientes.append(
        (
            i,
            f"Cliente {i:03d}",
            random.choice(segmentos),
            random.choices(portes, weights=[40, 40, 20])[0],
            regiao,
            random.choice(regioes[regiao]),
        )
    )

# vendedor responsável por região (carteira)
vend_por_regiao = {}
for vid, _, reg in vendedores:
    vend_por_regiao.setdefault(reg, []).append(vid)
vend_por_regiao["Sudeste"] = [1, 4]

# ---------- Fato: vendas (2024-01-01 a 2025-12-31) ----------
inicio, fim = date(2024, 1, 1), date(2025, 12, 31)
dias = (fim - inicio).days
vendas = []
for venda_id in range(1, 3001):
    d = inicio + timedelta(days=random.randint(0, dias))
    # sazonalidade: nov/dez e mai (dia das mães) vendem mais
    if d.month in (5, 11, 12) or random.random() < 0.8:
        pass
    else:
        continue
    cli = random.choice(clientes)
    prod = random.choice(produtos)
    qtd = random.choices([1, 2, 3, 5, 10], weights=[50, 25, 12, 8, 5])[0]
    desconto = random.choices([0, 0.05, 0.10, 0.15], weights=[55, 25, 15, 5])[0]
    preco = prod[3]
    receita = round(preco * qtd * (1 - desconto), 2)
    custo = round(preco * prod[4] * qtd, 2)
    vend = random.choice(vend_por_regiao[cli[4]])
    vendas.append(
        (venda_id, d.isoformat(), cli[0], prod[0], vend, qtd, preco, desconto, receita, custo)
    )

vendas.sort(key=lambda r: r[1])
vendas = [(i + 1,) + r[1:] for i, r in enumerate(vendas)]

meta_mensal = {}  # meta por vendedor/mês, calibrada no realizado médio de cada vendedor
receita_vend = {}
for v in vendas:
    receita_vend[v[4]] = receita_vend.get(v[4], 0) + v[8]
for vid, _, _ in vendedores:
    media_mensal = receita_vend[vid] / 24
    for ano in (2024, 2025):
        for mes in range(1, 13):
            fator = (1.05 if ano == 2025 else 1.0) * (1.15 if mes in (5, 11, 12) else 1.0)
            ruido = random.uniform(0.9, 1.1)  # gera atingimentos variados (~80% a ~120%)
            meta_mensal[(vid, ano, mes)] = round(media_mensal * fator * ruido, 2)


def salvar(nome, cabecalho, linhas):
    with open(DATA_DIR / nome, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(cabecalho)
        w.writerows(linhas)


salvar("produtos.csv", ["id_produto", "produto", "categoria", "preco_lista", "custo_pct"], produtos)
salvar("vendedores.csv", ["id_vendedor", "vendedor", "regiao"], vendedores)
salvar("clientes.csv", ["id_cliente", "cliente", "segmento", "porte", "regiao", "uf"], clientes)
salvar(
    "vendas.csv",
    ["id_venda", "data", "id_cliente", "id_produto", "id_vendedor", "quantidade",
     "preco_unitario", "desconto_pct", "receita", "custo"],
    vendas,
)
salvar(
    "metas.csv",
    ["id_vendedor", "ano", "mes", "meta_receita"],
    [(v, a, m, val) for (v, a, m), val in sorted(meta_mensal.items())],
)

print(f"vendas: {len(vendas)} linhas | clientes: {len(clientes)} | produtos: {len(produtos)}")
