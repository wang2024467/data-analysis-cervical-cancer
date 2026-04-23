#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
in_csv <- if (length(args) >= 1) args[[1]] else "data/raw/risk_factors_cervical_cancer.csv"
out_dir <- if (length(args) >= 2) args[[2]] else "extensions/outputs/figures"

if (!file.exists(in_csv)) {
  stop(sprintf("Input CSV not found: %s", in_csv))
}

dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

raw <- read.csv(in_csv, stringsAsFactors = FALSE)

normalize_name <- function(x) {
  x <- tolower(x)
  x <- gsub("[^a-z0-9]+", "_", x)
  x <- gsub("_+", "_", x)
  x <- gsub("^_|_$", "", x)
  x
}

names(raw) <- vapply(names(raw), normalize_name, character(1))

required <- c("age", "smokes", "stds", "biopsy")
missing_cols <- setdiff(required, names(raw))
if (length(missing_cols) > 0) {
  stop(sprintf("Missing required columns: %s", paste(missing_cols, collapse = ", ")))
}

for (col in required) {
  raw[[col]][raw[[col]] %in% c("?", "", "NA", "NaN")] <- NA
  raw[[col]] <- suppressWarnings(as.numeric(raw[[col]]))
}

model_df <- raw[, required]
model_df <- model_df[complete.cases(model_df), ]
if (nrow(model_df) < 20) {
  stop("Not enough complete rows for a stable logistic regression fit")
}

fit <- glm(biopsy ~ age + smokes + stds, data = model_df, family = binomial())
coef_tbl <- summary(fit)$coefficients
or_df <- data.frame(
  term = rownames(coef_tbl),
  estimate = coef_tbl[, 1],
  odds_ratio = exp(coef_tbl[, 1]),
  p_value = coef_tbl[, 4],
  row.names = NULL
)

write.csv(or_df, file.path(out_dir, "r_logit_odds_ratio.csv"), row.names = FALSE)

pred <- predict(fit, type = "response")
plot_path <- file.path(out_dir, "r_predicted_risk_density.png")
png(plot_path, width = 900, height = 550)
hist(pred, breaks = 25, main = "Predicted Biopsy Risk (R glm)", xlab = "Predicted probability", col = "steelblue")
abline(v = mean(model_df$biopsy), col = "firebrick", lwd = 2, lty = 2)
dev.off()

cat(sprintf("Saved: %s\n", file.path(out_dir, "r_logit_odds_ratio.csv")))
cat(sprintf("Saved: %s\n", plot_path))
