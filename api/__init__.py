import os

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .models.database import db

app = Flask(__name__)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "50 per hour"],
)

deploy = os.getenv("FLASK_ENV", "development")

app.config.from_object("config.Config")
if deploy == "development":
    app.config.from_object("devconf.DevelopmentConfig")
else:
    app.config.from_object("config.ProductionConfig")

db.init_app(app)
with app.app_context():
    db.create_all()

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

from api.views import cesty
