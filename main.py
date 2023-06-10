from flask import Flask, render_template, flash, redirect
from config import Config
from forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

posts=[
    {"authorname": "Fred", "body" :"Hi buds"},
    {"authorname": "Sally", "body" :"why"},
]
import models
@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html", posts=posts)
@app.route("/login", methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        flash("Login requested for user {}, remember_me={}".format(form.username.data, form.remember_me.data))
        return redirect("/index")
    return render_template("login.html", form=form, title="Login", nonav=True)
