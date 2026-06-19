import logging
import os
import sys
from flask import Flask
app = Flask(__name__)
from db_utils import init_db

logging.basicConfig(level=logging.INFO)

from app import routes
from apscheduler.schedulers.background import BackgroundScheduler


schedule = BackgroundScheduler(daemon=True)
runtime_initialized = False


def start_scheduler():
    def run_weather():
        from pybloom import weather

        weather()

    if getattr(schedule, 'running', False):
        return

    from datetime import datetime, timedelta
    from apscheduler.triggers.interval import IntervalTrigger

    # Run one observation immediately on server startup.
    run_weather()

    # Schedule recurring observations every 10 minutes after the initial run.
    schedule.add_job(
        run_weather,
        trigger=IntervalTrigger(minutes=10, start_date=datetime.now() + timedelta(minutes=10)),
    )
    schedule.start()

def should_start_scheduler() -> bool:
    """Return True when scheduler should start for this process."""
    return os.getenv('PYBLOOM_DISABLE_SCHEDULER') != '1'


def initialize_runtime(*, init_database: bool = True, start_background_jobs: bool = True) -> None:
    """Initialize operational runtime concerns explicitly.

    Keep imports side-effect free by running DB setup and scheduler startup only
    when the caller intentionally asks for it.
    """
    global runtime_initialized
    if runtime_initialized:
        return

    if init_database:
        init_db()

    if start_background_jobs and should_start_scheduler():
        start_scheduler()
    runtime_initialized = True



def should_initialize_runtime_on_import() -> bool:
    """Keep local app runs simple while avoiding startup side effects in pytest."""
    return 'pytest' not in sys.modules


if should_initialize_runtime_on_import():
    initialize_runtime(init_database=True, start_background_jobs=True)
