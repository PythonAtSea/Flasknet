from flask import Flask, render_template, flash, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
from flask_mail import Mail


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view="login"
mail=Mail(app)
from models import User, Post
from forms import LoginForm, RegistrationForm, EditForm, EmptyForm, PostForm


# Removed redundant code


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("feed"))

@app.route("/unfollow/<username>", methods=["GET","POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        if unfollow_user(username):
            return redirect(url_for("user", username=username))
        else:
            return redirect(url_for("feed"))
    else:
        return redirect(url_for("feed"))



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html")

@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html")
def unfollow_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("User not found".format(username))
        return False
    if user == current_user:
        flash("You can't unfollow yourself")
        return False
    current_user.unfollow(user)
    db.session.commit()
    flash("You are now not following {}".format(str(user.username)))
    return True



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html")

@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html")
def unfollow_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("User not found".format(username))
        return False
    if user == current_user:
        flash("You can't unfollow yourself")
        return False
    current_user.unfollow(user)
    db.session.commit()
    flash("You are now not following {}".format(str(user.username)))
    return True
@app.route("/feed", methods=["POST","GET"])
@login_required
def feed():
    page = request.args.get("page", 1, type=int)
    form = PostForm()
    if form.validate_on_submit():
        create_post(form)
        return redirect(url_for("feed"))
    posts, next_url, prev_url = get_paginated_posts(page)
    return render_template("feed.html", posts=posts, form=form, next_url=next_url, prev_url=prev_url)
def create_post(form):
    post = Post(body=form.post.data, author=current_user)
    db.session.add(post)
    db.session.commit()
    flash("Your post is now live!")

def get_paginated_posts(page):
    posts = current_user.followed_posts().paginate(page=page, per_page=app.config["POSTS_PER_PAGE"])
    next_url = url_for('feed', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('feed', page=posts.prev_num) if posts.has_prev else None
    return posts.items, next_url, prev_url

@app.route("/explore")
@login_required
def explore():
    page = request.args.get("page", 1, type=int)
    posts=Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config["POSTS_PER_PAGE"])
    next_url = url_for('feed', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('feed', page=posts.prev_num) if posts.has_prev else None
    return render_template("feed.html", posts=posts.items, next_url=next_url, prev_url=prev_url)
@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form=LoginForm()
    if form.validate_on_submit():
        if validate_login(form):
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    return render_template("login.html", form=form, title="Login")
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/signup", methods=["GET","POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        register_user(form)
    return render_template("signup.html", form=form)

@app.route("/user/<username>")
def register_user(form):
    u = User(username=form.username.data, email=form.email.data)
    u.set_password(form.password.data)
    db.session.add(u)
    db.session.commit()
def validate_login(form):
    user = User.query.filter_by(username=form.username.data).first()
    if user is None or not user.check_password(form.password.data):
        flash("Invalid Username or password")
        return False
    login_user(user, remember=form.remember_me.data)
    flash("You have logged in.")
    return True
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/signup", methods=["GET","POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(username=form.username.data, email=form.email.data)
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
    return render_template("signup.html", form=form)

@app.route("/user/<username>")
def user(username):
    form=EmptyForm()
    page = request.args.get("page", 1, type=int)
    user, posts, next_url, prev_url = get_user_posts(username, page)
    return render_template("user.html", user=user, posts=posts, form=form, next_url=next_url, prev_url=prev_url)

@app.route("/edit", methods=["GET","POST"])
# Removed redundant code
    if form.validate_on_submit():
        update_user(form)
        return redirect(url_for("user", username=current_user.username))
    elif request.method == "GET":
        populate_form(form)
    return render_template("edit_account.html", form=form)

@app.route("/follow/<username>", methods=["GET","POST"])
def update_user(form):
    current_user.username = form.username.data
    current_user.about = form.about.data
    db.session.commit()

def populate_form(form):
    form.username.data = current_user.username
    form.about.data = current_user.about
def get_user_posts(username, page):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.post.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config["POSTS_PER_PAGE"])
    next_url = url_for('user', username=username,page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=username, page=posts.prev_num) if posts.has_prev else None
    return user, posts.items, next_url, prev_url
def edit():
    form = EditForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about = form.about.data
        db.session.commit()
        return redirect(url_for("user", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about.data = current_user.about
    return render_template("edit_account.html", form=form)

@app.route("/follow/<username>", methods=["GET","POST"])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        if follow_user(username):
            return redirect(url_for("user", username=username))
        else:
            return redirect(url_for("feed"))
    else:
        return redirect(url_for("feed"))
def follow_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("User not found".format(username))
        return False
    if user == current_user:
        flash("You can't follow yourself")
        return False
    current_user.follow(user)
    db.session.commit()
    flash("You are now following {}".format(str(user.username)))
    return True

@app.route("/unfollow/<username>", methods=["GET","POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash("User not found".format(username))
            return redirect(url_for("feed"))
        if user == current_user:
            flash("You can't unfollow yourself")
            return redirect(url_for("feed"))
        current_user.unfollow(user)
        db.session.commit()
        flash("You are now not following {}".format(str(user.username)))
        return redirect(url_for("user", username=username))
    else:
    return render_template("feed.html", posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)

@app.route("/explore")
@login_required
def explore():
    page = request.args.get("page", 1, type=int)
    posts, next_url, prev_url = get_explore_posts(page)
    return render_template("feed.html", posts=posts, next_url=next_url, prev_url=prev_url)
@app.route("/login", methods=["GET","POST"])
def get_explore_posts(page):
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config["POSTS_PER_PAGE"])
    next_url = url_for('feed', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('feed', page=posts.prev_num) if posts.has_prev else None
    return posts.items, next_url, prev_url
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html")

@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html")
