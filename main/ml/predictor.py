import joblib
import os
from django.conf import settings
import pandas as pd
import numpy as np
import json
from pathlib import Path
import subprocess
import sys
from main.ml.custom_transformers import ExclusiveCars, YearsExtractor, OutlierFlagTransformer #do not delete!

BASE_MODEL_PATH = Path(settings.BASE_DIR) / "main/ml/model"
latest_version = BASE_MODEL_PATH / "latest_version.json"

if not latest_version.exists():
    script_path = Path(__file__).resolve().parent / "train_model.py"
    print(script_path)
    subprocess.run([sys.executable, str(script_path)], check=True)

with open(latest_version, "r", encoding="utf-8") as f:
    tmp = json.load(f)
    
model_path = tmp.get("model_path")
model = None

if os.path.exists(model_path):
    try:
        model = joblib.load(model_path)
    except Exception as e:
        print(f"Unable to load model: {e}")
        print(model_path)


def predict_price(car_data):
    car_data = {k: (np.nan if v is None else v) for k, v in car_data.items()}
    print(car_data)
    data = pd.DataFrame([car_data])
    data = data.replace({None: np.nan})
    print(data)
    prediction = model.predict(data)

    return int(prediction[0])
