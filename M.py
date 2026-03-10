import numpy as np
import pandas as pd
from main.ml.transformers import ExclusiveCars, YearsExtractor, OutlierFlagTransformer

import sqlite3
import pandas as pd
from contextlib import closing

num_attributes = ['years', 'mileage_km', 'power_hp', 'co2_emissions', 'vehicle_brand']
cat_attributes = ['condition', 'transmission', 'type', 'drive', 'fuel_type']
db_path = 'db.sqlite3'
query = "SELECT production_year, mileage_km, power_hp, co2_emissions, vehicle_brand, " \
"condition, transmission, type, drive, fuel_type, sold_price FROM main_car WHERE sold_price is not NULL"


with closing(sqlite3.connect(db_path)) as conn:
    cars = pd.read_sql_query(query, conn)
    print("reading from db")
np.random.seed(1)

from sklearn.model_selection import train_test_split
train_set_df, test_set_df = train_test_split(cars, test_size=0.01 , random_state=0)
labels = train_set_df['sold_price']
test_labels = test_set_df['sold_price']


####################################
from sklearn.ensemble import RandomForestRegressor, IsolationForest, StackingRegressor
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from lightgbm import LGBMRegressor

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler, FunctionTransformer, OneHotEncoder
from sklearn.compose import TransformedTargetRegressor, ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_percentage_error as mape, root_mean_squared_error as rmse

# class ExclusiveCars(BaseEstimator, TransformerMixin):
#     def __init__(self, brand_col, ex_cars):
#         self.brand_col = brand_col
#         self.ex_cars = ex_cars
#     def fit(self, X, y=None):
#         self._ex_cars_set_ = set(self.ex_cars)
#         return self
#     def transform(self, X):
#         if isinstance(X, pd.DataFrame):
#             X_copy = X.copy()
#             if isinstance(self.brand_col, int):
#                 col_name = X_copy.columns[self.brand_col]
#             else:
#                 col_name = self.brand_col

#             X_copy[col_name] = X_copy[col_name].isin(self._ex_cars_set_).astype(int)
#             return X_copy

#         X_arr = np.asarray(X).copy()
#         X_arr[:, self.brand_col] = np.isin(
#             X_arr[:, self.brand_col],
#             list(self._ex_cars_set_)
#         ).astype(int)
#         return X_arr

# # class CurrencyConverter(BaseEstimator, TransformerMixin):
# #     def __init__(self, rules: dict = None):
# #         self.rules = rules
# #     def fit(self, X, y=None):
# #         return self
# #     def transform(self, X):
# #         X_copy = X.copy()
# #         if 'Price' not in X_copy.columns or 'Currency' not in X_copy.columns:
# #             return X_copy
    
# #         X_copy['Price'] = X_copy['Price'].astype(float)
# #         rates = X_copy['Currency'].map(self.rules)
# #         mask = rates.notna()
# #         X_copy.loc[mask, 'Price'] = X_copy.loc[mask, 'Price'] * rates[mask].astype(float)
        
# #         return X_copy

# class YearsExtractor(BaseEstimator, TransformerMixin):
#     def __init__(self, current_year: int = None, target_col: str = 'Production_year', out_col: str = 'Years'):
#         self.current_year = current_year if current_year is not None else datetime.now().year
#         self.target_col = target_col
#         self.out_col = out_col
#     def fit(self, X, y=None):
#         return self
#     def transform(self, X):
#         X = X.copy()
#         if self.target_col not in X.columns:
#             return X
#         prod = pd.to_numeric(X[self.target_col], errors='coerce')
#         X[self.out_col] = (self.current_year - prod).where(prod.notna(), np.nan).astype(float)
#         return X

# class OutlierFlagTransformer(BaseEstimator, TransformerMixin):
#     def __init__(self, n_estimators=100, max_samples='auto', contamination=0.05, random_state=42):
#         self.n_estimators = n_estimators
#         self.max_samples = max_samples
#         self.contamination = contamination
#         self.random_state = random_state
#         self.iso_ = None
#     def fit(self, X, y=None):
#         self.iso_ = IsolationForest(
#             n_estimators=self.n_estimators,
#             max_samples=self.max_samples,
#             contamination=self.contamination,
#             random_state=self.random_state
#         )
#         self.iso_.fit(X)
#         return self
#     def transform(self, X):
#         flags = self.iso_.predict(X)
#         return flags.reshape(-1, 1)

