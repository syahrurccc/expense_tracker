from sqlalchemy import text
from flask import Flask, flash, redirect, render_template, request, session, get_flashed_messages
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, get_balance, validate_form, income_types, expense_types, currency_symbols
from db import engine


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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

    # Define numbers for pagination
    page = request.args.get("page", default=1, type=int)
    entries = request.args.get("entries", default=10, type=int)
    offset = (page - 1) * entries

    currency_code = session.get("currency_code", "IDR")
    symbol = currency_symbols.get(currency_code, "Rp")

    balance = get_balance(session["user_id"])
    with engine.connect() as conn:
        # Count how many rows in the table
        rows = conn.execute(text("""
            SELECT COUNT(*) FROM statements WHERE user_id = :id
        """), {"id": session["user_id"]}).scalar()

        statements = conn.execute(text("""
            SELECT * FROM statements
            WHERE user_id = :id
            ORDER BY date DESC
            LIMIT :limit OFFSET :offset
            """), {
                "id": session["user_id"],
                "limit": entries,
                "offset": offset
        }).mappings().fetchall()

    # Catch the flashed messaged with it's categories
    messages = get_flashed_messages(with_categories=True)
    expense_error = None
    income_error = None
    balance_error = None

    for category, message in messages:
        if category == "expense_error":
            expense_error = message
        elif category == "income_error":
            income_error = message
        elif category == "balance_error":
            balance_error = message

    total_pages = (rows + entries - 1) // entries

    return render_template(
        "index.html",
        statements=statements,
        balance=balance,
        income_types=income_types,
        expense_types=expense_types,
        currency_symbols=currency_symbols,
        expense_error=expense_error,
        income_error=income_error,
        balance_error=balance_error,
        symbol=symbol,
        page=page,
        entries=entries,
        total_pages=total_pages
    )

@app.route("/update_balance", methods=["POST"])
@login_required
def update_balance():

    new_balance = request.form.get("update_balance")

    try:
        if int(new_balance) < 1:
            return render_template("index.html", balance_error="Please enter a valid amount")
    except (ValueError, TypeError):
        return render_template("index.html", balance_error="Please enter a valid amount")

    with engine.begin() as conn:
        conn.execute(text("UPDATE users SET balance = :balance WHERE id = :id"),
                     {"balance": new_balance, "id": session["user_id"]})

    return redirect("/")

@app.route("/update_currency", methods=["POST"])
@login_required
def update_currency():

    currency_code = request.form.get("currency_code")
    # Save currency code in session so it's saved within session
    if currency_code in currency_symbols:
        session["currency_code"] = currency_code
    return redirect ("/")

@app.route("/add_income", methods=["POST"])
@login_required
def add_income():

    # Validate the form to get the values
    error, date_income, type_income, income, notes_income = validate_form(
        request.form, balance=None, is_income=True)

    # If error print error
    if error:
        flash(error, "income_error")
        return redirect("/")

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO statements (user_id, date, debit, type, notes)
            VALUES (:id, :date, :debit, :type, :notes)
        """), {
            "id": session["user_id"],
            "date": date_income,
            "debit": int(income),
            "type": type_income,
            "notes": notes_income
        })
        conn.execute(text("UPDATE users SET balance = balance + :income WHERE id = :id"), {
            "income": income, "id": session["user_id"]})

        return redirect("/")

@app.route("/add_expense", methods=["POST"])
@login_required
def add_expense():

    error, date_expense, type_expense, expense, notes_expense = validate_form(
        request.form, balance=get_balance(session["user_id"]), is_income=False)

    if error:
        flash(error, "expense_error")
        return redirect("/")

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO statements (user_id, date, debit, type, notes)
            VALUES (:id, :date, :debit, :type, :notes)
        """), {
            "id": session["user_id"],
            "date": date_expense,
            "debit": -int(expense),
            "type": type_expense,
            "notes": notes_expense
        })
        conn.execute(text("UPDATE users SET balance = balance - :expense WHERE id = :id"), {
            "expense": expense, "id": session["user_id"]
        })

    return redirect("/")


@app.route("/delete_statement/<int:statement_id>", methods=["POST"])
@login_required
def delete_statement(statement_id):

    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM statements WHERE id = :id AND user_id = :user_id
            """), {
            "id": statement_id,
            "user_id": session["user_id"]
        })

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return render_template("register.html", error="Missing username")
        elif not password:
            return render_template("register.html", error="Missing password")
        elif not confirmation:
            return render_template("register.html", error="Missing confirmation")
        elif confirmation != password:
            return render_template("register.html", error="Password and confirmation must match")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT username FROM users WHERE username = :username"), {
                                  "username": username}).fetchone()
            if result:
                return render_template("register.html", error="Username has been taken")
        with engine.begin() as conn:
            password_hash = generate_password_hash(password)
            conn.execute(text("INSERT INTO users (username, hash) VALUES (:username, :hash)"), {
                         "username": username, "hash": password_hash})
            flash("Registration successful! You can now log in.")
            return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("login.html", error="Require username")
        elif not request.form.get("password"):
            return render_template("login.html", error="Require password")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM users WHERE username = :username"),
                                  {"username": request.form.get("username")}).mappings().fetchone()
            if not result or not check_password_hash(result["hash"], request.form.get("password")):
                return render_template("login.html", error="Invalid username and/or password")

        session["user_id"] = result["id"]
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():

    session.clear()

    return redirect("/")
