import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

cars = pd.read_csv("prepared_car_sales.csv")
np.random.seed(0)

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
    print(cars['First_owner'].unique())
    print(cars['Condition'].unique())
# cars.hist()
# plt.show

train_set, test_set = train_test_split(cars, test_size=0.15 , random_state=0)

if 1:
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
df = train_set[['Price', 'Production_year', 'Mileage_km', 'Condition', 'Power_HP', 'CO2_emissions', 'Currency']].copy()
df['Years'] = 2021 - df['Production_year']

fig, axis = plt.subplots(figsize=(10, 6))
if 0:
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
from sklearn.base import BaseEstimator, TransformerMixin
from copy import deepcopy

def currency_conversion(row, rules: dict):
    row['Price'] = row['Price'] * rules[row['Currency']]
    return row

def make_years(row, current_year: int):
    row['Years'] = current_year - row['Production_year']
    return row

train_set.apply(lambda row: currency_conversion(row, {'PLN': 1, 'EUR': 4.26}))
train_set.apply(lambda row: make_years(row, 2022))

num_attributes = ['Years', 'Mileage_km', 'Power_HP', 'CO2_emissions']
cat_attributes = ['Condition']

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