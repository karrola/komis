from pathlib import Path
from django.conf import settings
from django.db import transaction
from apscheduler.schedulers.background import BackgroundScheduler
import json
import subprocess
import sys, os
from main.models import Car

scheduler = BackgroundScheduler(timezone="Europe/Warsaw")
started = False

THRESHOLD = getattr(settings, "ML_RETRAIN_THRESHOLD", 500)
CHECK_EVERY_MINUTES = getattr(settings, "ML_CHECK_EVERY_MINUTES", 60)


def get_trained_rows():
    meta_path = Path(settings.BASE_DIR) / "main\\ml\\model\\latest_version.json"
    if not meta_path.exists():
        return 0
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f).get("trained_rows", 0)


def run_training_script():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    script_path = Path(__file__).resolve().parent / "train_model.py"
    print(script_path)
    env = os.environ.copy()

    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{PROJECT_ROOT}{os.pathsep}{existing}"

    subprocess.run(
        [sys.executable, "-m", "main.ml.train_model"],
        cwd=str(PROJECT_ROOT),
        env=env,
        check=True,
    )

    from main.ml.predictor import load_model
    load_model()


def check_and_train():
    current_rows = Car.objects.count()
    trained_rows = int(get_trained_rows())

    if current_rows - trained_rows >= THRESHOLD:
        run_training_script()


def start_scheduler():
    global started
    if started:
        return

    scheduler.add_job(
        check_and_train,
        "interval",
        minutes=CHECK_EVERY_MINUTES,
        id="ml_retrain_job",
        replace_existing=True,
    )
    scheduler.start()
    started = True