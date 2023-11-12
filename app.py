# Importing necessary modules and libraries
from flask import Flask, render_template, flash, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
from flask_mail import Mail

# Setting up the Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Setting up the database using SQLAlchemy and Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Setting up the login manager
login = LoginManager(app)
login.login_view="login"

# Setting up the mail server
mail=Mail(app)

# Importing the models and forms used in the application
from models import User, Post
from forms import LoginForm, RegistrationForm, EditForm, EmptyForm, PostForm


# Removed redundant code


# Route for the home page
@app.route("/")
def index():
    # If the user is authenticated, redirect to the feed page
    if current_user.is_authenticated:
        return redirect(url_for("feed"))

# Route for unfollowing a user
@app.route("/unfollow/<username>", methods=["GET","POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        # If the unfollow is successful, redirect to the user's page
        if unfollow_user(username):
            return redirect(url_for("user", username=username))
        else:
            # If the unfollow is not successful, redirect to the feed page
            return redirect(url_for("feed"))
    else:
        # If the form is not submitted, redirect to the feed page
        return redirect(url_for("feed"))

# Before each request, update the last seen time of the current user
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Error handler for 404 errors
@app.errorhandler(404)
# Render a 404 error page when a 404 error occurs
def not_found_error(error):
    return render_template("404.html")

# Render a 500 error page when a 500 error occurs
@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html")

# Function to unfollow a user
def unfollow_user(username):
    # Query the user to be unfollowed
    user = User.query.filter_by(username=username).first()
    # If the user does not exist, flash an error message and return False
    if user is None:
        flash("User not found".format(username))
        return False
    # If the user to be unfollowed is the current user, flash an error message and return False
    if user == current_user:
        flash("You can't unfollow yourself")
        return False
    # Unfollow the user and commit the changes to the database
    current_user.unfollow(user)
    db.session.commit()
    # Flash a success message and return True
    flash("You are now not following {}".format(str(user.username)))
    return True

# Before each request, update the last seen time of the current user
@app.before_request
# Before each request, update the last seen time of the current user
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Render a 404 error page when a 404 error occurs
@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html")

# Render a 500 error page when a 500 error occurs
@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html")

# Function to unfollow a user
def unfollow_user(username):
    # Query the user to be unfollowed
    user = User.query.filter_by(username=username).first()
    # If the user does not exist, flash an error message and return False
    if user is None:
        flash("User not found".format(username))
        return False
    # If the user to be unfollowed is the current user, flash an error message and return False
    if user == current_user:
        flash("You can't unfollow yourself")
        return False
    # Unfollow the user and commit the changes to the database
    current_user.unfollow(user)
    db.session.commit()
    # Flash a success message and return True
    flash("You are now not following {}".format(str(user.username)))
    return True
# Route for the feed page
@app.route("/feed", methods=["POST","GET"])
@login_required
def feed():
    # Get the page number from the request arguments
    page = request.args.get("page", 1, type=int)
    # Create a new post form
    form = PostForm()
    # If the form is submitted and valid, create a new post
    if form.validate_on_submit():
        create_post(form)
        # Redirect to the feed page
        return redirect(url_for("feed"))
    # Get the paginated posts
    posts, next_url, prev_url = get_paginated_posts(page)
    # Render the feed page
    return render_template("feed.html", posts=posts, form=form, next_url=next_url, prev_url=prev_url)

# Function to create a new post
def create_post(form):
    # Create a new post with the form data and the current user as the author
    post = Post(body=form.post.data, author=current_user)
    # Add the post to the database
    db.session.add(post)
    # Commit the changes to the database
    db.session.commit()
    # Flash a success message
    flash("Your post is now live!")

# Function to get paginated posts
def get_paginated_posts(page):
    # Get the posts followed by the current user and paginate them
    posts = current_user.followed_posts().paginate(page=page, per_page=app.config["POSTS_PER_PAGE"])
    # Get the URLs for the next and previous pages
    next_url = url_for('feed', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('feed', page=posts.prev_num) if posts.has_prev else None
    # Return the posts and the next and previous URLs
    return posts.items, next_url, prev_url

# Route for the explore page
@app.route("/explore")
@login_required
def explore():
    # Get the page number from the request arguments
    page = request.args.get("page", 1, type=int)
    # Get all posts ordered by timestamp and paginate them
    posts=Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config["POSTS_PER_PAGE"])
    # Get the URLs for the next and previous pages
    next_url = url_for('feed', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('feed', page=posts.prev_num) if posts.has_prev else None
    # Render the feed page with the posts
    return render_template("feed.html", posts=posts.items, next_url=next_url, prev_url=prev_url)
# Route for the login page
@app.route("/login", methods=["GET","POST"])
def login():
    # If the user is already authenticated, redirect to the index page
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    # Create a new login form
    form=LoginForm()
    # If the form is submitted and valid, validate the login
    if form.validate_on_submit():
        if validate_login(form):
            # If the login is valid, redirect to the index page
            return redirect(url_for("index"))
        else:
            # If the login is not valid, redirect to the login page
            return redirect(url_for("login"))
    # Render the login page
    return render_template("login.html", form=form, title="Login")

# Route for the logout page
@app.route("/logout")
def logout():
    # Logout the current user
    logout_user()
    # Redirect to the index page
    return redirect(url_for("index"))

# Route for the signup page
@app.route("/signup", methods=["GET","POST"])
def signup():
    # If the user is already authenticated, redirect to the index page
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    # Create a new registration form
    form = RegistrationForm()
    # If the form is submitted and valid, register the user
    if form.validate_on_submit():
        register_user(form)
    # Render the signup page
    return render_template("signup.html", form=form)

# Route for the user profile page
@app.route("/user/<username>")
# Function to register a new user
def register_user(form):
    # Create a new user with the form data
    u = User(username=form.username.data, email=form.email.data)
    # Set the password for the user
    u.set_password(form.password.data)
    # Add the user to the database
    db.session.add(u)
    # Commit the changes to the database
    db.session.commit()
# Function to validate a login
def validate_login(form):
    # Query the user by username
    user = User.query.filter_by(username=form.username.data).first()
    # If the user does not exist or the password is incorrect, flash an error message and return False
    if user is None or not user.check_password(form.password.data):
        flash("Invalid Username or password")
        return False
    # Login the user and remember them
    login_user(user, remember=form.remember_me.data)
    # Flash a success message
    flash("You have logged in.")
    return True
# Function to logout a user
def logout():
    # Logout the current user
    logout_user()
    # Redirect to the index page
    return redirect(url_for("index"))

# Route for the signup page
@app.route("/signup", methods=["GET","POST"])
def signup():
    # If the user is already authenticated, redirect to the index page
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    # Create a new registration form
    form = RegistrationForm()
    # If the form is submitted and valid, register the user
    if form.validate_on_submit():
        # Create a new user with the form data
        u = User(username=form.username.data, email=form.email.data)
        # Set the password for the user
        u.set_password(form.password.data)
        # Add the user to the database
        db.session.add(u)
        # Commit the changes to the database
        db.session.commit()
    # Render the signup page
    return render_template("signup.html", form=form)

# Route for the user profile page
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
