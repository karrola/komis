import joblib
import os
from django.conf import settings
import pandas as pd
import numpy as np
from .transformers import ExclusiveCars, YearsExtractor, OutlierFlagTransformer

MODEL_PATH = os.path.join(settings.BASE_DIR, "main/ml/model/final_model")
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Nie udało się wczytać modelu: {e}")


def predict_price(car_data):
    car_data = {k: (np.nan if v is None else v) for k, v in car_data.items()}
    print(car_data)
    data = pd.DataFrame([car_data])
    data = data.replace({None: np.nan})
    print(data)
    prediction = model.predict(data)

    return int(prediction[0])
