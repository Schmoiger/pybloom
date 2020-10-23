from flask import Flask
app = Flask(__name__)
from app import routes
from apscheduler.schedulers.background import BackgroundScheduler
from pybloom import weather


schedule = BackgroundScheduler(daemon=True)
schedule.add_job(lambda: weather(), 'interval', minutes=10)
schedule.start()
