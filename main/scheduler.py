from pathlib import Path
from django.conf import settings
from django.db import transaction
from apscheduler.schedulers.background import BackgroundScheduler
import json
import subprocess
import sys
from main.models import Car
# podmień na swój model z danymi

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
    script_path = Path(settings.BASE_DIR) / "main\\ml\\train_model.py"
    subprocess.run([sys.executable, str(script_path)], check=True)


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