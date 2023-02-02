class Forecasting:
    from statsmodels.tsa.arima.model import ARIMA
    import statsmodels.api as sm
    import pandas as pd
    import numpy as np
    
    # Initialisation
    def __init__(self):
        self.model = {
            "ARIMA": self.ARIMA,
            "SARIMAX": self.sm.tsa.statespace.SARIMAX
        }
        self.model_params = {
            "ARIMA": {"order": (1, 1, 1)},
            "SARIMAX": {"order":(1, 1, 1), "seasonal_order":(1, 1, 1, 12), "enforce_stationarity":False, "enforce_invertibility":False}
        }
        
        self.datas = None
        self.target_c = "countryiso3code"
        self.target_y = "value"
    
    # Load df into the class
    def load_datas(self, datas):
        self.datas = datas
        return self
    
    # Handling models
    def _model_handler(self, m, d):
        return self.model[m](d, **self.model_params[m])
    
    # Handling datas
    def _data_handler(self, c):
        return self.datas[self.datas[self.target_c] == c][self.target_y]
    
    # Forecasting
    def predict(self, model, country, start, end):
        d = self._data_handler(country)
    
        model_fit = self._model_handler(model, d).fit()
        pred = model_fit.get_prediction(start=self.pd.to_datetime(start), end=self.pd.to_datetime(end), dynamic=False)
        return d, pred.predicted_mean, pred.conf_int(0.05)
    