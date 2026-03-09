"""
Forecast Evaluation Teachin — Live Demo Script
Based on MTP No. 6 (Bank of England, January 2026)
pip install forecast_evaluation

Timing guide (total ~20 minutes):
  Section 1: Loading and exploring       ~3 min
  Section 2: Visualising forecasts       ~3 min
  Section 3: Accuracy                    ~4 min
  Section 4: Bias                        ~3 min
  Section 5: Efficiency                  ~3 min
  Section 6: Rolling analysis            ~2 min
  Section 7: Data revisions              ~1 min
  Section 8: Dashboard                   ~1 min
"""

import forecast_evaluation as fe

# =============================================================================
# SECTION 1: Loading and exploring data                               (~3 min)
# =============================================================================

# Load the built-in 2026 Forecast Evaluation Report dataset
data = fe.ForecastData(load_fer=True)

# Inspect what's available
print(data)
print("\nVariables:", data.forecasts["variable"].unique())
print("Sources:", data.forecasts["source"].unique())
print("Frequency:", data.forecasts["frequency"].unique())
print("Shape:", data.forecasts.shape)

# Focus on key macro variables
data.filter(variables=["cpisa", "gdpkp", "aweagg"])
print("\nAfter filter:", data.forecasts.shape)

# Peek at the data structure
print("\nData structure:")
print(
    data.forecasts[
        ["date", "vintage_date", "variable", "source", "forecast_horizon", "value"]
    ]
    .head(10)
    .to_string()
)

# =============================================================================
# SECTION 2: Visualising forecasts                                    (~3 min)
# =============================================================================

# Hedgehog plot — each line is a forecast vintage; the dark line is outturns
fe.plot_hedgehog(
    data=data,
    variable="cpisa",
    forecast_source="mpr",
    metric="yoy",
    frequency="Q",
    k=12,
    convert_to_percentage=True,
)

# Distribution of forecast errors — where do recent errors sit?
fe.plot_forecast_error_density(
    data=data,
    horizon=4,  # 1-year-ahead errors
    variable="cpisa",
    metric="yoy",
    frequency="Q",
    source="mpr",
    k=12,
)

# Errors over time
fe.plot_errors_across_time(
    data=data,
    variable="cpisa",
    metric="yoy",
    horizons=4,
    sources="mpr",
    frequency="Q",
    k=12,
    ma_window=4,
)

# =============================================================================
# SECTION 3: Accuracy                                                 (~4 min)
# =============================================================================

# Compute RMSE and MAE by variable, source, horizon
accuracy = fe.compute_accuracy_statistics(data=data, k=12)
print("\nAccuracy statistics:")
print(accuracy.to_df().head(20).to_string())

# Plot RMSE by horizon for all sources
fe.plot_accuracy(
    accuracy,
    variable="cpisa",
    metric="yoy",
    frequency="Q",
    statistic="rmse",
)

# RMSE ratios relative to AR(p) benchmark
comparison = fe.compare_to_benchmark(
    df=accuracy.to_df(),
    benchmark_model="baseline ar(p) model",
    statistic="rmse",
)
print("\nRMSE ratios vs AR(p):")
print(comparison.to_string())

# Comparison table (selected horizons)
table = fe.create_comparison_table(
    df=accuracy.to_df(),
    variable="cpisa",
    metric="yoy",
    frequency="Q",
    benchmark_model="baseline ar(p) model",
    statistic="rmse",
    horizons=[0, 1, 2, 4, 8, 12],
)
print("\nComparison table (CPI inflation):")
print(table.to_string())

# Diebold-Mariano test — is the difference significant?
dm = fe.diebold_mariano_table(
    data=data,
    benchmark_model="baseline ar(p) model",
)
print("\nDiebold-Mariano test:")
print(dm.to_df().to_string())
dm.plot(variable="cpisa", metric="yoy", frequency="Q")

# =============================================================================
# SECTION 4: Bias                                                     (~3 min)
# =============================================================================

# Test whether the mean forecast error is significantly different from zero
bias = fe.bias_analysis(data=data)
print("\nBias analysis:")
print(bias.summary())

# Plot bias by horizon (with confidence bands)
bias.plot(variable="cpisa", metric="yoy", frequency="Q")

# Also look at GDP growth
bias.plot(variable="gdpkp", metric="yoy", frequency="Q")

# =============================================================================
# SECTION 5: Efficiency                                               (~3 min)
# =============================================================================

# Weak efficiency — are forecast revisions predictable?
we = fe.weak_efficiency_analysis(data=data)
print("\nWeak efficiency (revision predictability):")
print(we.to_df().to_string())

# Strong efficiency — Blanchard-Leigh regression
# Do CPI inflation forecast errors correlate with GDP growth forecasts?
bl = fe.blanchard_leigh_horizon_analysis(
    data=data,
    outcome_variable="cpisa",
    outcome_metric="yoy",
    instrument_variable="gdpkp",
    instrument_metric="yoy",
)
print("\nBlanchard-Leigh (strong efficiency):")
print(bl.to_df().to_string())
bl.plot()

# =============================================================================
# SECTION 6: Rolling analysis                                         (~2 min)
# =============================================================================

# Rolling bias — shows WHEN bias changed, not just WHETHER it exists
rolling_bias = fe.rolling_analysis(
    data=data,
    window_size=16,
    analysis_func=fe.bias_analysis,
    analysis_args={},
)
rolling_bias.plot(variable="aweagg", metric="yoy", frequency="Q")

# Rolling Diebold-Mariano — has relative accuracy shifted over time?
rolling_dm = fe.rolling_analysis(
    data=data,
    window_size=16,
    analysis_func=fe.diebold_mariano_table,
    analysis_args={"benchmark_model": "baseline ar(p) model"},
)
rolling_dm.plot(variable="cpisa", metric="yoy", frequency="Q")

# =============================================================================
# SECTION 7: Data revisions                                           (~1 min)
# =============================================================================

# How much do outturns change across vintages?
fe.plot_outturn_revisions(
    data=data,
    variable="gdpkp",
    metric="yoy",
    frequency="Q",
    k=12,
)

# Are forecast errors correlated with data revisions?
revisions_corr = fe.revisions_errors_correlation_analysis(data=data)
print("\nRevisions-errors correlation:")
print(revisions_corr.to_df().to_string())

# =============================================================================
# SECTION 8: Interactive Dashboard                                    (~1 min)
# =============================================================================

print("\n" + "=" * 60)
print("Launch dashboard: data.run_dashboard()")
print("=" * 60)

# data.run_dashboard()                   # opens in browser
# data.run_dashboard(from_jupyter=True)  # embed in Jupyter
