# 🎯 Como avaliar este portfólio em 5 minutos

*(para recrutadores, gestores de RH e lideranças de dados)*

Olá! Este repositório foi organizado para que você não precise procurar: cada projeto tem **pergunta de negócio, resultado em tabela, método e instruções de execução**. Abaixo, o roteiro mais rápido de leitura.

## ⏱️ Roteiro de 5 minutos

| Tempo | O que abrir | O que você vai ver |
|---|---|---|
| 1 min | [README principal](README.md) | quem sou, stack e os 10 projetos com resultado em uma linha |
| 1 min | [Pipeline ETL + Dashboard](pipeline-etl-dashboard/dashboard.html) | um painel real gerado por código, aberto direto no navegador |
| 1 min | [Teste A/B](analise-teste-ab/README.md) | decisão de negócio com p-valor, intervalo de confiança e impacto em R$ |
| 1 min | [Retenção (coorte)](analise-cohort-retencao/README.md) | matriz de coorte, churn e LTV por segmento |
| 1 min | [CI verde](https://github.com/danielmartins-data/danielmartins-data/actions) | 11 testes automatizados rodando a cada push |

## ✅ O que está garantido por teste automatizado

Não é só "código que roda na minha máquina": o GitHub Actions executa, a cada push, os 10 projetos e valida as saídas.

- os 10 projetos executam de ponta a ponta;
- as regras de qualidade do pipeline ETL passam (7 de 7);
- o teste A/B tem p-valor coerente com a decisão tomada;
- a previsão tem 30 dias com intervalo de confiança consistente;
- a matriz de coorte é monotônica (retenção não sobe com o tempo);
- o RFM reproduz os números publicados no README;
- todo projeto publicado tem README com resumo, método, aviso de dados sintéticos e `requirements.txt`.

## 🔍 Perguntas que este portfólio responde

- **"Ele sabe SQL de verdade?"** → [Inadimplência](analise-inadimplencia-sql/consultas.sql): CTEs, window functions, safra, concentração.
- **"Ele entende estatística ou só usa biblioteca?"** → [Teste A/B](analise-teste-ab/analise.py): teste z implementado do zero, com IC e poder.
- **"Ele sabe preparar dado sujo?"** → [Pipeline ETL](pipeline-etl-dashboard/src/etl.py): log auditável de cada transformação.
- **"Ele entrega para o negócio?"** → todos os READMEs têm resumo executivo e recomendação.
- **"Ele cuida de qualidade de código?"** → `testes/`, `pytest.ini` e `.github/workflows/ci.yml`.

## ⚠️ Transparência

Todos os dados são **sintéticos (fictícios)**, gerados por script com seed fixa e sinalizados em cada README. Nenhuma informação de empresa real é usada. O objetivo é demonstrar método, não resultado comercial verdadeiro.

## 📬 Contato

[LinkedIn](https://www.linkedin.com/in/danielfernandomartins) · dfm21031983@gmail.com
