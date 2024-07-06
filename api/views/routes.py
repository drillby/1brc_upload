import os

from flask import render_template

from api import app


@app.route("/")
def index():
    return "Hello, World!"
    # return render_template("index.html")
