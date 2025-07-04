
from sqlalchemy import text
from flask import redirect, session
from functools import wraps
from db import engine
from datetime import datetime, date

income_types = ["Salary", "Gift", "Allowance", "Credit", "Social Support", "Other"]
expense_types = ["Food", "Transportation", "Education",
                     "Charity", "Housing", "Internet", "Other"]
currency_symbols = {
    "IDR": "Rp",   # Indonesian Rupiah
    "USD": "$",    # US Dollar
    "EUR": "€",    # Euro
    "JPY": "¥",    # Japanese Yen
    "GBP": "£",    # British Pound
    "AUD": "A$",   # Australian Dollar
    "CAD": "C$",   # Canadian Dollar
    "CHF": "CHF",  # Swiss Franc
    "CNY": "¥",    # Chinese Yuan Renminbi
    "SGD": "S$",   # Singapore Dollar
}


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def get_balance(user_id):
    # mapping() to make the output as dict like object fetchone() to get 1 value
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT balance FROM users WHERE id = :id"),
            {"id": user_id}
        ).mappings().fetchone()
        return result["balance"] if result else 0

def validate_form(form, balance=None, is_income=False):

    date_form = form.get("date_income" if is_income else "date_expense")
    type = form.get("type_income" if is_income else "type_expense")
    amount = form.get("income" if is_income else "expense")
    # strip() to cut all extra whitespaces
    notes = (form.get("notes_income" if is_income else "notes_expense") or '').strip()

    if not date_form:
        return "Please enter a valid date", None, None, None, None
    elif not type:
        return "Please choose a valid type", None, None, None, None
    elif not amount:
        return "Please enter a valid amount", None, None, None, None

    try:
        if int(amount) < 1:
            return "Please enter a valid amount", None, None, None, None
    except ValueError:
        return "Please enter a valid amount", None, None, None, None

    try:
        # Check if the date format is correct
        valid_date = datetime.strptime(date_form, "%Y-%m-%d")
    except (ValueError, TypeError):
        return "Please enter a valid date", None, None, None, None

    if valid_date.date() > date.today():
        return "Please enter a valid date", None, None, None, None

    if not is_income and balance is not None and int(amount) > int(balance):
        return "Expense exceeds balance", None, None, None, None

    return None, date_form, type, amount, notes
