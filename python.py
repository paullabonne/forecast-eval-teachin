import forecast_evaluation as fe

forecast_data = fe.ForecastData(
    forecasts_data=your_forecasts, outturns_data=your_outturns
)

forecast_data.run_dashboard()
