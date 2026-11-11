import json
import math

# ---------- helpers ----------
def brl(v, casas=0):
    s = f"{v:,.{casas}f}"
    return "R$ " + s.replace(",", "@").replace(".", ",").replace("@", ".")

def num(v):
    return f"{v:,.0f}".replace(",", ".")

def pct(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",") + "%"

# ---------- dados reais dos projetos ----------
ab = json.load(open("analise-teste-ab/dados/resultado_teste.csv")) if False else None
import pandas as pd
r = pd.read_csv("analise-teste-ab/dados/resultado_teste.csv").iloc[0]
prev = pd.read_csv("previsao-demanda/dados/metricas_modelos.csv", index_col=0)
kpi = pd.read_csv("pipeline-etl-dashboard/dados/kpis.csv", index_col=0)["valor"]
coorte = pd.read_csv("analise-cohort-retencao/dados/cohort_retencao.csv", index_col=0)
coorte_m12 = float(coorte["12"].dropna().mean())

# ---------- cartões de projeto ----------
projetos = [
    dict(emoji="🏗️", titulo="Pipeline ETL + Dashboard", pasta="pipeline-etl-dashboard",
         resumo="Base “suja” do ERP: 7,6% das linhas tratadas e justificadas, 7 regras de qualidade e um dashboard executivo gerado por código.",
         destaque=f"{pct(kpi['atingimento_meta_pct'])} da meta · {brl(kpi['receita_total']/1e6,2)} mi de receita",
         tags=["Python", "SQL", "ETL", "HTML"], img="pipeline-etl-dashboard/imagens/dashboard.png"),
    dict(emoji="🧪", titulo="Teste A/B de conversão", pasta="analise-teste-ab",
         resumo="Teste z implementado do zero: p-valor, intervalo de confiança, poder estatístico e o impacto do ganho em receita por ano.",
         destaque=f"+{pct(r['lift_absoluto_pct'],2)} p.p. de conversão · p < 0,0001",
         tags=["Estatística", "Python"], img="analise-teste-ab/graficos/conversao_por_grupo.png"),
    dict(emoji="🔄", titulo="Retenção de assinantes (coorte)", pasta="analise-cohort-retencao",
         resumo="Matriz de coorte em SQL, churn mensal e LTV por plano e canal de aquisição, com o viés das coortes recentes corrigido.",
         destaque=f"{pct(coorte_m12)} de retenção no 12º mês",
         tags=["SQL", "Coorte", "LTV"], img="analise-cohort-retencao/graficos/cohort_retencao.png"),
    dict(emoji="🚀", titulo="Previsão de demanda", pasta="previsao-demanda",
         resumo="Holt-Winters contra baseline sazonal, validação temporal e MAE, MAPE e WAPE — inclusive quando o modelo simples ganha.",
         destaque=f"WAPE de {pct(prev.loc['baseline_sazonal','WAPE_pct'])} · 30 dias à frente",
         tags=["Série temporal", "Python"], img="previsao-demanda/graficos/previsao_30dias.png"),
    dict(emoji="🧮", titulo="Score de risco de churn (modelo)", pasta="analise-risco-credito",
         resumo="Regressão logística implementada do zero, validação cruzada 5 folds, AUC, KS e curva de ganho — comparada com a regra de negócio.",
         destaque="AUC 0,744 · 44% de acerto no top 20% da base",
         tags=["Machine learning", "Estatística"], img="analise-risco-credito/graficos/curva_roc.png"),
    dict(emoji="🔁", titulo="Churn de clientes", pasta="analise-churn-clientes",
         resumo="Análise exploratória de fatores de churn e um score de risco explicável, com a lista de prioridade para o comercial.",
         destaque="Score separa 5,5% de 52,8% de churn",
         tags=["EDA", "Python"], img="analise-churn-clientes/graficos/churn_por_score.png"),
    dict(emoji="🏦", titulo="Inadimplência de crédito", pasta="analise-inadimplencia-sql",
         resumo="Seis consultas de SQL analítico: CTEs, funções de janela, safra com média móvel e concentração do risco.",
         destaque="46,8% da perda em 37 contratos",
         tags=["SQL", "CTE", "Window"], img="analise-inadimplencia-sql/graficos/inadimplencia_produto_score.png"),
    dict(emoji="📊", titulo="Análise de vendas 2025", pasta="analise-vendas",
         resumo="Do CSV bruto à recomendação: limpeza, KPIs, sazonalidade e comparação entre canal e região.",
         destaque="R$ 4,10 mi · ticket R$ 1.932",
         tags=["Python", "SQL"], img="analise-vendas/graficos/receita_mensal.png"),
    dict(emoji="📈", titulo="Painel Comercial (Excel + Power BI)", pasta="painel-comercial-excel-powerbi",
         resumo="Painel por fórmula (SUMIFS, lista suspensa, formatação condicional) e modelo estrela com medidas DAX prontas.",
         destaque="Meta x realizado por produto",
         tags=["Excel", "Power BI", "DAX"], img="painel-comercial-excel-powerbi/imagens/painel_excel.png"),
    dict(emoji="🎯", titulo="Segmentação RFM (R + Tableau)", pasta="segmentacao-rfm-r-tableau",
         resumo="Notas por quintil, 7 segmentos e plano de ação — em R base, com versão equivalente em Python e roteiro do Tableau.",
         destaque="Campeões: 18% dos clientes, 50% do valor",
         tags=["R", "Tableau", "RFM"], img="segmentacao-rfm-r-tableau/imagens/segmentos_valor.svg"),
]

