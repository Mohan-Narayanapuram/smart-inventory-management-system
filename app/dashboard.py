"""
Dashboard Module: Main landing page with role-specific metrics

The dashboard provides:
- All users: Basic inventory metrics (total products, stock units)
- Admins only: Financial metrics (revenue, COGS, expenses, profit/loss)

This ensures staff members cannot see any financial performance data,
maintaining role-based access control at both backend and frontend levels.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from .models import Product, StockTransaction, Expense
from . import db
from .decorators import roles_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """
    Main dashboard endpoint.
    
    Universal metrics (all users):
    - total_products: Count of all products in inventory
    - total_stock_units: Sum of all stock quantities
    
    Admin-only metrics (hidden from staff):
    - revenue: Sum of (quantity * unit_price) for all sales
    - cogs: Sum of (quantity * product.cost_price) for all sales
    - expenses: Sum of all operating expenses
    - profit: revenue - cogs - expenses
    
    The template checks current_user.role and only displays
    financial metrics if user is admin.
    """
    # Basic inventory metrics - visible to all
    total_products = Product.query.count()
    total_stock_units = db.session.query(
        func.sum(Product.stock)
    ).scalar() or 0

    data = {
        "total_products": total_products,
        "total_stock_units": int(total_stock_units),
    }

    # Admin-only financial metrics
    if current_user.role == "admin":
        # Revenue: sum of (quantity * unit_price) for all sales
        revenue = db.session.query(
            func.coalesce(
                func.sum(
                    StockTransaction.quantity * StockTransaction.unit_price
                ),
                0
            )
        ).filter(StockTransaction.txn_type == "sale").scalar() or 0

        # COGS: sum of (quantity * cost_price) for all sales
        # Requires joining with Product to get cost_price
        cogs = db.session.query(
            func.coalesce(
                func.sum(StockTransaction.quantity * Product.cost_price),
                0
            )
        ).join(
            Product, Product.id == StockTransaction.product_id
        ).filter(
            StockTransaction.txn_type == "sale"
        ).scalar() or 0

        # Operating expenses
        expenses = db.session.query(
            func.coalesce(func.sum(Expense.amount), 0)
        ).scalar() or 0

        # Net profit calculation
        profit = float(revenue) - float(cogs) - float(expenses)

        data.update({
            "revenue": float(revenue),
            "cogs": float(cogs),
            "expenses": float(expenses),
            "profit": profit,
        })

    return render_template("dashboard.html", data=data)
