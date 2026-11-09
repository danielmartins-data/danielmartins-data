# =====================================================================
# Segmentação de clientes (RFM) com R
# ---------------------------------------------------------------------
# Entrada : dados/fato_transacoes.csv  (transações por cliente, dados SINTÉTICOS)
#           dados/dim_cliente.csv      (cadastro dos clientes)
# Saída   : dados/rfm_clientes.csv     (1 linha por cliente, base para o Tableau)
#           dados/resumo_segmentos.csv (1 linha por segmento)
#
# Como rodar (a partir da pasta do projeto, em UTF-8):
#   Rscript analise_rfm.R        # ou abra no RStudio, defina a pasta e use Source
#
# Só R base: nenhum pacote para instalar.
# =====================================================================

options(scipen = 999)  # evita notação científica (1e+05) nos CSVs

# ---------- 1. Leitura e preparo ----------
arq_trans <- "dados/fato_transacoes.csv"
arq_cli   <- "dados/dim_cliente.csv"
stopifnot("rode o script a partir da pasta do projeto" = file.exists(arq_trans, arq_cli))

transacoes <- read.csv(arq_trans, stringsAsFactors = FALSE, fileEncoding = "UTF-8")
clientes   <- read.csv(arq_cli,   stringsAsFactors = FALSE, fileEncoding = "UTF-8")

transacoes$Data <- as.Date(transacoes$Data)
# "Segmento" do cadastro é o setor do cliente; renomeio para não confundir com o segmento RFM
names(clientes)[names(clientes) == "Segmento"] <- "Segmento_Cliente"

data_ref <- as.Date("2025-12-31")  # data de referência para a recência

# ---------- 2. Recência, Frequência e Valor por cliente ----------
ids     <- as.character(sort(unique(transacoes$id_cliente)))
valor   <- tapply(transacoes$Valor, transacoes$id_cliente, sum)
freq    <- table(transacoes$id_cliente)
ultima  <- tapply(as.numeric(transacoes$Data), transacoes$id_cliente, max)
gerente <- tapply(transacoes$Gerente, transacoes$id_cliente, function(x) x[1])

rfm <- data.frame(
  id_cliente    = as.integer(ids),
  Ultima_Compra = as.Date(as.numeric(ultima[ids]), origin = "1970-01-01"),
  Frequencia    = as.integer(freq[ids]),
  Valor_Total   = round(as.numeric(valor[ids]), 2),
  Gerente       = as.character(gerente[ids]),
  stringsAsFactors = FALSE
)
rfm$Recencia_Dias <- as.integer(data_ref - rfm$Ultima_Compra)
rfm$Ticket_Medio  <- round(rfm$Valor_Total / rfm$Frequencia, 2)

# ---------- 3. Notas de 1 a 5 (quintis) ----------
# Posição média (empates recebem a mesma nota) dividida em 5 faixas.
quintil <- function(x) ceiling(5 * rank(x, ties.method = "average") / length(x))

rfm$R <- 6 - quintil(rfm$Recencia_Dias)  # menos dias desde a última compra = nota maior
rfm$F <- quintil(rfm$Frequencia)
rfm$M <- quintil(rfm$Valor_Total)
rfm$Score_RFM <- paste0(rfm$R, rfm$F, rfm$M)

# ---------- 4. Segmentos ----------
# A ordem importa: a regra mais abaixo prevalece sobre as de cima.
rfm$Segmento_RFM <- "Precisam de Atenção"
rfm$Segmento_RFM[rfm$R <= 2 & rfm$F <= 2] <- "Hibernando"
rfm$Segmento_RFM[rfm$R >= 4 & rfm$F <= 2] <- "Novos e Promissores"
rfm$Segmento_RFM[rfm$R <= 2 & rfm$F >= 3] <- "Em Risco"
rfm$Segmento_RFM[rfm$R <= 2 & rfm$M >= 4] <- "Grandes Valores em Risco"
rfm$Segmento_RFM[rfm$R >= 3 & rfm$F >= 4] <- "Fiéis"
rfm$Segmento_RFM[rfm$R >= 4 & rfm$F >= 4 & rfm$M >= 4] <- "Campeões"

# ---------- 5. Junta com o cadastro (inclui clientes sem compra no ano) ----------
base <- merge(clientes, rfm, by = "id_cliente", all.x = TRUE)
base <- base[order(base$id_cliente), ]

sem_compra <- is.na(base$Frequencia)
base$Frequencia[sem_compra]   <- 0L
base$Valor_Total[sem_compra]  <- 0
base$Gerente[sem_compra]      <- "Não identificado"
base$Segmento_RFM[sem_compra] <- "Sem compras em 2025"

colunas <- c("id_cliente", "Cliente", "Segmento_Cliente", "Porte", "Regiao", "UF", "Gerente",
             "Ultima_Compra", "Recencia_Dias", "Frequencia", "Valor_Total", "Ticket_Medio",
             "R", "F", "M", "Score_RFM", "Segmento_RFM")
base <- base[, colunas]

# ---------- 6. Resumo por segmento ----------
seg <- unique(base$Segmento_RFM)
resumo <- data.frame(Segmento_RFM = seg, stringsAsFactors = FALSE)
resumo$Clientes            <- as.integer(table(base$Segmento_RFM)[seg])
resumo$Valor_Total         <- round(as.numeric(tapply(base$Valor_Total, base$Segmento_RFM, sum)[seg]), 2)
resumo$Pct_Clientes        <- round(100 * resumo$Clientes / sum(resumo$Clientes), 1)
resumo$Pct_Valor           <- round(100 * resumo$Valor_Total / sum(resumo$Valor_Total), 1)
resumo$Valor_Medio_Cliente <- round(resumo$Valor_Total / resumo$Clientes, 2)
resumo$Recencia_Media_Dias <- round(as.numeric(tapply(base$Recencia_Dias, base$Segmento_RFM, mean)[seg]))
resumo$Frequencia_Media    <- round(as.numeric(tapply(base$Frequencia, base$Segmento_RFM, mean)[seg]), 1)
resumo <- resumo[order(-resumo$Valor_Total), ]

# ---------- 7. Conferência e exportação ----------
# O valor segmentado tem que ser igual ao valor das transações.
stopifnot(abs(sum(base$Valor_Total) - sum(transacoes$Valor)) < 0.01)

write.csv(base,   "dados/rfm_clientes.csv",     row.names = FALSE, quote = FALSE, na = "", fileEncoding = "UTF-8")
write.csv(resumo, "dados/resumo_segmentos.csv", row.names = FALSE, quote = FALSE, na = "", fileEncoding = "UTF-8")

cat("Clientes no cadastro:", nrow(base), "| com compra:", sum(!sem_compra), "| sem compra:", sum(sem_compra), "\n")
cat("Valor total: R$", format(sum(base$Valor_Total), big.mark = ".", decimal.mark = ",", nsmall = 2), "\n\n")
print(resumo, row.names = FALSE)