REPO = "https://github.com/danielmartins-data/danielmartins-data"

def cartao(p):
    tags = " ".join(
        f'<img src="https://img.shields.io/badge/{t.replace(" ", "_")}-1f4e79?style=flat-square&labelColor=1f4e79" alt="{t}">'
        for t in p["tags"])
    return f"""<td width="50%" valign="top">
<a href="{REPO}/tree/main/{p['pasta']}"><img src="./{p['img']}" alt="{p['titulo']}" width="100%"></a>

### {p['emoji']} {p['titulo']}

{p['resumo']}

**{p['destaque']}**

{tags}

<a href="{REPO}/tree/main/{p['pasta']}"><b>Ver projeto →</b></a>
</td>"""

linhas = []
for i in range(0, len(projetos), 2):
    par = projetos[i:i+2]
    if len(par) == 1:
        linhas.append(f"<tr>{cartao(par[0])}<td></td></tr>")
    else:
        linhas.append(f"<tr>{cartao(par[0])}{cartao(par[1])}</tr>")
tabela_projetos = "<table>\n" + "\n  ".join(linhas) + "\n</table>"

# ---------- gráfico de barras (competências) ----------
competencias = [
    ("SQL analítico", 5), ("Python / pandas", 5), ("Excel avançado", 5),
    ("Power BI + DAX", 4), ("Estatística aplicada", 4), ("R", 3),
    ("Tableau", 3), ("Git / CI", 4),
]
largura, altura_barra = 620, 26
barras = []
for i, (nome, nivel) in enumerate(competencias):
    y = i * altura_barra + 6
    largura_barra = nivel / 5 * (largura - 210)
    barras.append(f'<text x="0" y="{y+14}" font-size="12" fill="#33475b">{nome}</text>')
    barras.append(f'<rect x="160" y="{y+2}" width="{largura-210}" height="14" rx="4" fill="#e8eef4"/>')
    barras.append(f'<rect x="160" y="{y+2}" width="{largura_barra:.0f}" height="14" rx="4" fill="#1f4e79"/>')
svg_competencias = (f'<svg viewBox="0 0 {largura} {altura_barra*len(competencias)+8}" '
                    f'role="img" aria-label="Competências por nível">' + "".join(barras) + "</svg>")

# ---------- gráfico de barras (resultados de carreira) ----------
resultados = [("185% de meta por 5 meses", 185), ("214% da meta (consórcios)", 214),
              ("118% de meta na Cielo", 118), ("+35% volume de negócios", 135),
              ("96–97% de retenção", 97)]
largura2, hb = 620, 30
b2 = []
for i, (nome, valor) in enumerate(resultados):
    y = i * hb + 8
    w = valor / 220 * (largura2 - 250)
    b2.append(f'<text x="0" y="{y+15}" font-size="12" fill="#33475b">{nome}</text>')
    b2.append(f'<rect x="200" y="{y+3}" width="{w:.0f}" height="16" rx="4" fill="#2ea043"/>')
    b2.append(f'<text x="{200+w+8:.0f}" y="{y+16}" font-size="11" fill="#6b7c8f">{valor}%</text>')
