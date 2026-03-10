import pandas as pd

data = pd.read_csv("prepared_car_sales.csv")

print(data.loc[691])


def currency_conversion(row, rules: dict):
    if row['Currency'] in rules:
        row['Price'] = int(row['Price'] * rules[row['Currency']])
    return row

#Axis 0 will act on all the ROWS in each COLUMN
#Axis 1 will act on all the COLUMNS in each ROW
data = data.apply(lambda row: currency_conversion(row, {'EUR' : 4.28}), axis=1)


print("############### PO ZMIANACH ################")

print(data.loc[691])

data.to_csv("car_sales.csv", index=False)