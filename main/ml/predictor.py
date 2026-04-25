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

model = None

def load_model():
    latest_version = Path(settings.BASE_DIR) / "main/ml/model" / "latest_version.json"
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")

    if not latest_version.exists():
        script_path = Path(__file__).resolve().parent / "train_model.py"
        print(script_path)
        env = os.environ.copy()

        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{PROJECT_ROOT}{os.pathsep}{existing}"

        subprocess.run(
            [sys.executable, "-m", "main.ml.train_model"],  # -m zamiast ścieżki do pliku!
            cwd=str(PROJECT_ROOT),
            env=env,
            check=True,
        )

    with open(latest_version, "r", encoding="utf-8") as f:
        tmp = json.load(f)
    
    global model
    model_path = tmp.get("model_path")

    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
        except Exception as e:
            print(f"Unable to load model: {e}")
            print(model_path)
    print("model has been loaded")


def predict_price(car_data):
    global model
    car_data = {k: (np.nan if v is None else v) for k, v in car_data.items()}
    print(car_data)
    data = pd.DataFrame([car_data])
    data = data.replace({None: np.nan})
    print(data)
    prediction = model.predict(data)

    return int(prediction[0])
