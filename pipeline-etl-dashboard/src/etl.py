"""Pipeline ETL das vendas: extrai, limpa, valida, carrega e mede a qualidade.

Etapas
1. EXTRACT  lê as três fontes de dados/ (vendas, clientes, metas)
2. TRANSFORM
   - normaliza datas (dd/mm/aaaa e aaaa-mm-dd), nomes de produto e textos
   - remove pedidos duplicados (mantém o primeiro registro válido)
   - trata nulos (quantidade/preço), devoluções (quantidade negativa)
   - padroniza nomes de produto com um dicionário de-para
   - cruza com o cadastro de clientes (deduplicado) e com as metas
3. VALIDATE regras de negócio: chaves únicas, faixas de valor, datas dentro de 2025
4. LOAD    grava dados/vendas_limpo.csv, dados/qualidade.csv, dados/kpis.csv

Cada etapa registra o que entrou e o que saiu: é isso que permite explicar,
em entrevista, exatamente o que o pipeline fez com os dados.

Como rodar (a partir desta pasta): python src/etl.py
"""
import json
import re
import unicodedata

import pandas as pd

LOG = []


def registrar(etapa: str, descricao: str, antes: int, depois: int) -> None:
    LOG.append({"etapa": etapa, "descricao": descricao, "linhas_antes": antes,
                "linhas_depois": depois, "linhas_afetadas": antes - depois})
    print(f"[{etapa}] {descricao}: {antes} -> {depois}")


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(texto)) if not unicodedata.combining(c))


# ---------------------------------------------------------------- 1) EXTRACT
vendas = pd.read_csv("dados/vendas_2025.csv", dtype=str)
clientes = pd.read_csv("dados/clientes.csv", dtype=str)
metas = pd.read_csv("dados/metas.csv")
print(f"Extraído: {len(vendas)} vendas | {len(clientes)} clientes | {len(metas)} metas")
n0 = len(vendas)

# -------------------------------------------------------------- 2) TRANSFORM
# 2.1 datas em dois formatos -> datetime
def converter_data(valor: str):
    valor = str(valor).strip()
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(valor, format=formato)
        except ValueError:
            continue
    return pd.NaT


vendas["data"] = vendas["data"].map(converter_data)
invalidas = vendas["data"].isna().sum()
vendas = vendas[vendas["data"].notna()]
registrar("TRANSFORM", f"datas convertidas ({invalidas} inválidas removidas)", n0, len(vendas))

# 2.2 números
antes = len(vendas)
vendas["quantidade"] = pd.to_numeric(vendas["quantidade"], errors="coerce")
vendas["preco_unitario"] = pd.to_numeric(vendas["preco_unitario"], errors="coerce")
vendas = vendas[vendas["quantidade"].notna() & vendas["preco_unitario"].notna()]
registrar("TRANSFORM", "linhas sem quantidade ou preço removidas", antes, len(vendas))

# 2.3 devoluções: quantidade negativa é devolução, não venda
antes = len(vendas)
devolucoes = vendas["quantidade"] < 0
vendas.loc[devolucoes, "quantidade"] = vendas.loc[devolucoes, "quantidade"].abs()
vendas["devolucao"] = devolucoes.astype(int)
registrar("TRANSFORM", "devoluções identificadas (quantidade negativa)", antes, len(vendas))

# 2.4 duplicatas de pedido: mantém um registro por pedido
antes = len(vendas)
vendas = vendas.sort_values("data").drop_duplicates(subset="id_pedido", keep="first")
registrar("TRANSFORM", "pedidos duplicados removidos", antes, len(vendas))

# 2.5 nome do produto: dicionário de-para (maiúsculas, acentos, variações)
def padronizar_produto(nome: str) -> str:
    chave = sem_acento(nome).strip().lower()
    mapa = {
        "notebook pro 14": "Notebook Pro 14",
        "cadeira ergonomica": "Cadeira Ergonômica",
        'monitor 27"': 'Monitor 27"',
        "monitor 27": 'Monitor 27"',
        "teclado mecanico": "Teclado Mecânico",
        "mouse sem fio": "Mouse Sem Fio",
    }
    return mapa.get(chave, nome.strip().title())


antes_distintos = vendas["produto"].nunique()
vendas["produto"] = vendas["produto"].map(padronizar_produto)
registrar("TRANSFORM", f"nomes de produto padronizados ({antes_distintos} -> {vendas['produto'].nunique()} distintos)",
          antes_distintos, vendas["produto"].nunique())

