# Rates vs. Equity Returns
## Project Overview
This project investigates the empirical relationship between U.S. interest rate dynamics and equity market returns, with a focus on: 
- the timing of equity market responses to rate changes. 
- differences across rate measures (nominal, real, term structure).
- the stability of these relationships over time 
Rather than relying on market narratives, this project provides a fully reproducible, data-driven framework to quantify how interest rate movements are associated with equity returns. This repository is designed as a research-style empirical pipeline, emphasizing transparency, robustness, and interpretability.
## Research Questions
The analysis is centered around three core questions:
### Timing effects
Do equity returns react contemporaneously to interest rate changes, or with measurable lags?
### Which rate measures matter most?
How do different rate indicators—nominal Treasury yields, real yields, and term spreads—compare in explaining equity returns?
##3 Stability over time
Are these relationships stable across market environments, or do they vary across different macroeconomic regimes?
## Data Description
### Equity Data
- Broad equity market returns (e.g., major U.S. equity indices or ETFs)
- Daily frequency
- Returns computed using log differences
### Interest Rate Data
- U.S. Treasury yields (short-term and long-term)
- Real yields derived from inflation-protected securities
- Term structure measures (e.g., yield spreads)
- Daily frequency, aligned to equity trading days
### Sample Construction
- All time series are aligned on common trading dates
- Missing observations are handled consistently to avoid look-ahead bias
- Rate changes are computed as first differences unless otherwise specified
#### Note: All data used in this project are sourced from publicly available and widely used financial databases.
