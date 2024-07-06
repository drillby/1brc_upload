from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object("config.Config")


@app.route("/")
def index():
    return render_template("index.html")
