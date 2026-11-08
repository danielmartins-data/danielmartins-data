"""Monta excel/painel_comercial.xlsx: dados em Tabela, painel com fórmulas (SUMIFS), filtro por produto,
formatação condicional e gráficos. Tudo por fórmula: muda o filtro, muda o painel."""
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

df = pd.read_csv("dados/vendas_metas.csv", parse_dates=["Mes"])
N = len(df)
F = "Arial"
AZUL, CINZA = "1F4E79", "F2F2F2"
f = lambda **k: Font(name=F, **k)
fino = Side(style="thin", color="BFBFBF")
borda = Border(top=fino, bottom=fino, left=fino, right=fino)
brl = '"R$" #,##0'
pct = "0.0%"

wb = Workbook()

# ---------------- Leia-me ----------------
ws0 = wb.active; ws0.title = "Leia-me"
linhas = [
    ("Painel Comercial: Meta x Realizado (2025)", f(size=16, bold=True, color=AZUL)),
    ("Dados SINTÉTICOS (fictícios), criados para demonstração. Não representam nenhuma empresa real.", f(italic=True, color="C00000")),
    ("", f()),
    ("Como usar", f(bold=True, size=12)),
    ("1. Vá na aba 'Painel' e escolha o produto na célula B3 (lista suspensa). Todos os números e gráficos se atualizam.", f()),
    ("2. A aba 'Dados' é uma Tabela do Excel (384 linhas): Mês, Gerente, Região, Produto, Meta, Realizado.", f()),
    ("3. Cores do atingimento: verde = 100% ou mais; amarelo = 90% a 99,9%; vermelho = abaixo de 90%.", f()),
    ("", f()),
    ("Recursos do Excel demonstrados", f(bold=True, size=12)),
    ("Tabela de dados · SUMIFS · INDEX/MATCH · COUNTIF · IF · validação de dados (lista suspensa) · formatação condicional · gráficos", f()),
    ("", f()),
    ("Legenda: célula com fundo amarelo-claro e texto azul (Painel!B3) = entrada do usuário; o restante é fórmula.", f(italic=True)),
]
for i, (t, ft) in enumerate(linhas, 1):
    c = ws0.cell(row=i, column=1, value=t); c.font = ft
ws0.column_dimensions["A"].width = 120
ws0.sheet_view.showGridLines = False

# ---------------- Dados ----------------
wd = wb.create_sheet("Dados")
cols = ["Mês", "Gerente", "Região", "Produto", "Meta", "Realizado"]
wd.append(cols)
for r in df.itertuples(index=False):
    wd.append([r.Mes.to_pydatetime(), r.Gerente, r.Regiao, r.Produto, float(r.Meta), float(r.Realizado)])
for c in wd[1]:
    c.font = f(bold=True, color="FFFFFF")
for row in wd.iter_rows(min_row=2, max_row=N + 1):
    row[0].number_format = "mmm/yy"
    row[4].number_format = brl; row[5].number_format = brl
    for c in row: c.font = f()
tab = Table(displayName="TabelaVendas", ref=f"A1:F{N+1}")
tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
wd.add_table(tab)
for col, w in zip("ABCDEF", [10, 18, 16, 14, 14, 14]): wd.column_dimensions[col].width = w
wd.freeze_panes = "A2"

# ---------------- Painel ----------------
wp = wb.create_sheet("Painel", 1)
wp.sheet_view.showGridLines = False
rng_ = lambda col: f"Dados!${col}$2:${col}${N+1}"
MES, GER, PROD, META, REAL = rng_("A"), rng_("B"), rng_("D"), rng_("E"), rng_("F")