svg_resultados = (f'<svg viewBox="0 0 {largura2} {hb*len(resultados)+10}" '
                  f'role="img" aria-label="Resultados de carreira">' + "".join(b2) + "</svg>")

readme = f"""<div align="center">

<img src="./assets/banner.svg" alt="Daniel Fernando Martins, Analista de Dados" width="100%">

<br><br>

[![CI](https://github.com/danielmartins-data/danielmartins-data/actions/workflows/ci.yml/badge.svg)](https://github.com/danielmartins-data/danielmartins-data/actions/workflows/ci.yml)
[![Testes](https://img.shields.io/badge/testes-11_pytest-2EA043?style=flat-square&logo=pytest&logoColor=white)](./testes)
[![Projetos](https://img.shields.io/badge/portfólio-10_projetos-1f4e79?style=flat-square)](./COMO-AVALIAR.md)
[![Status](https://img.shields.io/badge/Status-Aberto_a_oportunidades-2EA043?style=flat-square)](https://www.linkedin.com/in/danielfernandomartins)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-1f4e79?style=flat-square)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.10_|_3.11_|_3.12-3776AB?style=flat-square&logo=python&logoColor=white)](./.github/workflows/ci.yml)
[![Dados](https://img.shields.io/badge/dados-100%25_sint%C3%A9ticos-f0a000?style=flat-square)](./COMO-AVALIAR.md)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Conectar-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/danielfernandomartins)
[![E-mail](https://img.shields.io/badge/E--mail-Falar_comigo-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:dfm21031983@gmail.com)
[![Currículo](https://img.shields.io/badge/Curr%C3%ADculo-Baixar-1f4e79?style=for-the-badge&logo=readdotcv&logoColor=white)](./CURRICULO.md)

**Transformo dados em decisão comercial.**
24 anos de mercado financeiro (Bradesco e Cielo) aplicados em análise de dados e BI.

<sub>🇬🇧 *Data Analyst with 24 years in financial services. SQL, Python, Power BI, Excel and R applied to sales, credit and customer analytics. Advanced English.*</sub>

<br>

<img src="./assets/kpis.svg" alt="24 anos de mercado financeiro, 185% de meta por 5 meses seguidos, 750 clientes em carteira, 4 graduações" width="100%">

<br>

**👉 Recrutador com 5 minutos?** Comece pelo [roteiro de avaliação](./COMO-AVALIAR.md) — ou abra direto o [dashboard gerado por código](./pipeline-etl-dashboard/dashboard.html).

<br>

<table>
<tr>
<td align="center" width="25%"><b>10</b><br><sub>projetos completos</sub></td>
<td align="center" width="25%"><b>23</b><br><sub>testes automatizados</sub></td>
<td align="center" width="25%"><b>3</b><br><sub>versões de Python no CI</sub></td>
<td align="center" width="25%"><b>0</b><br><sub>dados reais expostos</sub></td>
</tr>
</table>

</div>

<br>

## 🔎 Em 30 segundos

| | |
|---|---|
| 🎯 **Busco** | Vaga de **Analista de Dados Júnior** ou BI, com foco em negócios, vendas e finanças |
| 💡 **Diferencial** | 24 anos de mercado financeiro: entendo a pergunta de negócio, a meta e o cliente — não só a ferramenta |
| 🧰 **Ferramentas** | SQL · Python (pandas) · Power BI e DAX · Excel · R · Git/GitHub · GitHub Actions |
| 📂 **Provas** | **10 projetos**, cada um com pergunta de negócio, resultado, método e execução reproduzível |
| ✅ **Qualidade** | **11 testes automatizados** e CI verde a cada push — os projetos rodam e as saídas são validadas |
| 📫 **Contato** | [LinkedIn](https://www.linkedin.com/in/danielfernandomartins) · [dfm21031983@gmail.com](mailto:dfm21031983@gmail.com) |

---

## 🧭 Para quem está avaliando

<table>
<tr>
<td width="50%" valign="top">

**Se você é recrutador(a) ou RH**

- Comece pelo [roteiro de 5 minutos](./COMO-AVALIAR.md) — tem o que abrir e em qual ordem.
- [Currículo em uma página](./CURRICULO.md), com contato e stack.
- Toda competência citada tem um link que prova: código, base, resultado e teste.
- Os dados são **sintéticos** e isso está avisado em todos os projetos.

</td>
<td width="50%" valign="top">

**Se você é gestor(a) de dados ou tech lead**

- [Guia de entrevista](./docs/GUIA-ENTREVISTA.md): a narrativa, as perguntas difíceis e o que eu assumo como ponto fraco.
- Cada projeto tem teste que valida **as saídas**, não só "se rodou".
- [Como contribuir](./CONTRIBUTING.md): padrão de projeto, convenção de commit e fluxo de PR.
- Modelos e métricas feitos do zero (teste z, regressão logística) para mostrar conceito, não `import`.

</td>
</tr>
</table>

---

## ⭐ Portfólio em destaque

{tabela_projetos}

<sub>Todos os projetos usam **dados sintéticos** (fictícios), o que está explicado no README de cada um.</sub>

---

## 🧩 O que cada projeto demonstra

Todos seguem o mesmo caminho: **pergunta de negócio → dados → análise → insight → recomendação**.

| Competência | Onde está |
|---|---|
| **SQL analítico** (CTEs, funções de janela, subqueries, safra) | [Inadimplência de Crédito](./analise-inadimplencia-sql) · [Coorte](./analise-cohort-retencao) · [Pipeline](./pipeline-etl-dashboard/src/kpis.sql) |
| **Engenharia de dados e qualidade** (ETL com log, regras de validação) | [Pipeline ETL + Dashboard](./pipeline-etl-dashboard) |
| **Estatística aplicada** (teste z, IC 95%, poder estatístico) | [Teste A/B](./analise-teste-ab) |
| **Machine learning** (regressão logística do zero, AUC, KS, ganho acumulado) | [Score de risco de churn](./analise-risco-credito) |
| **Séries temporais** (Holt-Winters, baseline, validação temporal) | [Previsão de Demanda](./previsao-demanda) |
| **Limpeza e análise exploratória** (pandas) | [Vendas](./analise-vendas) · [Churn](./analise-churn-clientes) |
| **BI e modelagem** (modelo estrela, DAX, Excel por fórmula) | [Painel Comercial](./painel-comercial-excel-powerbi) |
| **Segmentação e score explicável** (RFM, regras de risco) | [RFM em R](./segmentacao-rfm-r-tableau) · [Churn](./analise-churn-clientes) |
| **Entrega visual** (dashboard HTML gerado por código) | [Pipeline ETL + Dashboard](./pipeline-etl-dashboard/dashboard.html) |
| **Qualidade de código e CI** (pytest + GitHub Actions) | [`testes/`](./testes) · [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) |
| **Documentação para recrutador** | [Como avaliar em 5 minutos](./COMO-AVALIAR.md) · [Contribuição](./CONTRIBUTING.md) · [Currículo](./CURRICULO.md) |
| **Organização de repositório** (licença, template de PR, política de segurança) | [`LICENSE`](./LICENSE) · [`.github/`](./.github) · [`SECURITY.md`](./SECURITY.md) |
| **Preparação para entrevista** (narrativa, perguntas difíceis, checklist) | [Guia de entrevista](./docs/GUIA-ENTREVISTA.md) |

### ▶️ Como rodar e testar

```bash
pip install -r requirements.txt          # dependências de todos os projetos
cd analise-vendas && python analise.py   # cada projeto roda na sua própria pasta
cd .. && pytest -q                       # executa os 10 projetos e valida as saídas
```

O badge **CI** no topo mostra o resultado da última execução no GitHub Actions.

---

## 🧰 Competências

<div>

{svg_competencias}

</div>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=sqlite&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![R](https://img.shields.io/badge/R-276DC3?style=for-the-badge&logo=r&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Excel](https://img.shields.io/badge/Excel-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=tableau&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Power Automate](https://img.shields.io/badge/Power_Automate-0066FF?style=for-the-badge&logo=powerautomate&logoColor=white)
![Azure](https://img.shields.io/badge/Azure_AI-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)

---

## 👋 Quem sou

Analista de Dados com uma combinação pouco comum: **vivência real de negócio** (Bradesco e Cielo) e **formação técnica em dados e sistemas**. Conheço o outro lado da planilha: sei quais perguntas o gestor comercial precisa responder, quais indicadores movem a meta e como transformar uma análise em ação.

- 📊 Foco em **análise de dados, BI e automação** aplicados a negócios e finanças
- 🎓 Cursando **Análise e Desenvolvimento de Sistemas** (Universidade São Judas); formado em **Economia, Finanças, Gestão de Riscos e Compliance e Direito**
- 🤖 Estudando **IA aplicada a dados**: certificado **Microsoft Azure AI Fundamentals (AI-900)** e em preparação para a AI-901
- 🗣️ Inglês avançado

## 📈 Resultados de carreira

Entregas em gestão de carteiras e metas, que hoje sei medir, modelar e prever com dados:

<div>

{svg_resultados}

</div>

| Resultado | Contexto |
|---|---|
| 🏆 **185%** de atingimento de metas por 5 meses seguidos | Carteira de 750 clientes |
| 📈 **+35%** no volume de negócios da carteira em 12 meses | Gerente Exclusive, Bradesco |
| 🤝 **96–97%** de retenção de clientes estratégicos | Segmentos Prime e Exclusive |
| 💳 **118%** de atingimento médio e **-14%** na perda de clientes | Gerente de Negócios, Cielo |
| 🚀 **214%** da meta em campanha de consórcios | Bradesco |

## 🎓 Formação e certificações

| | |
|---|---|
| 🎓 **Graduação** | Análise e Desenvolvimento de Sistemas, Universidade São Judas (em andamento) |
| ☁️ **Microsoft** | Azure AI Fundamentals (AI-900) |
| 📊 **Dados e BI** | Power BI, análise de dados e data science (SENAI); Modelagem e Visualização de Dados com Power BI e Excel Avançado |
| 🧠 **Trilha de dados e programação** | 19 cursos da Escola Virtual da Fundação Bradesco (169 h, 2024–2025): Python, bancos de dados, modelagem de dados, Power BI, Excel avançado, IA e programação orientada a objetos |
| ⚙️ **Automação** | Power Automate / RPA (DIO) |
| 💼 **Mercado financeiro** | ANBIMA CEA, CPA-20 e CPA-10 |

## 🗺️ Próximos passos

- [ ] Publicar o arquivo **.pbix** do painel comercial no Power BI (2 páginas: painel e carteira de clientes)
- [ ] Publicar o dashboard RFM no **Tableau Public** e colocar o link no projeto
- [ ] Teste automatizado da segmentação RFM executando o **R** no CI (hoje roda a versão Python equivalente)
- [ ] Modelo de propensão a churn com curva ROC comparado ao score de regras

---

---

## 🏁 Por que me contratar como Analista de Dados Júnior

| O que você ganha | Como isso aparece aqui |
|---|---|
| **Alguém que entende o negócio antes do código** | 24 anos em banco e adquirência; cada projeto começa por uma pergunta de negócio e termina em recomendação |
| **Base técnica sólida e verificável** | SQL analítico, pandas, estatística aplicada, modelo do zero, Excel/Power BI/DAX, R |
| **Hábito de qualidade** | 23 testes, CI em 3 versões de Python, licença, template de PR, política de dados |
| **Comunicação com quem decide** | resumo executivo em todos os projetos, dashboard executivo e guias de leitura |
| **Autonomia para aprender rápido** | 10 projetos construídos do zero, com método documentado e reproduzível |

> *"Não tenho 5 anos de experiência em dados. Tenho 24 anos resolvendo problema de negócio com número — e agora sei programar, modelar e testar esse número. O que você vê neste repositório é o meu jeito de trabalhar, não uma vitrine de curso."*

---

<div align="center">

### 📫 Vamos conversar?

Aberto a oportunidades em **Análise de Dados, BI e áreas que unam negócio e dados**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/danielfernandomartins)
[![E-mail](https://img.shields.io/badge/E--mail-dfm21031983@gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:dfm21031983@gmail.com)

<sub>Repositório organizado com testes automatizados, CI e documentação — porque portfólio de dados também precisa de qualidade de dado.</sub>

<sub>Licença MIT · dados 100% sintéticos · feito com Python, SQL, Excel, Power BI, R e GitHub Actions</sub>

</div>
"""

open("README.md", "w", encoding="utf-8").write(readme)
print("README gerado:", len(readme), "caracteres")
