"""
Expenses Module: Record and track business operating expenses

All users (both admin and staff) can:
- Add new expenses
- View the list of expenses with descriptions and amounts

Only Admins can:
- View financial summaries and expense reports
- See profit/loss calculations that include expenses
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import date, datetime
from .models import Expense
from . import db
from .decorators import roles_required

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/")
@login_required
def list_expenses():
    """
    List all expenses.

    All authenticated users can view:
    - Date of expense
    - Amount
    - Description
    - Who recorded it
    """
    expenses = Expense.query.order_by(Expense.date.desc()).all()

    # ── NEW: pass total and today's date to template ──
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    today_date = date.today().isoformat()  # e.g. "2026-04-15"

    return render_template(
        "expenses/list.html",
        expenses=expenses,
        total_expenses=float(total_expenses),
        today_date=today_date,
    )


@expenses_bp.route("/create", methods=["GET", "POST"])
@roles_required("admin", "staff")
def create_expense():
    """
    Create a new expense record.

    Required fields:
    - amount: numeric value of the expense
    - description: what the expense is for (optional but recommended)
    - date: when the expense occurred (optional, defaults to now)

    Both Admin and Staff can record expenses.
    The user who records the expense is automatically recorded in the audit trail.
    """
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", 0))

            if amount <= 0:
                flash("Expense amount must be greater than zero", "danger")
                return render_template("expenses/form.html")

            description = request.form.get("description", "").strip()
            date_str = request.form.get("date")

            # Parse date if provided, otherwise use current time
            date_val = None
            if date_str:
                try:
                    date_val = datetime.fromisoformat(date_str)
                except (ValueError, AttributeError):
                    flash("Invalid date format", "warning")
                    return render_template("expenses/form.html")

            # Create and save expense
            expense = Expense(
                amount=amount,
                description=description or None,
                date=date_val,
                created_by=current_user.id,
            )
            db.session.add(expense)
            db.session.commit()

            flash(f"Expense of ₹{amount:.2f} recorded successfully", "success")
            return redirect(url_for("expenses.list_expenses"))

        except (ValueError, TypeError):
            flash("Invalid input. Please check the amount field.", "danger")
            return render_template("expenses/form.html")

    return render_template("expenses/form.html")