if __name__ == "__main__":
    num_attributes = ['years', 'mileage_km', 'power_hp', 'co2_emissions', 'vehicle_brand']
    cat_attributes = ['condition', 'transmission', 'type', 'drive', 'fuel_type']
    ex_cars = [
        "Porsche",
        "Ferrari",
        "McLaren",
        "Bentley",
        "Lamborghini",
        "BMW",
        "Mercedes-Benz",
        "Land Rover",
        "Rolls-Royce"
    ]
    rules = {'EUR': 4.26}

    num_pipeline = Pipeline([
        ('exclusive-cars', ExclusiveCars(num_attributes.index('vehicle_brand'), ex_cars)),
        ('imputer', SimpleImputer(strategy='median')),
        ('standard-scaler', StandardScaler()),
    ])

    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('one-hot-encoder', OneHotEncoder(handle_unknown='ignore')),
    ])

    coltrans = ColumnTransformer(transformers=[
        ('nums', num_pipeline, num_attributes),
        ('cats', cat_pipeline, cat_attributes),
    ], 
    remainder='drop',
    n_jobs=1)

    preproc_pipeline = Pipeline([
        #('currency', CurrencyConverter(rules)),
        ('years', YearsExtractor(current_year=2022)),
        ('coltrans', coltrans),
    ], verbose=True)


    #########################################

    best_params = {'n_estimators': 1543, 'max_depth': 19, 'min_samples_split': 4, 'min_samples_leaf': 1, 'max_features': 10, 'bootstrap': True}
    base = RandomForestRegressor(**best_params)
    rf_model = TransformedTargetRegressor(regressor=base, func=np.log1p, inverse_func=np.expm1)

    best_params = {'subsample': 0.6, 'reg_lambda': 0.0, 'reg_alpha': 0.1, 'num_leaves': 15, 'n_estimators': 1200,
                'min_child_samples': 30, 'max_depth': 5, 'learning_rate': 0.05, 'colsample_bytree': 0.9}
    lgbm_model = LGBMRegressor(**best_params)

    # best_params = {'C': 2808, 'kernel': 'rbf', 'gamma': 'scale', 'epsilon': 3}
    # svr_model = SVR(**best_params)


    # svr_x_pipeline = Pipeline([
    #     ('scaler', StandardScaler()), 
    #     ('svr', svr_model)
    # ])

    # svr_wrapped = TransformedTargetRegressor(
    #     regressor=svr_x_pipeline,
    #     transformer=StandardScaler()
    # )

    # svr_pipeline = Pipeline([
    #     ('preproc', preproc_pipeline), 
    #     ('add_outlier_feature', FeatureUnion([
    #         ('original_data', FunctionTransformer(lambda x: x)),
    #         ('outlier_flag', OutlierFlagTransformer(contamination=0.05, random_state=42))
    #     ])),
    #     #('final_scaler', StandardScaler()),
    #     #('svr', svr_wrapped)
    # ])


    stacking_model = StackingRegressor(
        estimators=[
            ('rf', rf_model),
            ('lgbm', lgbm_model),
            #('svr', svr_wrapped)
        ],
        final_estimator=Ridge(alpha=7.114476009343421)
    )

    final_model = Pipeline([
        ('preproc', preproc_pipeline), 
        # ('add_outlier_feature', FeatureUnion([
        #     ('original_data', FunctionTransformer(lambda x: x)),
        #     ('outlier_flag', OutlierFlagTransformer(contamination=0.05, random_state=42))
        # ])),
        ('stacking', stacking_model)
    ])

    final_model.fit(train_set_df, labels)


    #result and saving model
    from joblib import dump
    from datetime import datetime

    print(1 - mape(test_labels, final_model.predict(test_set_df)))

    fname = f"main\\ml\\model\\final_model" #{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
    dump(final_model, fname, compress=3)

    # from sklearn.model_selection import cross_val_predict

    # train_set_df = preproc_pipeline.fit_transform(train_set_df)

    # rf_model.fit(train_set_df, labels)
    # print(1 - mape(labels, rf_model.predict(train_set_df)))

    # lgbm_model.fit(train_set_df, labels)
    # print(1 - mape(labels, lgbm_model.predict(train_set_df)))

    # # 2. Generujemy predykcje OOF (to jest serce Stackingu)
    # # Każdy model "widzi" dany fragment danych tylko gdy nie był na nim trenowany
    # print("Generowanie OOF dla RF...")
    # oof_rf = cross_val_predict(rf_model, train_set_df, labels, cv=3)

    # print("Generowanie OOF dla LGBM...")
    # oof_lgbm = cross_val_predict(lgbm_model, train_set_df, labels, cv=3)


    # # 3. Tworzymy nowy zbiór treningowy dla Ridge
    # # Każdy wiersz to predykcje trzech modeli
    # X_meta_train = np.column_stack((oof_rf, oof_lgbm))
    # from sklearn.linear_model import Ridge

    # meta_model = Ridge(alpha=1.0)
    # meta_model.fit(X_meta_train, labels)

    # # Sprawdź wagi modeli - zobaczysz kto "psuje" wynik!
    # for name, coef in zip(['RF', 'LGBM'], meta_model.coef_):
    #     print(f"Waga modelu {name}: {coef:.4f}")


    # import optuna
    # from sklearn.model_selection import cross_val_score

    # def ridge_objective(trial):
    #     alpha = trial.suggest_float('alpha', 0.01, 10.0, log=True)
    #     model = Ridge(alpha=alpha)
    #     # X_meta_train to tabela z predykcjami OOF Twoich modeli
    #     preds = cross_val_predict(model, X_meta_train, labels, cv=5, n_jobs=-1)
    #     rmse_score = rmse(labels, preds)
    #     mape_score = mape(labels, preds)
    #     trial.set_user_attr("rmse", float(rmse_score))
    #     trial.set_user_attr("mape", float(1 - mape_score))
    #     #return float(rmse_score)
    #     return float(1 - mape_score)
    # study = optuna.create_study(direction='maximize', sampler=optuna.samplers.RandomSampler(seed=42))
    # study.optimize(ridge_objective, n_trials=10)
    # best_params = study.best_params
    # print(f"Best Hyperparameters: {best_params}")
    # best_score = study.best_value
    # print(f"Best Accuracy: {best_score:.3f}")