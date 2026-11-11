# 🎤 Guia de entrevista: como usar este portfólio

*(documento de trabalho do Daniel — fica no repositório porque organização também conta ponto)*

## A narrativa de 60 segundos

> "Tenho 24 anos de mercado financeiro, em Bradesco e Cielo, e migrei para dados. Por isso meus projetos começam sempre por uma pergunta de negócio, não por uma biblioteca. No repositório você encontra 10 projetos, todos com dados sintéticos avisados, cada um rodando com um comando e com teste automatizado no CI. Gosto de explicar resultado em uma tabela de resumo executivo — é assim que o gestor lê."

## Qual projeto abrir para cada pergunta

| Se o entrevistador perguntar… | Abra |
|---|---|
| "Você sabe SQL?" | `analise-inadimplencia-sql/consultas.sql` (CTE, `AVG OVER`, `RANK`, `NTILE`) |
| "Você sabe estatística ou só usa biblioteca?" | `analise-teste-ab/analise.py` (teste z, IC, poder — feito do zero) |
| "E machine learning?" | `analise-risco-credito` (regressão logística do zero, AUC, KS, ganho) |
| "Já tratou dado sujo?" | `pipeline-etl-dashboard/src/etl.py` (log auditável, 7 regras de qualidade) |
| "Como você entrega para o negócio?" | `pipeline-etl-dashboard/dashboard.html` (dashboard gerado por código) |
| "E Power BI / Excel?" | `painel-comercial-excel-powerbi` (modelo estrela, DAX, painel por fórmula) |
| "Você programa em R?" | `segmentacao-rfm-r-tableau` (R base + versão Python equivalente) |

## Perguntas que eu preciso saber responder de cabeça

1. **Por que a AUC da regressão logística é maior, mas o recall menor?** Porque o corte é fixo em 20% da base; a regra empata muitos clientes no mesmo ponto (2 pontos), então o corte dela inclui mais gente. Métrica diferente, decisão de custo diferente.
2. **Por que validar em 5 folds e não só dividir em treino/teste?** Com 3.000 linhas, uma única divisão depende da sorte do sorteio; a validação cruzada mostra a estabilidade do resultado.
3. **O que é KS?** A maior distância entre as curvas acumuladas de quem deu churn e de quem ficou — quanto maior, melhor o score separa os dois grupos.
4. **Por que dados sintéticos?** Porque não posso expor dado real de cliente, e porque com seed fixa qualquer pessoa reproduz o resultado. O método é o mesmo; muda a fonte.
5. **Por que o baseline ganhou do Holt-Winters na previsão?** Porque o efeito sazonal semanal domina e o modelo mais simples reage mais rápido. Escolhi o modelo pelo erro no teste, não pela sofisticação.

## Pontos fracos a assumir com honestidade (e o que já fiz)

- **Sem experiência profissional em dados ainda**: por isso o portfólio tem CI, testes e documentação — mostram hábito de trabalho, não só estudo.
- **O `.pbix` não está publicado**: está como issue #2, com o roteiro pronto.
- **O dashboard RFM no Tableau** ainda não publicado: issue #3.

## Checklist 24h antes da entrevista

- [ ] `pytest -q` rodando verde no meu computador
- [ ] badge de CI verde no GitHub
- [ ] LinkedIn apontando para o repositório
- [ ] abrir o `dashboard.html` uma vez para lembrar do visual
- [ ] reler o resumo executivo de 2 projetos que combinam com a vaga
