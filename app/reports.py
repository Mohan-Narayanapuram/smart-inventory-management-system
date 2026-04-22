from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func, desc
from .models import Product, StockTransaction, Expense, User
from . import db
from .decorators import roles_required
from datetime import datetime, date

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/financial-summary")
@roles_required("admin")
def financial_summary():
    # ── Filters ──────────────────────────────────────────────
    months = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]
    current_year  = date.today().year
    current_month = date.today().month

    sel_month = request.args.get("month", type=int, default=current_month)
    sel_year  = request.args.get("year",  type=int, default=current_year)

    years = list(range(current_year - 3, current_year + 1))

    def txn_filter(q):
        return q.filter(
            func.strftime('%m', StockTransaction.timestamp) == f"{sel_month:02d}",
            func.strftime('%Y', StockTransaction.timestamp) == str(sel_year),
        )

    # ── Queries ───────────────────────────────────────────────
    revenue = txn_filter(
        db.session.query(func.coalesce(func.sum(StockTransaction.quantity * StockTransaction.unit_price), 0))
        .filter(StockTransaction.txn_type == "sale")
    ).scalar() or 0

    cogs = txn_filter(
        db.session.query(func.coalesce(func.sum(StockTransaction.quantity * Product.cost_price), 0))
        .join(Product, Product.id == StockTransaction.product_id)
        .filter(StockTransaction.txn_type == "sale")
    ).scalar() or 0

    total_expenses = db.session.query(
        func.coalesce(func.sum(Expense.amount), 0)
    ).filter(
        func.strftime('%m', Expense.date) == f"{sel_month:02d}",
        func.strftime('%Y', Expense.date) == str(sel_year),
    ).scalar() or 0

    gross_profit = float(revenue) - float(cogs)
    net_profit   = gross_profit - float(total_expenses)

    units_sold = txn_filter(
        db.session.query(func.coalesce(func.sum(StockTransaction.quantity), 0))
        .filter(StockTransaction.txn_type == "sale")
    ).scalar() or 0

    data = {
        "revenue":          float(revenue),
        "cogs":             float(cogs),
        "gross_profit":     gross_profit,
        "expenses":         float(total_expenses),
        "profit":           net_profit,
        "total_units_sold": int(units_sold),
    }

    return render_template(
        "reports.html",
        data=data,
        sel_month=sel_month,
        sel_year=sel_year,
        months=months,
        years=years,
    )


@reports_bp.route("/transaction-details")
@roles_required("admin")
def transaction_details():
    # ── Filters ──────────────────────────────────────────────
    date_from = request.args.get("date_from", "")
    date_to   = request.args.get("date_to",   "")
    txn_type  = request.args.get("txn_type",  "")
    search    = request.args.get("search",    "").strip()

    # ── Base query ────────────────────────────────────────────
    q = StockTransaction.query.join(Product, Product.id == StockTransaction.product_id)

    if date_from:
        try:
            q = q.filter(StockTransaction.timestamp >= datetime.strptime(date_from, "%Y-%m-%d"))
        except ValueError:
            pass
    if date_to:
        try:
            q = q.filter(StockTransaction.timestamp <= datetime.strptime(date_to, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        except ValueError:
            pass
    if txn_type in ("sale", "purchase"):
        q = q.filter(StockTransaction.txn_type == txn_type)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))

    transactions_raw = q.order_by(desc(StockTransaction.timestamp)).all()

    transaction_data = []
    for txn in transactions_raw:
        product = Product.query.get(txn.product_id)
        transaction_data.append({
            "id":         txn.id,
            "product":    product.name if product else "Unknown",
            "type":       txn.txn_type.upper(),
            "quantity":   txn.quantity,
            "unit_price": float(txn.unit_price),
            "total":      txn.quantity * float(txn.unit_price),
            "timestamp":  txn.timestamp,
            "user":       txn.user.username if txn.user else "Unknown",
        })

    return render_template(
        "transaction_details.html",
        transactions=transaction_data,
        date_from=date_from,
        date_to=date_to,
        txn_type=txn_type,
        search=search,
    )


@reports_bp.route("/expense-summary")
@roles_required("admin")
def expense_summary():
    # ── Filters ──────────────────────────────────────────────
    date_from = request.args.get("date_from", "")
    date_to   = request.args.get("date_to",   "")
    category  = request.args.get("category",  "")

    # All unique categories for dropdown
    categories = [
        r[0] for r in db.session.query(Expense.description)
        .distinct().order_by(Expense.description).all() if r[0]
    ]

    # ── Base query ────────────────────────────────────────────
    q = Expense.query

    if date_from:
        try:
            q = q.filter(Expense.date >= datetime.strptime(date_from, "%Y-%m-%d"))
        except ValueError:
            pass
    if date_to:
        try:
            q = q.filter(Expense.date <= datetime.strptime(date_to, "%Y-%m-%d"))
        except ValueError:
            pass
    if category:
        q = q.filter(Expense.description == category)

    all_expenses = q.order_by(desc(Expense.date)).all()

    # Summary grouped by description (respects date filters, not category filter)
    summary_q = db.session.query(
        Expense.description,
        func.count(Expense.id).label("count"),
        func.sum(Expense.amount).label("total"),
    )
    if date_from:
        try:
            summary_q = summary_q.filter(Expense.date >= datetime.strptime(date_from, "%Y-%m-%d"))
        except ValueError:
            pass
    if date_to:
        try:
            summary_q = summary_q.filter(Expense.date <= datetime.strptime(date_to, "%Y-%m-%d"))
        except ValueError:
            pass

    expense_summary_data = summary_q.group_by(Expense.description).all()

    total_expenses = float(sum(r.total or 0 for r in expense_summary_data))

    return render_template(
        "expense_summary.html",
        expense_summary=expense_summary_data,
        all_expenses=all_expenses,
        total_expenses=total_expenses,
        categories=categories,
        date_from=date_from,
        date_to=date_to,
        category=category,
    )