# 2.6 região vazia -> "Não informada"
vendas["regiao"] = vendas["regiao"].fillna("Não informada").str.strip().replace("", "Não informada")

# 2.7 cadastro de clientes: deduplica e marca e-mail inválido
clientes = clientes.drop_duplicates(subset="cliente_id", keep="last")
email_valido = clientes["email"].str.match(r"^[\w.+-]+@[\w-]+\.[\w.]+$", na=False)
clientes["email_valido"] = email_valido.astype(int)
registrar("TRANSFORM", "cadastro de clientes deduplicado", 940, len(clientes))

# 2.8 cruzamentos e receita
vendas["cliente_id"] = vendas["cliente_id"].fillna("")
vendas = vendas.merge(clientes[["cliente_id", "nome", "uf", "email_valido"]],
                      on="cliente_id", how="left")
vendas["nome"] = vendas["nome"].fillna("Cliente não identificado")
# pedido sem cadastro de cliente não entra em ranking de cliente
vendas["nome_cliente_valido"] = vendas["nome"].where(vendas["cliente_id"] != "", None)
vendas["receita"] = (vendas["quantidade"] * vendas["preco_unitario"]).round(2)
vendas["receita_liquida"] = (vendas["receita"] * (1 - 2 * vendas["devolucao"])).round(2)  # devolução integral do valor bruto
vendas["mes"] = vendas["data"].dt.strftime("%Y-%m")

# 2.9 metas
vendas = vendas.merge(metas, on=["mes", "regiao"], how="left")

# --------------------------------------------------------------- 3) VALIDATE
regras = []
regras.append(("id_pedido único", vendas["id_pedido"].is_unique))
regras.append(("quantidade > 0", bool((vendas["quantidade"] > 0).all())))
regras.append(("preco_unitario > 0", bool((vendas["preco_unitario"] > 0).all())))
regras.append(("data dentro de 2025", bool(vendas["data"].dt.year.eq(2025).all())))
regras.append(("receita não negativa", bool((vendas["receita"] >= 0).all())))
regras.append(("produto sempre preenchido", bool(vendas["produto"].notna().all())))
regras.append(("toda venda tem meta de região",
               bool(vendas.loc[vendas["regiao"] != "Não informada", "meta_receita"].notna().all())))

qualidade = pd.DataFrame(regras, columns=["regra", "aprovada"])
print("\n== Regras de qualidade ==")
print(qualidade.to_string(index=False))
falhas = qualidade.loc[~qualidade["aprovada"], "regra"].tolist()
if falhas:
    raise ValueError(f"Pipeline interrompido: regras de qualidade reprovadas -> {falhas}")

# ------------------------------------------------------------------- 4) LOAD
vendas = vendas.sort_values(["data", "id_pedido"]).reset_index(drop=True)
vendas.to_csv("dados/vendas_limpo.csv", index=False)
qualidade.to_csv("dados/qualidade.csv", index=False)

kpis = {
    "linhas_brutas": int(n0),
    "linhas_limpas": int(len(vendas)),
    "pedidos_unicos": int(vendas["id_pedido"].nunique()),
    "receita_total": round(float(vendas["receita"].sum()), 2),
    "receita_liquida": round(float(vendas["receita_liquida"].sum()), 2),
    "ticket_medio": round(float(vendas["receita"].sum() / vendas["id_pedido"].nunique()), 2),
    "clientes_unicos": int(vendas.loc[vendas["cliente_id"] != "", "cliente_id"].nunique()),
    "produtos": int(vendas["produto"].nunique()),
    "taxa_devolucao_pct": round(float(vendas["devolucao"].mean() * 100), 2),
    "meta_total": round(float(metas["meta_receita"].sum()), 2),
    "atingimento_meta_pct": round(float(vendas["receita"].sum() / metas["meta_receita"].sum() * 100), 1),
    "percentual_linhas_descartadas": round((n0 - len(vendas)) / n0 * 100, 2),
}
pd.Series(kpis).to_csv("dados/kpis.csv", header=["valor"])
with open("dados/log_etl.json", "w", encoding="utf-8") as f:
    json.dump({"log": LOG, "kpis": kpis}, f, ensure_ascii=False, indent=2)

print("\n== KPIs ==")
for k, v in kpis.items():
    print(f"{k}: {v}")
print("\nArquivos gravados em dados/: vendas_limpo.csv, qualidade.csv, kpis.csv, log_etl.json")
