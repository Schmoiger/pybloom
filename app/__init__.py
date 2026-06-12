import logging

from flask import Flask
app = Flask(__name__)
from db_utils import init_db

init_db()

logging.basicConfig(level=logging.INFO)

from app import routes
from apscheduler.schedulers.background import BackgroundScheduler
from pybloom import weather


schedule = BackgroundScheduler(daemon=True)


@app.before_first_request
def start_scheduler():
    schedule.add_job(lambda: weather(), 'interval', minutes=10)
    schedule.start()
