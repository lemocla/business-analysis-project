import os
from app import login_manager
from flask import Flask, Blueprint, render_template, flash, redirect, \
                  url_for, session, request
from flask_login import current_user, login_user, logout_user, login_required, UserMixin
# from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash

from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from app.forms import LoginForm, RegisterForm

from werkzeug.security import generate_password_hash, check_password_hash
import certifi

from app import mongo
from app.forms import LoginForm, RegisterForm, ResetPasswordForm
from app.config import Config

# Blueprint
auth = Blueprint("auth", __name__, template_folder='templates')

mongo = PyMongo(tlsCAFile=certifi.where())
login_manager.login_view = 'login'
db = mongo.db

# Import User Loader to load user from databases
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

class User(UserMixin):
    
    def register(self):
        print(request.form)
        
        # Create the user object
        user = {
			"_id": uuid.uuid4().hex,
			"username": request.form.get("username"),
   			"email": request.form.get("email"),
      		"password": request.form.get("password")
		}
        
        # Encrypt the password
        user['password'] = pbkdf2_sha256.encrypt(user['password'])
        
        return jsonify(user), 200
    
    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

    @login_manager.user_loader
    def load_user(username):
        u = mongo.db.Users.find_one({"Name": username})
        if not u:
            return None
        return User(username=u['username'])


# A route to render the register page and add users to database
@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        # check if username already exists in db
        current_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if current_user:
            flash("Username already exists")
            return redirect(url_for("auth.register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for('home.view_home'))
    return render_template("auth/register.html", form = RegisterForm(request.form))


# A route to render the login page and authenticate users
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.view_home'))

    form = LoginForm()
    if request.method == "POST":
        # Check if username already exists in db
        user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
  
        if user and User.check_password(user['password'], form.password.data):
            # make sure the password is correct
            if check_password_hash(
                user["password"], request.form.get("password")):
                user_obj = User(username=user['username'])
                loggedin = login_user(user_obj)
                # session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for('home.view_home'))
            else:
                # If password is invalid
                flash("Invalid Username and/or Password")
                return redirect(url_for("auth.login"))               
        else:
            # If username doesn't exist
            flash("Invalid Username and/or Password")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html", form=form)


#A route to render logout template and remove user from session cookie  
@auth.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        logout_user()
        return redirect(url_for('home.view_home'))
    return render_template("auth/logout.html")


# A route to render the password reset page and reset users password
@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    form = ResetPasswordForm()
    if request.method == "POST":
        mongo.db.users.update_one(
            {"username": form.username.data.lower()},
            {"$set": {"password": generate_password_hash(form.password.data)}}
        )
        flash("Password Updated")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)
