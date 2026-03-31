# %%
"""
Forecast Evaluation Teachin — Live Demo Script
Based on MTP No. 6 (Bank of England, January 2026)
pip install forecast_evaluation
"""

import forecast_evaluation as fe

# %% SECTION 1: Loading and exploring data (~3 min)
# =============================================================================

# Load the built-in 2026 Forecast Evaluation Report dataset
data = fe.ForecastData(load_fer=True)

# Inspect what's available
print(data)
print("\nVariables:", data.forecasts["variable"].unique())
print("Sources:", data.forecasts["source"].unique())

# Focus on key macro variables
data.filter(variables=["cpisa", "gdpkp", "aweagg"])

# %% SECTION 2: Visualising forecasts
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

# Errors over time with moving-average smoothing
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
# SECTION 3: Accuracy                                                 (~5 min)
# =============================================================================

# Compute RMSE and MAE by variable, source, horizon
accuracy = fe.compute_accuracy_statistics(data=data, k=12)
print("\nAccuracy statistics:")
print(accuracy.to_df().head(20).to_string())

# Plot RMSE by horizon for all sources (including our benchmarks)
accuracy.plot(
    variable="cpisa",
    metric="yoy",
    frequency="Q",
    statistic="rmse",
    convert_to_percentage=True,
)

# RMSE ratios relative to AR(p) benchmark
comparison = fe.compare_to_benchmark(
    df=accuracy.to_df(),
    benchmark_model="baseline ar(p) model",
    statistic="rmse",
)
print("\nRMSE ratios vs AR(p):")
print(comparison.head(20).to_string())

# Plot comparison to benchmark
fe.plot_compare_to_benchmark(
    df=accuracy,
    variable="cpisa",
    metric="yoy",
    frequency="Q",
    benchmark_model="baseline ar(p) model",
    statistic="rmse",
)

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

# Diebold-Mariano test — is the RMSE difference significant?
dm = fe.diebold_mariano_table(
    data=data,
    benchmark_model="baseline ar(p) model",
)
print("\nDiebold-Mariano test results:")
print(dm.to_df().head(20).to_string())

# =============================================================================
# SECTION 5: Bias                                                     (~3 min)
# =============================================================================

# Test whether the mean forecast error is significantly different from zero
bias = fe.bias_analysis(data=data, source="mpr", k=12)

# Plot bias by horizon (with confidence bands) — CPI
bias.plot(variable="cpisa", source="mpr", metric="yoy", frequency="Q",
          convert_to_percentage=True)

# Also look at GDP growth
bias.plot(variable="gdpkp", source="mpr", metric="yoy", frequency="Q",
          convert_to_percentage=True)

# Summary table
print("\nBias analysis summary:")
print(bias.summary())

# =============================================================================
# SECTION 6: Efficiency                                               (~4 min)
# =============================================================================

# --- Weak efficiency: are forecast revisions predictable? ---
we = fe.weak_efficiency_analysis(data=data, source="mpr", k=12)
print("\nWeak efficiency results:")
print(we.to_df().to_string())

# --- Strong efficiency: Blanchard-Leigh regression ---
# Do CPI inflation forecast errors correlate with the forecaster's own
# GDP growth forecasts? (Uses own forecasts, not external ones.)
bl = fe.blanchard_leigh_horizon_analysis(
    data=data,
    source="mpr",
    outcome_variable="cpisa",
    outcome_metric="yoy",
    instrument_variable="gdpkp",
    instrument_metric="yoy",
)
print("\nBlanchard-Leigh (strong efficiency):")
print(bl.to_df().to_string())
bl.plot()

# =============================================================================
# SECTION 7: Rolling analysis                                         (~3 min)
# =============================================================================

# Filter to a manageable subset for rolling windows
data_rolling = data.copy()
data_rolling.filter(variables=["cpisa"], sources=["mpr"], metrics=["yoy"])

# Rolling bias — shows WHEN bias changed, not just WHETHER it exists
rolling_bias = fe.rolling_analysis(
    data=data_rolling,
    window_size=40,
    analysis_func=fe.bias_analysis,
    analysis_args={"k": 12},
)
rolling_bias.plot(variable="cpisa", source="mpr", horizons=[0, 4, 8])

# Fluctuation test — adjusts critical values for repeated testing
fluct_bias = fe.fluctuation_tests(
    data=data_rolling,
    window_size=40,
    test_func=fe.bias_analysis,
    test_args={"k": 12},
)
fluct_bias.plot(variable="cpisa", horizons=[0, 4, 8])

# Rolling Diebold-Mariano — has relative accuracy shifted over time?
data_dm_rolling = data.copy()
data_dm_rolling.filter(
    variables=["cpisa"], metrics=["yoy"],
    sources=["mpr", "baseline ar(p) model"],
)

rolling_dm = fe.rolling_analysis(
    data=data_dm_rolling,
    window_size=40,
    analysis_func=fe.diebold_mariano_table,
    analysis_args={"benchmark_model": "baseline ar(p) model"},
)
rolling_dm.plot(variable="cpisa", horizons=[0, 4])

# =============================================================================
# SECTION 8: Extra labels                                             (~3 min)
# =============================================================================

# Forecasts can carry metadata columns beyond 'source'.
# Useful for distinguishing scenarios, model families, conditioning paths, etc.

# Create a fresh ForecastData and add sample forecasts with an extra label
sample_forecasts = fe.create_sample_forecasts()
sample_forecasts["model_family"] = "experimental"
print("\nSample forecasts with extra label:")
print(sample_forecasts.head().to_string())

data_extra = fe.ForecastData(load_fer=True)
data_extra.add_forecasts(sample_forecasts, extra_ids=["model_family"])

# The extra column becomes part of the unique identifier.
# The same 'source' under different labels is treated as separate sets.
print("\nData with extra labels (tail):")
print(data_extra.df.tail(10).to_string())
print("\nData without extra labels (head):")
print(data_extra.df.head(10).to_string())

# =============================================================================
# SECTION 9: Interactive Dashboard                                    (~2 min)
# =============================================================================

print("\n" + "=" * 60)
print("Launching dashboard...")
print("=" * 60)

# data.run_dashboard()                   # opens in browser at localhost:8000
# data.run_dashboard(from_jupyter=True)  # embed in Jupyter
