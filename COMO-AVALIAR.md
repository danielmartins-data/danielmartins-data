# 🎯 Como avaliar este portfólio em 5 minutos

*(para recrutadores, gestores de RH e lideranças de dados)*

Olá! Este repositório foi organizado para que você não precise procurar: cada projeto tem **pergunta de negócio, resultado em tabela, método e instruções de execução**. Abaixo, o roteiro mais rápido de leitura.

## ⏱️ Roteiro de 5 minutos

| Tempo | O que abrir | O que você vai ver |
|---|---|---|
| 1 min | [README principal](README.md) | perfil, competências demonstradas e três projetos prioritários |
| 1 min | [Pipeline ETL e qualidade](pipeline-etl-dashboard/README.md) | um dashboard HTML gerado por código, aberto direto no navegador |
| 1 min | [Análise de inadimplência SQL](analise-inadimplencia-sql/README.md) | exercício estatístico em dados sintéticos, com p-valor e intervalo de confiança |
| 1 min | [Análise de vendas](analise-vendas/README.md) | matriz de coorte, churn e LTV por segmento |
| 1 min | [CI / Actions](https://github.com/danielmartins-data/danielmartins-data/actions) | confira a execução mais recente da matriz Python e do job R |

## ✅ O que está garantido por teste automatizado

O GitHub Actions está configurado para executar a suíte em pull requests direcionados à main e em pushes para main. Os testes executam análises selecionadas e verificam saídas específicas; não substituem revisão manual. Consulte o status e os logs da execução mais recente antes de considerar o CI aprovado.

- a suíte cobre estrutura dos projetos e análises selecionadas; não equivale a uma garantia de que cada projeto foi testado integralmente de ponta a ponta;
- o pipeline ETL verifica sete regras e interrompe a execução quando alguma falha;
- o exercício A/B valida limites do p-valor e coerência da decisão estatística na base simulada;
- a previsão gera 30 dias e compara baseline sazonal com Holt-Winters; a faixa de incerteza é exploratória, não calibrada;
- a matriz de coorte é testada quanto à monotonicidade, usando janelas aproximadas de 30 dias;
- o RFM reproduz os números publicados no README;
- a suíte verifica estrutura, documentação e saídas selecionadas; consulte os testes para conhecer exatamente a cobertura.

## 🔍 Perguntas que este portfólio responde

- **"Ele sabe SQL de verdade?"** → [Inadimplência](analise-inadimplencia-sql/consultas.sql): CTEs, window functions, safra, concentração.
- **"Ele entende estatística ou só usa biblioteca?"** → [Teste A/B](analise-teste-ab/analise.py): teste z aproximado e cálculo de amostra; exercício sintético com diferença programada na geração.
- **"Ele sabe preparar dado sujo?"** → [Pipeline ETL](pipeline-etl-dashboard/src/etl.py): log auditável de cada transformação.
- **"Ele entrega para o negócio?"** → os projetos selecionados apresentam problema, método e leituras de negócio.
- **"Ele cuida de qualidade de código?"** → `testes/`, `pytest.ini` e `.github/workflows/ci.yml`.

## ⚠️ Transparência

Todos os dados são **sintéticos (fictícios)**, gerados por script com seed fixa e sinalizados em cada README. Nenhuma informação de empresa real é usada. O objetivo é demonstrar método, não resultado comercial verdadeiro. No teste A/B, a diferença entre grupos foi construída na geração dos dados; significância estatística nesse cenário não comprova efeito causal nem aumento real de conversão. Métricas de previsão e retenção também descrevem apenas as bases simuladas e suas hipóteses.

## 📬 Contato

[LinkedIn](https://www.linkedin.com/in/danielfernandomartins) · dfm21031983@gmail.com
