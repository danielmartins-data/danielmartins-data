# 🧮 Score de Risco de Churn: da regra de negócio ao modelo com AUC

> **Pergunta de negócio:** *para quem a equipe deve ligar primeiro? A regra simples que o comercial já usa é boa o suficiente, ou um modelo entrega mais?*

![Curva ROC](graficos/curva_roc.png)

## 🎯 Resumo executivo

O script compara um score de regras com uma regressão logística por validação cruzada estratificada em cinco folds. A padronização é aprendida apenas no conjunto de treino de cada fold, evitando vazamento de informação.

As métricas AUC, KS, precisão, recall e F1 são recalculadas a cada execução e salvas em `dados/comparacao_modelos.csv`. O corte operacional do exercício seleciona exatamente 20% dos registros, com desempate estável.

**Leitura didática:** AUC/KS avaliam a capacidade de ordenação; precisão/recall no top 20% representam o compromisso entre contatos disponíveis e casos identificados. Como o conjunto é sintético, não se deve usar o score para priorizar clientes reais.

## 🧠 Método

1. **Base sintética reproduzível** (`gerar_dados.py`): 3.000 clientes, churn de 20,6%, com relações programadas entre produtos, app, reclamações, tempo de casa e saldo; são associações definidas pelo gerador, não efeitos causais.
2. **Regressão logística implementada do zero** (gradiente descendente + regularização L2). A padronização é ajustada dentro de cada fold para evitar vazamento de informação — sem `sklearn`.
3. **Validação cruzada estratificada em 5 folds**: as probabilidades que aparecem nas métricas são de clientes fora do fold de treino. O modelo final é ajustado separadamente para produzir coeficientes.
4. **Métricas de classificação**: AUC (Mann-Whitney, com empates), **KS** (a métrica que o mercado de crédito usa), precisão, recall, F1 e acurácia no corte de 20% da base.
5. **Curva de ganho acumulado**: quantos churns a equipe captura contatando 10%, 20%, 30%… da base — a métrica que o gestor entende.
6. **Explicabilidade**: coeficientes convertidos em odds ratio, e faixas de risco com o churn observado em cada uma.

## 📁 Estrutura

```
analise-risco-credito/
├── gerar_dados.py               # base sintética (seed fixa)
├── analise.py                   # modelo, validação cruzada, métricas e gráficos
├── dados/
│   ├── clientes.csv
│   ├── base_com_score.csv       # 1 linha por cliente, com probabilidade e faixa
│   ├── comparacao_modelos.csv
│   ├── coeficientes.csv
│   └── ganho_acumulado.csv
└── graficos/
    ├── curva_roc.png
    ├── ganho_acumulado.png
    └── churn_por_score.png
```

## ▶️ Como rodar

```bash
pip install -r requirements.txt
python gerar_dados.py
python analise.py
```

## ⚠️ Sobre os dados

Dados **sintéticos** (fictícios), gerados por script com seed fixa. Não representam nenhuma instituição real e o modelo não deve ser usado com dados de pessoas reais sem avaliação de viés e conformidade com a LGPD.

## 🚀 Próximos passos

- [ ] Comparar com árvore de decisão e Random Forest (com a mesma validação)
- [ ] Avaliar **lift por decis** e definir o corte pelo custo da ligação vs. valor do cliente retido
- [ ] Checar viés entre segmentos (paridade de recall por segmento)
