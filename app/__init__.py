import logging
from flask import Flask
app = Flask(__name__)
from db_utils import init_db

init_db()

logging.basicConfig(level=logging.INFO)

from app import routes
from apscheduler.schedulers.background import BackgroundScheduler


schedule = BackgroundScheduler(daemon=True)


def start_scheduler():
    def run_weather():
        from pybloom import weather

        weather()

    if getattr(schedule, 'running', False):
        return

    from datetime import datetime
    from apscheduler.triggers.interval import IntervalTrigger

    schedule.add_job(run_weather, trigger=IntervalTrigger(minutes=10, start_date=datetime.now()))
    schedule.start()


start_scheduler()
