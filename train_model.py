import numpy as np
import pandas as pd
from main.ml.transformers import ExclusiveCars, YearsExtractor

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
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.linear_model import Ridge
from lightgbm import LGBMRegressor

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import TransformedTargetRegressor, ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_percentage_error as mape, root_mean_squared_error as rmse

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

    stacking_model = StackingRegressor(
        estimators=[
            ('rf', rf_model),
            ('lgbm', lgbm_model),
        ],
        final_estimator=Ridge(alpha=7.114476009343421)
    )

    final_model = Pipeline([
        ('preproc', preproc_pipeline), 
        ('stacking', stacking_model)
    ])

    final_model.fit(train_set_df, labels)


    #result and saving model
    from joblib import dump
    from datetime import datetime
    from pathlib import Path

    print(1 - mape(test_labels, final_model.predict(test_set_df)))

    final_model_path = Path("main\\ml\\model")
    if not final_model_path.exists():
        final_model_path.mkdir(parents=True, exist_ok=True)
    
    fname = f"{final_model_path}\\final_model"
    dump(final_model, fname, compress=3)