wp["A1"] = "Painel Comercial: Meta x Realizado (2025)"; wp["A1"].font = f(size=16, bold=True, color=AZUL)
wp["A3"] = "Produto:"; wp["A3"].font = f(bold=True)
wp["B3"] = "Todos"
wp["B3"].font = f(bold=True, color="0000FF"); wp["B3"].fill = PatternFill("solid", fgColor="FFF2CC"); wp["B3"].border = borda
dv = DataValidation(type="list", formula1='"Todos,Crédito,Seguros,Cartões,Consórcios"', allow_blank=False)
wp.add_data_validation(dv); dv.add("B3")
wp["C3"] = "← escolha o produto (dados sintéticos)"; wp["C3"].font = f(italic=True, color="7F7F7F", size=9)
wp["Z3"] = '=IF(B3="Todos","*",B3)'; wp["Z3"].font = f(color="7F7F7F", size=8)  # critério auxiliar
wp["Y3"] = "critério auxiliar do filtro"; wp["Y3"].font = f(color="7F7F7F", size=8)

# KPIs
kpis = [("A", "Meta total", f"=B18", brl), ("C", "Realizado", f"=C18", brl), ("E", "Atingimento", "=D18", pct),
        ("G", "Gerentes na meta", '=COUNTIF(D10:D17,">=1")&" de 8"', "@"),
        ("I", "Melhor gerente", "=INDEX(A10:A17,MATCH(MAX(D10:D17),D10:D17,0))", "@")]
for col, rot, form, nf in kpis:
    a = wp[f"{col}5"]; a.value = rot; a.font = f(size=9, color="FFFFFF", bold=True)
    a.fill = PatternFill("solid", fgColor=AZUL); a.alignment = Alignment(horizontal="center")
    v = wp[f"{col}6"]; v.value = form; v.number_format = nf; v.font = f(size=14, bold=True, color=AZUL)
    v.fill = PatternFill("solid", fgColor=CINZA); v.alignment = Alignment(horizontal="center")
    nxt = chr(ord(col) + 1)
    wp.merge_cells(f"{col}5:{nxt}5"); wp.merge_cells(f"{col}6:{nxt}6")

def cab(ref_row, titulos, col0="A"):
    for i, t in enumerate(titulos):
        c = wp.cell(row=ref_row, column=ord(col0) - 64 + i, value=t)
        c.font = f(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor=AZUL)
        c.alignment = Alignment(horizontal="center"); c.border = borda

# Por gerente (respeita o filtro de produto)
wp["A8"] = "Por gerente (respeita o filtro de produto)"; wp["A8"].font = f(bold=True, size=12)
cab(9, ["Gerente", "Meta", "Realizado", "Atingimento", "Status"])
gerentes = list(dict.fromkeys(df.Gerente))
for i, g in enumerate(gerentes):
    r = 10 + i
    wp[f"A{r}"] = g
    wp[f"B{r}"] = f"=SUMIFS({META},{GER},$A{r},{PROD},$Z$3)"
    wp[f"C{r}"] = f"=SUMIFS({REAL},{GER},$A{r},{PROD},$Z$3)"
    wp[f"D{r}"] = f"=IFERROR(C{r}/B{r},0)"
    wp[f"E{r}"] = f'=IF(D{r}>=1,"Atingiu",IF(D{r}>=0.9,"Quase lá","Abaixo"))'
wp["A18"] = "Total"
wp["B18"] = "=SUM(B10:B17)"; wp["C18"] = "=SUM(C10:C17)"; wp["D18"] = "=IFERROR(C18/B18,0)"; wp["E18"] = ""
for r in range(10, 19):
    for col in "ABCDE":
        c = wp[f"{col}{r}"]; c.font = f(bold=(r == 18)); c.border = borda
    for col in "BC": wp[f"{col}{r}"].number_format = brl
    wp[f"D{r}"].number_format = pct; wp[f"E{r}"].alignment = Alignment(horizontal="center")
for col in "ABCDE": wp[f"{col}18"].fill = PatternFill("solid", fgColor="D9E1F2")

