from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import desc
from .models import Product, StockTransaction, User
from . import db
from .decorators import roles_required
from datetime import datetime

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")


@sales_bp.route("/", methods=["GET"])
@roles_required("admin", "staff")
def list_sales():
    """
    Sales log view.
    - Admin: sees all sale transactions with staff name
    - Staff: sees only their own sale transactions
    """
    search = request.args.get("search", "").strip()
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")

    q = (
        StockTransaction.query
        .join(Product, Product.id == StockTransaction.product_id)
        .filter(StockTransaction.txn_type == "sale")
    )

    # Staff can only see their own sales
    if current_user.role == "staff":
        q = q.filter(StockTransaction.user_id == current_user.id)

    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))

    if date_from:
        try:
            q = q.filter(StockTransaction.timestamp >= datetime.strptime(date_from, "%Y-%m-%d"))
        except ValueError:
            pass

    if date_to:
        try:
            q = q.filter(
                StockTransaction.timestamp <= datetime.strptime(date_to, "%Y-%m-%d").replace(
                    hour=23, minute=59, second=59
                )
            )
        except ValueError:
            pass

    sales_raw = q.order_by(desc(StockTransaction.timestamp)).all()

    sales_data = []
    for txn in sales_raw:
        sales_data.append({
            "id":         txn.id,
            "product":    txn.product.name if txn.product else "Unknown",
            "quantity":   txn.quantity,
            "unit_price": float(txn.unit_price),
            "total":      txn.quantity * float(txn.unit_price),
            "timestamp":  txn.timestamp,
            "staff":      txn.user.username if txn.user else "Unknown",
        })

    total_revenue = sum(s["total"] for s in sales_data)
    total_units   = sum(s["quantity"] for s in sales_data)

    products = Product.query.filter(Product.stock > 0).order_by(Product.name).all()

    return render_template(
        "sales/index.html",
        sales=sales_data,
        products=products,
        total_revenue=total_revenue,
        total_units=total_units,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )


@sales_bp.route("/add", methods=["POST"])
@roles_required("admin", "staff")
def add_sale():
    """
    Log a new sale:
    1. Validate stock availability
    2. Create StockTransaction (txn_type='sale', change=-qty)
    3. Deduct from Product.stock
    """
    product_id = request.form.get("product_id", type=int)
    quantity   = request.form.get("quantity",   type=int)
    unit_price = request.form.get("unit_price", type=float)

    if not product_id or not quantity or quantity <= 0:
        flash("Please fill in all fields with valid values.", "error")
        return redirect(url_for("sales.list_sales"))

    product = Product.query.get(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("sales.list_sales"))

    if product.stock < quantity:
        flash(
            f"Insufficient stock. Only {product.stock} unit(s) available for '{product.name}'.",
            "error",
        )
        return redirect(url_for("sales.list_sales"))

    # Use provided price or fall back to product's unit_price
    sale_price = unit_price if (unit_price and unit_price > 0) else float(product.unit_price)

    txn = StockTransaction(
        product_id=product_id,
        change=-quantity,          # negative = stock going out
        txn_type="sale",
        quantity=quantity,
        unit_price=sale_price,
        user_id=current_user.id,
        timestamp=datetime.utcnow(),
    )
    product.stock -= quantity

    db.session.add(txn)
    db.session.commit()

    flash(
        f"Sale logged: {quantity} × {product.name} @ ₹{sale_price:,.2f} = ₹{quantity * sale_price:,.2f}",
        "success",
    )
    return redirect(url_for("sales.list_sales"))
