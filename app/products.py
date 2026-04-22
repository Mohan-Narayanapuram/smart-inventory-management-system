"""
Products Module: Inventory and Product Management

Features:
- CRUD operations for products (admin and staff can create/edit, only admin can delete)
- Stock level tracking with full audit trail
- Two pricing models:
  * unit_price: Sale price (revenue calculation)
  * cost_price: Purchase cost (COGS calculation)

Permission Model:
- Admin & Staff: Can create, edit, and update stock on products
- Admin Only: Can delete products
- All authenticated users: Can view inventory
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .models import Product, StockTransaction
from . import db
from .decorators import roles_required

products_bp = Blueprint("products", __name__)


@products_bp.route("/")
@login_required
def list_products():
    """
    Display all products with their current stock levels and pricing.
    
    Visible to all authenticated users (admin and staff).
    Shows: name, SKU, stock, unit price, cost price
    """
    products = Product.query.order_by(Product.name).all()
    return render_template("products/list.html", products=products)


@products_bp.route("/create", methods=["GET", "POST"])
@roles_required("admin", "staff")
def create_product():
    """
    Create a new product.
    
    Required fields:
    - name: Product name
    - unit_price: Sale price per unit
    - cost_price: Purchase cost per unit
    
    Optional fields:
    - sku: Stock Keeping Unit (unique identifier)
    - description: Product details
    - stock: Initial stock quantity
    
    Both Admin and Staff can create products.
    Stock is initially set via this form, then updated via stock transactions.
    """
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            sku = request.form.get("sku", "").strip() or None
            description = request.form.get("description", "").strip()
            unit_price = float(request.form.get("unit_price", 0))
            cost_price = float(request.form.get("cost_price", 0))
            stock = int(request.form.get("stock", 0))

            # Validation
            if not name:
                flash("Product name is required", "danger")
                return render_template("products/form.html", product=None)

            if unit_price < 0:
                flash("Unit price cannot be negative", "danger")
                return render_template("products/form.html", product=None)

            if cost_price < 0:
                flash("Cost price cannot be negative", "danger")
                return render_template("products/form.html", product=None)

            if stock < 0:
                flash("Stock quantity cannot be negative", "danger")
                return render_template("products/form.html", product=None)

            # Check for duplicate SKU
            if sku and Product.query.filter_by(sku=sku).first():
                flash(f"SKU '{sku}' already in use", "warning")
                return render_template("products/form.html", product=None)

            # Create product
            product = Product(
                name=name,
                sku=sku,
                description=description or None,
                unit_price=unit_price,
                cost_price=cost_price,
                stock=stock,
            )
            db.session.add(product)
            db.session.commit()

            flash(f"Product '{name}' created successfully", "success")
            return redirect(url_for("products.list_products"))

        except ValueError:
            flash("Invalid numeric input. Check prices and stock.", "danger")
            return render_template("products/form.html", product=None)

    return render_template("products/form.html", product=None)


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@roles_required("admin", "staff")
def edit_product(product_id):
    """
    Edit an existing product's details.
    
    Can be updated:
    - name, SKU, description, unit_price, cost_price
    
    Cannot be updated via this endpoint:
    - stock: Must use stock transaction endpoint for audit trail
    
    Stock updates must go through the stock transaction system to maintain
    a complete audit trail of all inventory movements.
    """
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            sku = request.form.get("sku", "").strip() or None
            description = request.form.get("description", "").strip()
            unit_price = float(request.form.get("unit_price", 0))
            cost_price = float(request.form.get("cost_price", 0))

            # Validation
            if not name:
                flash("Product name is required", "danger")
                return render_template("products/form.html", product=product)

            if unit_price < 0:
                flash("Unit price cannot be negative", "danger")
                return render_template("products/form.html", product=product)

            if cost_price < 0:
                flash("Cost price cannot be negative", "danger")
                return render_template("products/form.html", product=product)

            # Check for duplicate SKU (excluding current product)
            if sku and sku != product.sku:
                if Product.query.filter_by(sku=sku).first():
                    flash(f"SKU '{sku}' already in use", "warning")
                    return render_template("products/form.html", product=product)

            # Update product
            product.name = name
            product.sku = sku
            product.description = description or None
            product.unit_price = unit_price
            product.cost_price = cost_price

            db.session.commit()
            flash(f"Product '{name}' updated successfully", "success")
            return redirect(url_for("products.list_products"))

        except ValueError:
            flash("Invalid numeric input. Check prices.", "danger")
            return render_template("products/form.html", product=product)

    return render_template("products/form.html", product=product)


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
@roles_required("admin")
def delete_product(product_id):
    """
    Delete a product (Admin only).
    
    Warning: This is a destructive operation. The product and all
    associated transactions will be deleted from the database.
    
    Consider if products should instead be marked as inactive rather
    than deleted for better audit trail preservation.
    """
    product = Product.query.get_or_404(product_id)
    product_name = product.name

    db.session.delete(product)
    db.session.commit()

    flash(f"Product '{product_name}' has been deleted", "success")
    return redirect(url_for("products.list_products"))


@products_bp.route("/<int:product_id>/stock", methods=["GET", "POST"])
@roles_required("admin", "staff")
def update_stock(product_id):
    """
    Record a stock transaction (purchase or sale).
    
    This is the primary way to update inventory levels. Every change
    creates an audit trail entry recording:
    - What product
    - How much (quantity)
    - At what price
    - When
    - Who made the change
    
    Transaction Types:
    1. Purchase: Increase stock from supplier
       - unit_price = cost per unit
       - Revenue calculation uses this
    
    2. Sale: Decrease stock from sale to customer
       - unit_price = sale price per unit
       - Revenue = quantity * unit_price
       - COGS = quantity * product.cost_price
    
    Stock Validation:
    - For sales: Prevents overselling (stock check)
    - All transactions recorded with full audit trail
    """
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        try:
            txn_type = request.form.get("txn_type", "").strip()
            quantity = int(request.form.get("quantity", 0))
            unit_price = float(request.form.get("unit_price", 0))

            # Validation
            if txn_type not in ["purchase", "sale"]:
                flash("Invalid transaction type", "danger")
                return redirect(url_for("products.update_stock", product_id=product_id))

            if quantity <= 0:
                flash("Quantity must be greater than zero", "danger")
                return redirect(url_for("products.update_stock", product_id=product_id))

            if unit_price < 0:
                flash("Unit price cannot be negative", "danger")
                return redirect(url_for("products.update_stock", product_id=product_id))

            # Check for overselling
            if txn_type == "sale":
                if product.stock < quantity:
                    flash(
                        f"Insufficient stock. Available: {product.stock}, "
                        f"Requested: {quantity}",
                        "danger"
                    )
                    return redirect(
                        url_for("products.update_stock", product_id=product_id)
                    )
                product.stock -= quantity
            elif txn_type == "purchase":
                product.stock += quantity

            # Record transaction for audit trail
            transaction = StockTransaction(
                product_id=product.id,
                change=quantity if txn_type == "purchase" else -quantity,
                txn_type=txn_type,
                quantity=quantity,
                unit_price=unit_price,
                user_id=current_user.id,
            )

            db.session.add(transaction)
            db.session.commit()

            flash(
                f"{txn_type.capitalize()} of {quantity} units recorded. "
                f"New stock: {product.stock}",
                "success"
            )
            return redirect(url_for("products.list_products"))

        except ValueError:
            flash("Invalid numeric input. Check quantity and price.", "danger")
            return redirect(url_for("products.update_stock", product_id=product_id))

    return render_template("products/stock.html", product=product)
