import os

from flask import Flask
from .models.user import db

app = Flask(__name__)

deploy = os.getenv("FLASK_ENV", "development")

app.config.from_object("config.Config")
if deploy == "development":
    app.config.from_object("devconf.DevelopmentConfig")
else:
    app.config.from_object("config.ProductionConfig")

db.init_app(app)
with app.app_context():
    db.create_all()

from api.views import cesty
