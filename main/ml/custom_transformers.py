from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_percentage_error as mape, root_mean_squared_error as rmse
import pandas as pd
import numpy as np
class ExclusiveCars(BaseEstimator, TransformerMixin):
    def __init__(self, brand_col, ex_cars):
        self.brand_col = brand_col
        self.ex_cars = ex_cars
    def fit(self, X, y=None):
        self._ex_cars_set_ = set(self.ex_cars)
        return self
    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            X_copy = X.copy()
            if isinstance(self.brand_col, int):
                col_name = X_copy.columns[self.brand_col]
            else:
                col_name = self.brand_col

            X_copy[col_name] = X_copy[col_name].isin(self._ex_cars_set_).astype(int)
            return X_copy

        X_arr = np.asarray(X).copy()
        X_arr[:, self.brand_col] = np.isin(
            X_arr[:, self.brand_col],
            list(self._ex_cars_set_)
        ).astype(int)
        return X_arr

class YearsExtractor(BaseEstimator, TransformerMixin):
    def __init__(self, current_year: int = None, target_col: str = 'production_year', out_col: str = 'years'):
        self.current_year = current_year if current_year is not None else datetime.now().year
        self.target_col = target_col
        self.out_col = out_col
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        X = X.copy()
        if self.target_col not in X.columns:
            return X
        prod = pd.to_numeric(X[self.target_col], errors='coerce')
        X[self.out_col] = (self.current_year - prod).where(prod.notna(), np.nan).astype(float)
        return X

class OutlierFlagTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, n_estimators=100, max_samples='auto', contamination=0.05, random_state=42):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.contamination = contamination
        self.random_state = random_state
        self.iso_ = None
    def fit(self, X, y=None):
        self.iso_ = IsolationForest(
            n_estimators=self.n_estimators,
            max_samples=self.max_samples,
            contamination=self.contamination,
            random_state=self.random_state
        )
        self.iso_.fit(X)
        return self
    def transform(self, X):
        flags = self.iso_.predict(X)
        return flags.reshape(-1, 1)