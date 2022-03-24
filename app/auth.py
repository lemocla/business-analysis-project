import os
import uuid
if os.path.exists("env.py"):
    import env
    
from flask_login import LoginManager
from app import login_manager


from flask import Blueprint, session, render_template, flash, redirect, \
                  url_for, session, request, jsonify
from flask_login import login_user, logout_user, UserMixin
# from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash

from app.forms import LoginForm, RegisterForm

from werkzeug.security import generate_password_hash, check_password_hash

from app import mongo
from app.forms import LoginForm, RegisterForm, ResetPasswordForm

# Blueprint
auth = Blueprint("auth", __name__, template_folder='templates')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

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
    if request.method == "POST":
        # check if username already exists in db
        current_user = mongo.db.u.find_one(
            {"username": request.form.get("username").lower()})

        if current_user:
            flash("Username already exists")
            return redirect(url_for("auth.register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.u.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for('home.view_home'))
    return render_template("auth/register.html", form = RegisterForm(request.form))

# A route to render the login page and authenticate u
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        login_user(User(request.form.get("username")))
        
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
        mongo.db.u.update_one(
            {"username": form.username.data.lower()},
            {"$set": {"password": generate_password_hash(form.password.data)}}
        )
        flash("Password Updated")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)
