import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

cars = pd.read_csv("prepared_car_sales.csv")
np.random.seed(1)

from sklearn.model_selection import train_test_split

"""['Index', 'Price', 'Currency', 'Condition', 'Vehicle_brand',
       'Vehicle_model', 'Vehicle_version', 'Vehicle_generation',
       'Production_year', 'Mileage_km', 'Power_HP', 'Displacement_cm3',
       'Fuel_type', 'CO2_emissions', 'Drive', 'Transmission', 'Type',
       'Doors_number', 'Colour', 'Origin_country', 'First_owner',
       'First_registration_date', 'Offer_publication_date', 'Offer_location',
       'Features']"""

# 'Currency', 
# TO DROP: Displacement_cm3, Origin_country, First_registration_date, Offer_publication_date, Offer_location, Features
"""['Price', 'Production_year', 'Mileage_km', ]"""
# TYPES: ['SUV' 'compact' 'minivan' 'city_cars' 'station_wagon' 'sedan' 'small_cars' 'coupe' 'convertible']

if 0:
    print(cars.info())
    print(cars.describe())
    print(cars.shape)
    print(cars.columns)
    exit()
    print(cars['First_owner'].unique())
    print(cars['Condition'].unique())
    # cars.hist()
    # plt.show

train_set, test_set = train_test_split(cars, test_size=0.15 , random_state=0)
labels = train_set['Price']

if 0:
    df = train_set[['Price', 'Production_year', 'Mileage_km', 'Condition', 'Power_HP', 'CO2_emissions', 'Currency']].copy()
    for i, row in df.iterrows():
        if row['Currency'] == 'EUR':
            df.at[i, 'Price'] = row['Price'] * 4.26
    df = df.drop(columns='Currency')
    df['Condition'] = df['Condition'].map({'Used': 0, 'New': 1})
    corr_mtx = df.corr()
    print(corr_mtx['Price'].sort_values(ascending=False))

if 0:
    dummies = pd.get_dummies(train_set['Vehicle_brand'], dummy_na=False) #, prefix='brand'
    corrs = dummies.apply(lambda col: col.corr(train_set['Price']))
    corrs.sort_values(ascending=False)
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(corrs)
    # train_set.plot(kind='scatter', x='Mileage_km', y='Price', alpha=0.5)
    # plt.show()

if 0:
    fig, axis = plt.subplots(figsize=(10, 6))
    df = train_set[['Price', 'Production_year', 'Mileage_km', 'Condition', 'Power_HP', 'CO2_emissions', 'Currency']].copy()
    df['Years'] = 2021 - df['Production_year']
    avg_prices = df.groupby('Years')['Price'].mean()
    median_prices = df.groupby('Years')['Price'].median()
    axis.scatter(df['Years'], df['Price'], alpha=0.5)
    axis.scatter(median_prices.index, median_prices, c='green', alpha=1)
    axis.scatter(avg_prices.index, avg_prices, c='red', alpha=0.7)
    tmp = pd.concat([avg_prices, median_prices], axis=1)
    print(tmp)
    plt.show()

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

num_attributes = ['Years', 'Mileage_km', 'Power_HP', 'CO2_emissions']
cat_attributes = ['Condition']

def currency_conversion(row, rules: dict):
    if row['Currency'] in rules:
        row['Price'] = row['Price'] * rules[row['Currency']]
    return row

#Axis 0 will act on all the ROWS in each COLUMN
#Axis 1 will act on all the COLUMNS in each ROW
train_set.apply(lambda row: currency_conversion(row, {'EUR': 4.26}), axis=1)
train_set['Years'] = 2022 - train_set['Production_year']

num_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
])

cat_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('one-hot-encoder', OneHotEncoder()),
])

final_pipeline = ColumnTransformer(transformers= [
    ('nums', num_pipeline, num_attributes),
    ('cats', cat_pipeline, cat_attributes),
],
remainder='drop',
n_jobs=-1,
)

train_set = final_pipeline.fit_transform(train_set)

if 0:
    from sklearn.model_selection import GridSearchCV
    from sklearn.ensemble import RandomForestRegressor

    param_grid = [
        {'n_estimators': [15, 20, 30], 'max_features': [3, 4, 5, 6], 'bootstrap': [True]},
    ]
    forest_reg = RandomForestRegressor()

    grid_search = GridSearchCV(forest_reg, param_grid, cv=10,
                            scoring='neg_mean_squared_error',
                            return_train_score=True)
    
    print("rozpoczynam naukę\n")
    grid_search.fit(train_set, labels)
    print(grid_search.best_params_)
    print(grid_search.best_estimator_)


from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor

params = {'bootstrap': [True, False],
          'max_depth': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, None],
          'max_features': [2, 3, 4, 5, 6, None],
          'min_samples_leaf': [1, 2, 4],
          'min_samples_split': [2, 5, 10],
          'n_estimators': [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]}
forest_reg = RandomForestRegressor()

random_search = RandomizedSearchCV(estimator=forest_reg, param_distributions=params,
                                   n_iter=10, cv=5, random_state=42, n_jobs=-1, verbose=3)

print("rozpoczynam naukę\n")
random_search.fit(train_set, labels)
print(random_search.best_params_)
print(random_search.best_estimator_)

def evaluate(model, test_features, test_labels):
    predictions = model.predict(test_features)
    errors = abs(predictions - test_labels)
    mape = 100 * np.mean(errors / test_labels)
    accuracy = 100 - mape
    print('Model Performance')
    print('Average Error: {:0.4f} degrees.'.format(np.mean(errors)))
    print('Accuracy = {:0.2f}%.'.format(accuracy))
    return accuracy

test_set.apply(lambda row: currency_conversion(row, {'EUR': 4.26}), axis=1)
test_set['Years'] = 2022 - test_set['Production_year']
test_labels = test_set['Price']
test_set = final_pipeline.fit_transform(test_set)
best_random = random_search.best_estimator_

random_accuracy = evaluate(best_random, test_set, test_labels)

from sklearn.metrics import mean_squared_error
final_mse = mean_squared_error(test_labels, best_random.predict(test_set))
final_rmse = np.sqrt(final_mse)
print('final_rmse: ', final_rmse)

# cvres = grid_search.cv_results_
# for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
#     print(np.sqrt(-mean_score), params)

# from sklearn.model_selection import cross_val_score
# scores = cross_val_score(model, train_set, labels, scoring='neg_mean_squared_error', cv=10)
# print("Rmse_scores = ", np.sqrt(-scores))
# print("Wyniki: ", scores)
# print("Średnia: ", scores.mean())
# print("Odchylenie standardowe: ", scores.std())