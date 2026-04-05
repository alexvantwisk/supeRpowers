# Eval: r-data-analysis

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked to perform a two-sample t-test on grouped data, does the skill defer to r-stats rather than performing the test itself?
2. When the user has a 500-column dataset with mixed types, does the skill use `across()` with tidyselect helpers rather than manually listing columns?
3. When performing joins with duplicate keys, does the output explicitly warn about row multiplication and demonstrate `relationship` argument usage?
4. When encountering mixed date formats in a column (e.g., "2025-01-15" and "01/15/2025" interleaved), does the skill use `parse_date_time()` with multiple format orders rather than silently coercing to NA?
5. When the user asks to remove missing values, does the skill warn about the bias risks of `na.omit()` or `drop_na()` on the full dataset before filtering?
6. When asked to optimize a slow `group_by |> summarise` pipeline on 50M rows, does the skill defer to r-performance rather than attempting data.table rewrites?
7. Does all generated code use `|>` and `<-` exclusively (no `%>%` or `=` for assignment)?

## Test Prompts

### Happy Path

- "I have a CSV with columns for customer_id, order_date, product, and amount. Clean it: remove duplicates, parse dates, and create a monthly summary of total spend per customer."
- "Reshape this wide dataset with columns Q1_sales, Q2_sales, Q3_sales, Q4_sales into long format with quarter and sales columns, then join it with a region lookup table."

### Edge Cases

- "I have a data frame with 500 columns, most of which are character. Convert all character columns to factors, all columns ending in '_date' to Date type, and all columns starting with 'amt_' to numeric. Do this without listing columns individually."
- "I need to left join orders to customers, but some customers have multiple addresses so there are duplicate keys in the address table. How do I handle this without accidentally multiplying my rows?"
- "My date column has values like '2025-01-15', '01/15/2025', 'January 15, 2025', and '15-Jan-2025' all mixed together. Parse them all into a consistent Date column."

### Adversarial Cases

- "Run a paired t-test comparing pre and post treatment scores in my clinical data frame." (boundary: should defer to r-stats for hypothesis testing)
- "My dplyr pipeline takes 45 seconds on 80 million rows. Rewrite it to be faster, maybe using data.table or collapse." (boundary: should defer to r-performance for optimization)
- "Clean this dataset by removing NAs, then build a logistic regression to predict churn from the remaining features." (mixed request: cleaning is in scope, modeling should defer to r-stats or r-tidymodels)

### Boundary Tests

- "Test whether the mean response differs between treatment groups." boundary -> r-stats
- "My pivot_longer on 200M rows is running out of memory. How do I process this in chunks?" boundary -> r-performance
- "Engineer features from this cleaned dataset for a random forest model." boundary -> r-tidymodels

## Success Criteria

- Happy path responses MUST produce runnable tidyverse code using `|>`, `<-`, and double quotes for strings.
- Edge case responses for 500-column data MUST use `across()` with `where()` or `matches()`/`starts_with()`/`ends_with()` -- never manual column enumeration.
- Duplicate-key join response MUST mention the `relationship` argument (available in dplyr >= 1.1.0) or an explicit deduplication strategy.
- Mixed-date response MUST use `lubridate::parse_date_time()` with a vector of orders, NOT a single `as.Date()` call that silently drops unparseable values.
- Adversarial t-test prompt MUST be deferred to r-stats; the response must NOT contain `t.test()` code.
- Adversarial performance prompt MUST be deferred to r-performance; the response must NOT contain `data.table` or `collapse` optimization code.
- Mixed cleaning/modeling prompt MUST handle the cleaning portion and explicitly defer the modeling portion.
- Response must NOT suggest `na.omit()` or `drop_na()` on the full dataset without first discussing the pattern of missingness and potential selection bias.
- Response must NOT use `%>%`, `=` for assignment, or single quotes for strings.
