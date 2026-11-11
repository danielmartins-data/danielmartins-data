"""Gera o dashboard executivo em HTML (arquivo único, sem internet, sem CDN).

Lê dados/vendas_limpo.csv e dados/kpis.csv (saída do ETL) e escreve
dashboard.html com:
- 4 cartões de KPI (receita, ticket médio, pedidos, atingimento de meta)
- gráfico de linha de receita mensal x meta
- gráfico de barras por região e por produto
- tabela dos 10 maiores clientes
Todos os gráficos são SVG desenhado por este script: nada de bibliotecas
externas, então o arquivo abre em qualquer navegador, offline.

Como rodar (a partir desta pasta): python src/gerar_dashboard.py
"""
import html
from pathlib import Path

import pandas as pd

vendas = pd.read_csv("dados/vendas_limpo.csv", parse_dates=["data"])
kpis = pd.read_csv("dados/kpis.csv", index_col=0)["valor"]

receita_mes = vendas.groupby("mes")["receita"].sum().sort_index()
meta_mes = (vendas.drop_duplicates("mes").set_index("mes")["meta_receita"].sort_index())
receita_regiao = vendas.groupby("regiao")["receita"].sum().sort_values(ascending=False)
receita_produto = vendas.groupby("produto")["receita"].sum().sort_values(ascending=False)
top_clientes = (vendas.dropna(subset=["nome_cliente_valido"]).groupby("nome")["receita"]
                .sum().sort_values(ascending=False).head(10))

AZUL, AZUL_CLARO, CINZA, VERDE, VERMELHO = "#1f4e79", "#4a90c2", "#c9d6e3", "#2ea043", "#d62728"


def brl(valor: float) -> str:
    return f"R$ {valor:,.0f}".replace(",", ".")


def svg_linha(meses: list[str], real: list[float], meta: list[float], largura=760, altura=260) -> str:
    margem_esq, margem_dir, margem_topo, margem_base = 70, 20, 20, 40
    largura_util = largura - margem_esq - margem_dir
    altura_util = altura - margem_topo - margem_base
    teto = max(max(real), max(meta)) * 1.15
    passo = largura_util / max(len(meses) - 1, 1)

    def pontos(valores):
        return " ".join(
            f"{margem_esq + i * passo:.1f},{margem_topo + altura_util - (v / teto) * altura_util:.1f}"
            for i, v in enumerate(valores)
        )

    partes = [f'<svg viewBox="0 0 {largura} {altura}" role="img" aria-label="Receita mensal x meta">']
    for fracao in (0, .25, .5, .75, 1):
        y = margem_topo + altura_util - fracao * altura_util
        partes.append(f'<line x1="{margem_esq}" y1="{y:.1f}" x2="{largura - margem_dir}" y2="{y:.1f}" stroke="#e8eef4"/>')
        partes.append(f'<text x="{margem_esq - 8}" y="{y + 4:.1f}" font-size="10" fill="#6b7c8f" text-anchor="end">{teto * fracao / 1e6:.1f}M</text>')
    partes.append(f'<polyline points="{pontos(meta)}" fill="none" stroke="{CINZA}" stroke-width="2" stroke-dasharray="6 4"/>')
    partes.append(f'<polyline points="{pontos(real)}" fill="none" stroke="{AZUL}" stroke-width="2.5"/>')
    for i, (m, v) in enumerate(zip(meses, real)):
        x = margem_esq + i * passo
        y = margem_topo + altura_util - (v / teto) * altura_util
        partes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{AZUL}"/>')
        if i % 2 == 0:
            partes.append(f'<text x="{x:.1f}" y="{altura - 14}" font-size="10" fill="#6b7c8f" text-anchor="middle">{m[5:]}</text>')
    partes.append("</svg>")
    return "".join(partes)


def svg_barras_h(itens: list[tuple[str, float]], largura=760, altura_por_item=34) -> str:
    altura = altura_por_item * len(itens) + 10
    maior = max(v for _, v in itens)
    partes = [f'<svg viewBox="0 0 {largura} {altura}" role="img" aria-label="Receita por categoria">']
    for i, (rotulo, valor) in enumerate(itens):
        y = i * altura_por_item + 6
        largura_barra = (valor / maior) * (largura - 260)
        partes.append(f'<text x="0" y="{y + 16}" font-size="12" fill="#33475b">{html.escape(rotulo)}</text>')
        partes.append(f'<rect x="190" y="{y + 4}" width="{largura_barra:.1f}" height="18" rx="3" fill="{AZUL_CLARO}"/>')
        partes.append(f'<text x="{190 + largura_barra + 8:.1f}" y="{y + 18}" font-size="11" fill="#6b7c8f">{brl(valor)}</text>')
    partes.append("</svg>")
    return "".join(partes)


