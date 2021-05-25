import os
from flask import Flask, render_template, request, redirect, url_for, make_response
from sqla_wrapper import SQLAlchemy
from hashlib import sha256
import uuid

db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite").replace("postgres://", "postgresql://", 1)
db = SQLAlchemy(db_url)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    first_name = db.Column(db.String, unique=False)
    last_name = db.Column(db.String, unique=False)
    country = db.Column(db.String, unique=False)
    postal_code = db.Column(db.Integer, unique=False)
    email = db.Column(db.String, unique=True)
    phone_number = db.Column(db.Integer, unique=True)
    password = db.Column(db.String, unique=False)
    session_token = db.Column(db.String, unique=False)


class CarAd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    brand = db.Column(db.String, unique=False)
    date = db.Column(db.String, unique=False)
    kilometers = db.Column(db.Integer, unique=False)
    horsepower = db.Column(db.Integer, unique=False)
    transmission = db.Column(db.String, unique=False)
    email = db.Column(db.String, unique=True)
    telephone = db.Column(db.Integer, unique=True)
    color = db.Column(db.String, unique=False)
    price = db.Column(db.Integer, unique=False)


app = Flask(__name__)

db.create_all()


# in alphabetical order

@app.route("/about")
def about():
    session_cookie = request.cookies.get("session")
    if session_cookie:
        user = db.query(User).filter_by(session_token=session_cookie).first()
        if user:
            return render_template("about.html", user=user)
    return render_template("about.html")


@app.route("/contact")
def contact():
    session_cookie = request.cookies.get("session")
    if session_cookie:
        user = db.query(User).filter_by(session_token=session_cookie).first()
        if user:
            return render_template("contact.html", user=user)
    return render_template("contact.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    session_cookie = request.cookies.get("session")
    if session_cookie:
        user = db.query(User).filter_by(session_token=session_cookie).first()
        if user:
            return render_template("dashboard.html", user=user)

    return "ERROR: You are not logged in! Please logg in to see contents of this page!"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    # get username and password
    elif request.method == "POST":
        username = request.form.get("username")

        password = request.form.get("password")
        # check for password hash
        password_hash = sha256(password.encode("utf-8")).hexdigest()
        # check if username exists
        existing_user = db.query(User).filter_by(username=username, password=password_hash).first()
        # if it does exists than give him session token and set cookie
        if existing_user:
            session_token = str(uuid.uuid4())
            existing_user.session_token = session_token
            existing_user.save()

            response = make_response(redirect(url_for("dashboard")))
            response.set_cookie("session", session_token)
            return response
        else:
            return "ERROR: Password or username is not correct!"
    return redirect(url_for("dashboard"))


@app.route("/logout", methods=["POST"])
def logout():
    session_cookie = request.cookies.get("session")
    user = db.query(User).filter_by(session_token=session_cookie).first()
    user.session_token = ""
    user.save()

    return redirect(url_for("login"))


@app.route("/dashboard/post-car", methods=["GET", "POST"])
def post_car():
    if request.method == "GET":
        return render_template("post-car.html")
    elif request.method == "POST":
        # mors dobit vse podatke vn
        username = request.form.get("username")
        brand = request.form.get("brand")
        date = request.form.get("date")
        kilometers = request.form.get("kilometers")
        horsepower = request.form.get("horsepower")
        transmission = request.form.get("transmission")
        email = request.form.get("email")
        telephone = request.form.get("telephone")
        color = request.form.get("color")
        price = request.form.get("price")

        session_cookie = request.cookies.get("session")
        if session_cookie:
            user = db.query(User).filter_by(session_token=session_cookie).first()
            username = db.query(User).filter_by(username=username).first()
            if user == username:
                new_add = CarAd(brand=brand, date=date, kilometers=kilometers, horsepower=horsepower,
                                transmission=transmission, email=email, telephone=telephone,
                                color=color, price=price)
                new_add.save()
            print("car brand {}".format(brand))
            print("car date {}".format(date))
            print("car km {}".format(kilometers))
            print("car horsepower {}".format(horsepower))
            print("car transmission {}".format(transmission))
            print("car email {}".format(email))
            print("car telephone {}".format(telephone))
            print("car color {}".format(color))
            print("car price {}".format(price))

            return "Your post was successful"
        else:
            return "Something went wrong"


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "GET":
        return render_template("registration.html")
    elif request.method == "POST":
        # dobi vse podatke iz baze
        username = request.form.get("username")
        first_name = request.form.get("first-name")
        last_name = request.form.get("last-name")
        country = request.form.get("country")
        postal_code = request.form.get("postal-code")
        email = request.form.get("user-email")
        phone_number = request.form.get("telephone")
        password = request.form.get("password")
        repeat = request.form.get("repeat")
        # ce user ne obstaja naredimo novega. check in base
        existing_user = db.query(User).filter_by(username=username).first()

        if existing_user:
            return "ERROR: This username already exist! You need to choose something else."
        else:
            # check if password == repeat
            if password == repeat:
                # camouflage password
                password_hash = sha256(password.encode("utf-8")).hexdigest()
                new_user = User(username=username, first_name=first_name, last_name=last_name,
                                country=country, postal_code=postal_code, email=email,
                                phone_number=phone_number, password=password_hash)
                print("password hash {}".format(password_hash))
                new_user.save()
                return "Your registration was successful."
            else:
                return "ERROR: Passwords do not match!"

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(use_reloader=True)