# Por produto (todos os produtos, sempre)
wp["G8"] = "Por produto (sempre todos)"; wp["G8"].font = f(bold=True, size=12)
cab(9, ["Produto", "Meta", "Realizado", "Atingimento"], "G")
for i, p in enumerate(["Crédito", "Seguros", "Cartões", "Consórcios"]):
    r = 10 + i
    wp[f"G{r}"] = p
    wp[f"H{r}"] = f"=SUMIFS({META},{PROD},$G{r})"
    wp[f"I{r}"] = f"=SUMIFS({REAL},{PROD},$G{r})"
    wp[f"J{r}"] = f"=IFERROR(I{r}/H{r},0)"
    for col in "GHIJ": wp[f"{col}{r}"].font = f(); wp[f"{col}{r}"].border = borda
    wp[f"H{r}"].number_format = brl; wp[f"I{r}"].number_format = brl; wp[f"J{r}"].number_format = pct

# Por mês (respeita o filtro de produto)
wp["A20"] = "Por mês (respeita o filtro de produto)"; wp["A20"].font = f(bold=True, size=12)
cab(21, ["Mês", "Meta", "Realizado", "Atingimento"])
meses = sorted(df.Mes.unique())
for i, m in enumerate(meses):
    r = 22 + i
    wp[f"A{r}"] = pd.Timestamp(m).to_pydatetime(); wp[f"A{r}"].number_format = "mmm/yy"
    wp[f"B{r}"] = f"=SUMIFS({META},{MES},$A{r},{PROD},$Z$3)"
    wp[f"C{r}"] = f"=SUMIFS({REAL},{MES},$A{r},{PROD},$Z$3)"
    wp[f"D{r}"] = f"=IFERROR(C{r}/B{r},0)"
    for col in "ABCD": wp[f"{col}{r}"].font = f(); wp[f"{col}{r}"].border = borda
    wp[f"A{r}"].alignment = Alignment(horizontal="left")
    wp[f"B{r}"].number_format = brl; wp[f"C{r}"].number_format = brl; wp[f"D{r}"].number_format = pct

# Formatação condicional (atingimento)
verde = PatternFill("solid", bgColor="C6EFCE", fgColor="C6EFCE")
amar = PatternFill("solid", bgColor="FFEB9C", fgColor="FFEB9C")
verm = PatternFill("solid", bgColor="FFC7CE", fgColor="FFC7CE")
for rng in ["D10:D17", "J10:J13", "D22:D33"]:
    wp.conditional_formatting.add(rng, CellIsRule(operator="greaterThanOrEqual", formula=["1"], fill=verde))
    wp.conditional_formatting.add(rng, CellIsRule(operator="between", formula=["0.9", "0.99999"], fill=amar))
    wp.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0.9"], fill=verm))

# Gráficos
c1 = BarChart(); c1.type = "col"; c1.title = "Meta x Realizado por gerente"; c1.height = 8; c1.width = 17
c1.add_data(Reference(wp, min_col=2, max_col=3, min_row=9, max_row=17), titles_from_data=True)
c1.set_categories(Reference(wp, min_col=1, min_row=10, max_row=17)); c1.y_axis.numFmt = '#,##0'
c1.y_axis.delete = False; c1.x_axis.delete = False
wp.add_chart(c1, "L3")
c2 = LineChart(); c2.title = "Meta x Realizado por mês"; c2.height = 8; c2.width = 17
c2.add_data(Reference(wp, min_col=2, max_col=3, min_row=21, max_row=33), titles_from_data=True)
c2.set_categories(Reference(wp, min_col=1, min_row=22, max_row=33)); c2.y_axis.numFmt = '#,##0'
c2.y_axis.delete = False; c2.x_axis.delete = False; c2.x_axis.number_format = "mmm/yy"
for sr in c2.series: sr.smooth = False
wp.add_chart(c2, "L20")

for col, w in zip("ABCDEFGHIJK", [18, 15, 15, 13, 12, 3, 14, 15, 15, 13, 3]): wp.column_dimensions[col].width = w
wp.row_dimensions[6].height = 26
wb.save("excel/painel_comercial.xlsx")
print("ok")
