import os

from flask import render_template

from api import app


@app.route("/")
async def index():
    return await render_template("index.html")
