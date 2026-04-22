from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager

class User(UserMixin, db.Model):
    """
    User model: Represents application users (Admin or Staff)
    
    Roles:
    - 'admin': Full access to all features including financial reports and user management
    - 'staff': Limited access - cannot see financial data or manage users
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')  # 'admin' or 'staff'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('StockTransaction', backref='user', lazy='dynamic')
    expenses = db.relationship('Expense', backref='created_by_user', lazy='dynamic')

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    def is_staff(self):
        """Check if user is staff"""
        return self.role == 'staff'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Product(db.Model):
    """
    Product model: Represents inventory items
    
    Fields:
    - unit_price: Sale price per unit (revenue calculation)
    - cost_price: Purchase cost per unit (COGS calculation)
    - stock: Current quantity on hand
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    sku = db.Column(db.String(80), unique=True, nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    cost_price = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('StockTransaction', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'

class StockTransaction(db.Model):
    """
    StockTransaction model: Audit trail for all inventory movements
    
    Tracks:
    - Purchase transactions: increase stock (change > 0)
    - Sale transactions: decrease stock (change < 0)
    - Full audit trail with timestamp and user who performed the transaction
    
    Financial Calculations:
    - Revenue from sales: quantity * unit_price (for sales)
    - COGS: quantity * Product.cost_price (for sales)
    """
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False, index=True)
    change = db.Column(db.Integer, nullable=False)  # positive=purchase, negative=sale
    txn_type = db.Column(db.String(20), nullable=False)  # 'purchase' or 'sale'
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    
    def __repr__(self):
        return f'<StockTransaction {self.id} {self.txn_type}>'

class Expense(db.Model):
    """
    Expense model: Tracks all operating expenses
    
    Examples: Utilities, Maintenance, Shipping, Salaries, etc.
    Only Admins can see summaries and financial calculations
    Staff can only add expenses, not view summaries
    """
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    
    def __repr__(self):
        return f'<Expense {self.id} ${self.amount}>'
