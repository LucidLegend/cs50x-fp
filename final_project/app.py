import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///deliv.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

current_time = datetime.datetime.now()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """assign driver to group of addresses with associated order number"""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username").upper())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/stores")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if not request.method == "POST":
        return render_template("register.html")

    #  Ensure username was submitted
    if not request.form.get("username"):
        return apology("must provide username", 400)

    # Ensure password was submit
    elif not request.form.get("password"):
        return apology("must provide password", 400)

    # Ensure confirmation password was submit
    elif not request.form.get("confirmation"):
        return apology("must confirm password", 400)

    # Ensure username doesnt already exist in DB
    if db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username").upper()):
        return apology("username already exists", 400)

    # Ensure password and confirmation password match
    if request.form.get("confirmation") == request.form.get("password"):

        # Insert new row into users table containing the filled forms data
        db.execute("INSERT INTO users (id, username, hash) VALUES (?, ?, ?)", id(request.form.get("username")), request.form.get(
            "username").upper(), generate_password_hash(request.form.get("password")))

    else:
        return apology("passwords do not match")

    # Redirect user to login page
    return redirect("/login")


@app.route("/stores", methods=["GET", "POST"])
def stores():
    """change current store_id"""

    # Create a "stores" variable to hold any store_id associated to user
    stores = db.execute("SELECT UNIQUE store_id FROM stores st JOIN users usr ON st.store_id = usr.store_id WHERE user_id = ?", session["user_id"])

    # Ensure "stores" variable is not empty
    if len(stores) <= 0:
        return redirect("/select_your_store")

    if request.method == "POST":
        return render_template("stores.html", stores=stores)

    # Set selected store_id as session variable
    if not request.method == "POST":
    session["current_store_id"] = request.form.get("store_id")


@app.route("/select_your_stores", methods=["GET", "POST"])
def select_your_store():
    """select the store/s to which the user is employed"""

    # Create a "stores" variable to hold all available store_id for the user to select from
    stores = db.execute("SELECT UNIQUE store_id FROM stores")
    if request.method == "GET":
        return render_template("select_your_store.html", stores=stores)

    if not request.form.get("store_id"):
        return apology("Please select a store number", 400)
    
    # Update users table with new store_id
    db.execute("INSERT INTO users (store_id) VALUE (?) WHERE user_id = ?", session["store_id"], session["user_id"])

    # If admin box checked prompt for passcode
    if request.form.get("admin") == True:
        return redirect("/admin")

    return redirect("/stores")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """verify admin privileges via store password and updates user table with admin credentials"""
    
if request.method == "POST":
    return render_template("admin.html")

# Store the store admin password to check agains users typed passcode
password = db.execute("SELECT admin_password FROM stores WHERE store_id = ?")

if request.form.get("password") != password:
    return apology("passwords does not match", 400)

# If typed password matches store_password 
if request.form.get("password") == password

    # Update admin row on users table to give user admin priveleges
    db.execute("UPDATE users (admin) VALUE(True) WHERE user_id = ?", session["user_id"])

    return redirect("/employee")

    

@app.route("/employee", methods=["GET", "POST"])
def employee():
    """add or remove employee from database"""

    # Store a list of all drivers for the assoiciated store_id
    employees = db.execute("SELECT name FROM drivers dr JOIN stores st ON dr.store_id = st.store_id WHERE store_id = ?", session["store_id"])

    if request.method == "POST":
        return render_template("employee.html", employees=employees)



@app.route("/history", methods=["GET", "POST"])
def history():
    """shows table of dilivery history filterable by time passed"""
    return render_template("history.html")