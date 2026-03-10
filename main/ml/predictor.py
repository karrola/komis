import joblib
import os
from django.conf import settings
import pandas as pd
import numpy as np
from .transformers import ExclusiveCars, YearsExtractor, OutlierFlagTransformer

MODEL_PATH = os.path.join(settings.BASE_DIR, "main/ml/model/final_model")

model = joblib.load(MODEL_PATH)

def predict_price(car_data):

    # features = [
    #     car_data["condition"],
    #     car_data["vehicle_brand"],
    #     car_data["production_year"],
    #     car_data["mileage_km"],
    #     car_data["power_hp"],
    #     car_data["fuel_type"],
    #     car_data["co2_emissions"],
    #     car_data["drive"],
    #     car_data["transmission"],
    #     car_data["type"],
    # ]
    car_data = {k: (np.nan if v is None else v) for k, v in car_data.items()}
    print(car_data)
    data = pd.DataFrame([car_data])
    data = data.replace({None: np.nan})
    print(data)
    prediction = model.predict(data)

    return int(prediction[0])
