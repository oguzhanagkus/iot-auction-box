from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import database
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exist!", category="error")
        elif len(first_name) < 3 or len(last_name) < 3:
            flash("First name and last name must be longer than 2 characters!", category="error")
        elif len(email) < 5:
            flash("Email must be longer than 5 characters!", category="error")
        elif len(password) < 8:
            flash("Password must be longer than 8 characters!", category="error")
        else:
            new_user = User(first_name=first_name, last_name=last_name, email=email,
                            password=generate_password_hash(password, method="sha256"))
            database.session.add(new_user)
            database.session.commit()
            login_user(new_user, remember=True)
            flash("Account created! You can login!", category="success")
            return redirect(url_for('views.home'))
        return render_template("signup.html", user=current_user)


@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))

            else:
                flash("Invalid credentials!", category="error")
        else:
            flash('Email does not exist!', category='error')
        return render_template("login.html")


@auth.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
