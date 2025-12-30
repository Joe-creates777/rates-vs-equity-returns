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
## Key Findings
- Equity returns exhibit **non-zero sensitivity** to interest rate changes, with effects varying by rate measure.
- Market responses are **not purely contemporaneous**; lagged rate changes contribute meaningful explanatory power.
- Rate–equity sensitivities are **time-varying**, strengthening or weakening across different macro environments.
- Decomposing rates into **nominal, real, and term structure components** reveals materially different equity responses.
<details>
<summary><strong>Detailed Results and Interpretation</strong></summary>

<br>

### Baseline Relationship Between Rates and Equity Returns
Across baseline specifications, equity returns exhibit a **statistically meaningful relationship** with changes in interest rates.
- Changes in U.S. Treasury yields are associated with systematic movements in equity returns.
- The sign and magnitude of sensitivity depend on the specific rate measure used.
- Short- to medium-term yields tend to show stronger contemporaneous associations than longer maturities.
These results suggest that equity markets respond not only to the level of rates, but also to **unexpected rate movements**.
### Lag Effects and Market Adjustment
Including lagged rate changes shows that equity market responses are **not purely instantaneous**.
- Lagged rate changes add explanatory power beyond contemporaneous effects.
- The strongest responses typically occur within short horizons.
- Lag structures help distinguish immediate repricing from delayed adjustment dynamics.
This highlights the importance of modeling **temporal dynamics**, rather than relying solely on same-day correlations.
### Time-Varying Sensitivity (Rolling Analysis)
Rolling-window regressions indicate that rate–equity sensitivities are **not stable over time**.
- Estimated betas vary substantially across different market periods.
- Periods of elevated macro uncertainty often coincide with stronger rate sensitivity.
- In calmer environments, estimated relationships weaken or temporarily disappear.
These findings caution against assuming constant parameters in macro–equity relationships.
### Comparison Across Rate Measures
Different interest rate measures produce **materially different equity responses**.
- Nominal yields, real yields, and term structure measures capture distinct channels.
- Real yields tend to show stronger associations during inflation-sensitive periods.
- Term structure variables provide complementary information beyond level changes alone.
This underscores the importance of **rate decomposition**, rather than treating interest rates as a single variable.
### Robustness Checks
Key results remain qualitatively consistent across alternative specifications:
- Different return constructions
- Alternative lag lengths
- Subsample splits
While magnitudes vary, the central patterns—non-zero sensitivity, lag effects, and time variation—persist.
</details>
