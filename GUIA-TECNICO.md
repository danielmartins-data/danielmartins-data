# Guia técnico de avaliação

Este guia resume o que pode ser inspecionado diretamente no repositório. Os projetos usam bases sintéticas; métricas e conclusões não devem ser interpretadas como resultados de clientes ou empresas reais.

## 1. Pipeline ETL e qualidade de dados

**Onde olhar**
- `pipeline-etl-dashboard/src/etl.py`
- `pipeline-etl-dashboard/dados/`
- `testes/test_pipeline_etl.py`

**O que inspecionar**
- Leitura e tratamento de dados operacionais simulados.
- Padronização, deduplicação, tratamento de devoluções e registro das transformações.
- Regras de qualidade com interrupção do fluxo quando há reprovação.
- Persistência/saídas analíticas e dashboard HTML.

**Perguntas para aprofundar**
- Como você decidiu o tratamento de cada tipo de dado inválido?
- Quais regras são bloqueantes e quais poderiam gerar apenas alerta?
- Como garantir idempotência e rastreabilidade numa carga recorrente?

## 2. Inadimplência com SQL

**Onde olhar**
- `analise-inadimplencia-sql/consultas.sql`
- `analise-inadimplencia-sql/gerar_dados.py`
- `analise-inadimplencia-sql/README.md`

**O que inspecionar**
- Consultas em SQLite com CTEs, agregações, CASE WHEN, funções de janela e subqueries.
- Indicadores por produto, faixa de score, safra e concentração.
- Definição operacional explícita de inadimplência: contrato com mais de 90 dias de atraso.

**Perguntas para aprofundar**
- Como mudariam os resultados com outra definição de inadimplência?
- Qual denominador é usado em cada taxa: contratos ou exposição financeira?
- Como validaria os resultados com uma segunda consulta independente?

## 3. Análise de vendas

**Onde olhar**
- `analise-vendas/`
- `analise-vendas/README.md`

**O que inspecionar**
- Limpeza e tratamento de campos ausentes.
- Agregações por período, produto, região e canal em SQLite.
- Indicadores e recomendações comerciais vinculados às análises.

**Perguntas para aprofundar**
- Como o tratamento de pedidos duplicados afeta receita e ticket?
- Por que preservar a categoria “Não informada” em vez de descartar os registros?
- Como monitoraria a qualidade da dimensão geográfica em produção?

## Qualidade, testes e automação

- Suíte automatizada: `testes/`, executada com `pytest -q`.
- Verificação estática de erros críticos via Flake8 no workflow `.github/workflows/ci.yml`.
- Matriz Python configurada para 3.10, 3.11 e 3.12.
- Job dedicado executa o script RFM em R base.
- Consulte a aba [GitHub Actions](https://github.com/danielmartins-data/danielmartins-data/actions) para o status da execução mais recente. A configuração do workflow não significa, por si só, que toda execução esteja aprovada.

## Limites conhecidos e próximos passos

- As bases são sintéticas e não comprovam efeito causal, performance comercial real ou validade para decisões de crédito.
- SQL executado e demonstrado nos projetos usa SQLite; outros dialetos exigem validação específica.
- A faixa exploratória da previsão não é um intervalo preditivo calibrado.
- O teste A/B tem diferença programada na geração da base; significância estatística nessa simulação não prova impacto causal.
- Power BI/DAX e Tableau têm materiais de apoio, mas não são apresentados como dashboards públicos publicados nesta vitrine.
- Evoluções relevantes: empacotar ETL como módulo testável, adicionar testes de contrato por regra, ampliar testes de integração SQL e publicar artefatos BI reproduzíveis.

## Como reproduzir

Na raiz do repositório:

```bash
python -m pip install -r requirements.txt
pytest -q
```

Para entender uma análise específica, siga também as instruções e dependências do README dentro da pasta do projeto.
