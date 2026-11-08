# 🔁 Análise de Churn de Clientes (Python)

Projeto básico de análise exploratória: **quais clientes de um banco tendem a sair e o que eles têm em comum?** O resultado vira uma regra simples de priorização para a área comercial agir antes da perda.

> ⚠️ **Os dados são sintéticos (fictícios)**, gerados por `gerar_dados.py` com seed fixa. Servem para demonstrar o método e não representam nenhuma instituição real.

## 🎯 Perguntas respondidas

1. Qual a taxa geral de churn?
2. Quais fatores mais se associam à saída (produtos, app, reclamações, tempo de casa, segmento)?
3. Dá para criar uma lista de prioridade simples e explicável?

## 🧰 Ferramentas

Python (pandas, matplotlib)

## 🔎 Principais resultados

- **Churn geral:** 17,3% dos 3.000 clientes.
- **Vínculo protege:** clientes com 1 produto saem **31,2%**; com 5 ou mais, **7,4%**.
- **Digital retém:** quem não usa o app sai **24,9%**, contra **12,8%** de quem usa.
- **Reclamação é alerta:** sem reclamações, **11,7%**; com 2 ou mais, **35,9%**.
- **Tempo de casa:** até 1 ano, **28,0%**; mais de 7 anos, **13,2%**.
- **Segmento** tem efeito pequeno (Varejo 18,5%, Prime 15,2%, Exclusive 15,7%).

## 🧮 Score de risco (regra simples)

1 ponto para cada condição: **até 2 produtos**, **não usa app**, **teve reclamação**.

| Pontos | Clientes | Churn |
|---|---|---|
| 0 | 709 | 5,5% |
| 1 | 1.352 | 13,9% |
| 2 | 776 | 26,7% |
| 3 | 163 | **52,8%** |

Os clientes com 2 ou 3 pontos (939 de 3.000) são a lista de contato prioritária.

## 💡 Recomendações (exemplo)

- Ligar primeiro para quem tem 2-3 pontos de risco, tratando a reclamação em aberto.
- Estimular a adesão ao app e a contratação de um segundo ou terceiro produto.
- Acompanhar de perto o primeiro ano de relacionamento.

> Observação metodológica: é uma análise **descritiva**. As associações mostram padrões, não provam causa. Um próximo passo seria um modelo preditivo (regressão logística) validado em base de teste.

## ▶️ Como executar

```bash
pip install -r requirements.txt
python gerar_dados.py   # gera dados/clientes.csv
python analise.py       # tabelas no terminal e gráficos em graficos/
```

![Churn por fator](graficos/churn_por_fator.png)

---
Feito por **Daniel Fernando Martins** · [LinkedIn](https://www.linkedin.com/in/danielfernandomartins)
