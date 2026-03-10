"""Generate illustration plots for the slides using the default FER data."""

import pandas as pd
import forecast_evaluation as fe
import matplotlib.pyplot as plt
import os

os.makedirs("images", exist_ok=True)

# Load FER data
data = fe.ForecastData(load_fer=True)
data.filter(custom_filter=fe.filter_fer_variables)

# ── 1. Hedgehog chart (sniff tests) — aweagg ──
fig, ax = fe.plot_hedgehog(
    data=data, variable="aweagg",
    forecast_source="mpr", metric="yoy",
    frequency="Q", k=12, convert_to_percentage=True,
    return_plot=True,
)
fig.savefig("images/hedgehog.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("✓ hedgehog.png (aweagg)")

# ── 2. Errors across time (sniff tests) ──
fig, ax = fe.plot_errors_across_time(
    data=data, variable="cpisa",
    metric="yoy", horizons=4, sources="mpr",
    frequency="Q", k=12, ma_window=1,
    convert_to_percentage=True, return_plot=True,
)
fig.savefig("images/errors_across_time.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("✓ errors_across_time.png")

# ── 3. Forecast error density (sniff tests) ──
fig, ax = fe.plot_forecast_error_density(
    data=data, variable="cpisa", horizon=4,
    metric="yoy", frequency="Q", source="mpr", k=12,
    highlight_dates=pd.date_range(start="2022-01-01", end="2024-12-31", freq="QE"),
    return_plot=True,
)
fig.savefig("images/error_density.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("✓ error_density.png")

# ── 4. Revision plot (after storing data slide) — GDP errors at k=0 vs k=12 ──
existing_plot = fe.plot_errors_across_time(
    data=data, variable="gdpkp", metric="yoy",
    error="raw", horizons=[0], sources="mpr",
    frequency="Q", k=0, ma_window=4,
    convert_to_percentage=True, return_plot=True,
    custom_labels={"mpr": "k=0"},
)
fig, ax = fe.plot_errors_across_time(
    data=data, variable="gdpkp", metric="yoy",
    frequency="Q", error="raw", horizons=[0],
    sources="mpr", k=12, ma_window=4,
    convert_to_percentage=True,
    existing_plot=existing_plot, return_plot=True,
    custom_labels={"mpr": "k=12"},
)
fig.savefig("images/outturn_revisions.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("✓ outturn_revisions.png (GDP errors k=0 vs k=12)")

# ── 5. Accuracy (RMSE by horizon) ──
accuracy = fe.compute_accuracy_statistics(data=data, k=12)
fig, ax = accuracy.plot(
    variable="cpisa", metric="yoy",
    frequency="Q", statistic="rmse",
    convert_to_percentage=True, return_plot=True,
)
fig.savefig("images/accuracy_rmse.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("✓ accuracy_rmse.png")

# ── 6. Relative accuracy (benchmark comparison) ──
fig, ax = fe.plot_compare_to_benchmark(
    df=accuracy.to_df(), variable="cpisa", metric="yoy",
    frequency="Q", benchmark_model="baseline ar(p) model",
    statistic="rmse", return_plot=True,
)
fig.savefig("images/relative_accuracy.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("✓ relative_accuracy.png")

# ── 7. Bias by horizon — aweagg ──
bias = fe.bias_analysis(data=data, source="mpr", k=12)
fig, ax = bias.plot(
    variable="aweagg", metric="yoy",
    frequency="Q", convert_to_percentage=True,
    return_plot=True,
)
fig.savefig("images/bias.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("✓ bias.png (aweagg)")

# ── 8. Weak efficiency ──
we = fe.weak_efficiency_analysis(data=data, source="mpr", k=12)
print("✓ weak efficiency computed (tabular)")

# ── 9. Blanchard-Leigh (strong efficiency) ──
bl = fe.blanchard_leigh_horizon_analysis(
    data=data, source="mpr",
    outcome_variable="cpisa", outcome_metric="yoy",
    instrument_variable="gdpkp", instrument_metric="yoy",
)
fig, ax = bl.plot(return_plot=True)
fig.savefig("images/blanchard_leigh.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("✓ blanchard_leigh.png")

# ── 10. Rolling bias with fluctuation tests — aweagg, horizons 1 & 4 ──
data_aweagg = data.copy()
data_aweagg.filter(variables=["aweagg"], sources=["mpr"], metrics=["yoy"])
rolling_bias = fe.fluctuation_tests(
    data=data_aweagg,
    window_size=16,
    test_func=fe.bias_analysis,
    test_args={"k": 12},
)
fig, ax = rolling_bias.plot(
    variable="aweagg", horizons=[1, 4], source="mpr",
    convert_to_percentage=True, return_plot=True,
)
fig.savefig("images/rolling_bias.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("✓ rolling_bias.png (aweagg, fluctuation tests, h=1,4)")

# ── 11. Benchmark hedgehog: cpisa AR(p) and random walk ──
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

fe.plot_hedgehog(
    data=data, variable="cpisa",
    forecast_source="baseline ar(p) model", metric="yoy",
    frequency="Q", k=12, convert_to_percentage=True,
    return_plot=True,
)
# Get the figure that plot_hedgehog created and close it; we'll redo on subplots
plt.close()

fig_ar, ax_ar = fe.plot_hedgehog(
    data=data, variable="cpisa",
    forecast_source="baseline ar(p) model", metric="yoy",
    frequency="Q", k=12, convert_to_percentage=True,
    return_plot=True,
)
fig_ar.savefig("images/hedgehog_arp.png", dpi=200, bbox_inches="tight")
plt.close(fig_ar)
print("✓ hedgehog_arp.png")

fig_rw, ax_rw = fe.plot_hedgehog(
    data=data, variable="cpisa",
    forecast_source="baseline random walk model", metric="yoy",
    frequency="Q", k=12, convert_to_percentage=True,
    return_plot=True,
)
fig_rw.savefig("images/hedgehog_rw.png", dpi=200, bbox_inches="tight")
plt.close(fig_rw)
print("✓ hedgehog_rw.png")

print("\nAll plots saved to images/")
