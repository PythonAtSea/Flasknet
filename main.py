from flask import Flask, render_template, flash, redirect, url_for
from config import Config
from forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view="login"
posts=[
    {"authorname": "Fred", "body" :"Hi buds"},
    {"authorname": "Sally", "body" :"why"},
]
from models import User, Post


@app.route("/index")
@app.route("/")
@login_required
def index():
    return render_template("index.html", posts=posts)
@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid Username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        flash("You have logged in.")
        return redirect("/index")
    return render_template("login.html", form=form, title="Login", nonav=True)
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))