cartoes = [
    ("Receita 2025", brl(float(kpis["receita_total"])), "após limpeza de 7,6% das linhas"),
    ("Atingimento de meta", f'{float(kpis["atingimento_meta_pct"]):.1f}%', "receita x metas por região"),
    ("Ticket médio", brl(float(kpis["ticket_medio"])), f'{int(float(kpis["pedidos_unicos"]))} pedidos únicos'),
    ("Taxa de devolução", f'{float(kpis["taxa_devolucao_pct"]):.2f}%', "pedidos com devolução"),
]

tabela = "".join(
    f"<tr><td>{i + 1}</td><td>{html.escape(nome)}</td><td>{brl(valor)}</td></tr>"
    for i, (nome, valor) in enumerate(top_clientes.items())
)

documento = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard Comercial 2025 · dados sintéticos</title>
<style>
  :root {{ --azul:#1f4e79; --fundo:#f5f8fb; --texto:#22323f; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family: "Segoe UI", Roboto, Arial, sans-serif; background:var(--fundo); color:var(--texto); }}
  header {{ background:var(--azul); color:#fff; padding:22px 28px; }}
  header h1 {{ margin:0; font-size:22px; }}
  header p {{ margin:6px 0 0; font-size:13px; opacity:.85; }}
  main {{ max-width:1080px; margin:0 auto; padding:22px; }}
  .aviso {{ background:#fff4e5; border-left:4px solid #f0a000; padding:10px 14px; font-size:13px; border-radius:4px; margin-bottom:18px; }}
  .cartoes {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(210px,1fr)); gap:14px; margin-bottom:18px; }}
  .cartao {{ background:#fff; border-radius:10px; padding:16px 18px; box-shadow:0 1px 3px rgba(16,42,67,.08); }}
  .cartao .rotulo {{ font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:#6b7c8f; }}
  .cartao .valor {{ font-size:26px; font-weight:700; margin:6px 0 2px; color:var(--azul); }}
  .cartao .nota {{ font-size:12px; color:#6b7c8f; }}
  section {{ background:#fff; border-radius:10px; padding:18px; margin-bottom:18px; box-shadow:0 1px 3px rgba(16,42,67,.08); }}
  section h2 {{ margin:0 0 12px; font-size:16px; }}
  .legenda {{ font-size:12px; color:#6b7c8f; margin-bottom:8px; }}
  .legenda span {{ display:inline-block; margin-right:16px; }}
  .legenda i {{ display:inline-block; width:18px; height:3px; vertical-align:middle; margin-right:6px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th, td {{ text-align:left; padding:8px 6px; border-bottom:1px solid #eef2f6; }}
  th {{ color:#6b7c8f; font-weight:600; }}
  footer {{ text-align:center; font-size:12px; color:#6b7c8f; padding:18px; }}
</style>
</head>
<body>
<header>
  <h1>Dashboard Comercial 2025</h1>
  <p>Pipeline ETL em Python + dashboard gerado como HTML/SVG · Daniel Fernando Martins</p>
</header>
<main>
  <div class="aviso"><strong>Dados sintéticos.</strong> Todas as informações desta página foram geradas por script para demonstração. Não representam nenhuma empresa real.</div>

  <div class="cartoes">
    {''.join(f'<div class="cartao"><div class="rotulo">{r}</div><div class="valor">{v}</div><div class="nota">{n}</div></div>' for r, v, n in cartoes)}
  </div>

  <section>
    <h2>Receita mensal x meta</h2>
    <div class="legenda"><span><i style="background:{AZUL}"></i>Receita realizada</span><span><i style="background:{CINZA}"></i>Meta</span></div>
    {svg_linha(list(receita_mes.index), list(receita_mes.values), list(meta_mes.values))}
  </section>

  <section>
    <h2>Receita por região</h2>
    {svg_barras_h(list(receita_regiao.items()))}
  </section>

  <section>
    <h2>Receita por produto</h2>
    {svg_barras_h(list(receita_produto.items()))}
  </section>

  <section>
    <h2>10 maiores clientes</h2>
    <table>
      <thead><tr><th>#</th><th>Cliente</th><th>Receita</th></tr></thead>
      <tbody>{tabela}</tbody>
    </table>
  </section>
</main>
<footer>Gerado automaticamente por <code>src/gerar_dashboard.py</code> a partir de <code>dados/vendas_limpo.csv</code>.</footer>
</body>
</html>
"""

Path("dashboard.html").write_text(documento, encoding="utf-8")
print("dashboard.html gerado "
      f"({len(documento) / 1024:.0f} KB) | meses: {len(receita_mes)} | "
      f"regiões: {len(receita_regiao)} | produtos: {len(receita_produto)}")
