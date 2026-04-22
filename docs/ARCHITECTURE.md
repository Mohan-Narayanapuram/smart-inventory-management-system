# Smart Inventory Management System - Architecture & Design Document

## Table of Contents
1. System Architecture
2. Role-Based Access Control
3. Database Design
4. Financial Calculation Logic
5. Module Descriptions
6. Security Model
7. Deployment Architecture

---

## 1. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser (Client)                  │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/HTTPS
┌───────────────────────▼─────────────────────────────────┐
│              Flask Application Server                     │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │            Flask Blueprints (Modules)               │ │
│ ├────────────┬──────────────┬──────────────┬──────────┤ │
│ │   auth.py  │ products.py  │ expenses.py  │ reports  │ │
│ │            │              │              │          │ │
│ │ • Login    │ • CRUD       │ • Create     │ • Admin  │ │
│ │ • Logout   │ • Stock      │ • List       │ • Only   │ │
│ │ • Users    │ • Audit      │ • Categorize │ • Graphs │ │
│ └────────────┴──────────────┴──────────────┴──────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │              Core Components                         │ │
│ ├──────────────┬──────────────┬──────────────────────┤ │
│ │ models.py    │ decorators   │ dashboard.py         │ │
│ │              │              │                      │ │
│ │ • User       │ • RBAC       │ • Metrics calc       │ │
│ │ • Product    │ • roles_req  │ • Financial calcs    │ │
│ │ • Transaction│              │                      │ │
│ │ • Expense    │              │                      │ │
│ └──────────────┴──────────────┴──────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│           Template Rendering (Jinja2)                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │ base.html + role-based content selection         │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │ SQLAlchemy ORM
                        │
┌───────────────────────▼─────────────────────────────────┐
│              SQLite Database (sepm.db)                    │
├─────────────────────────────────────────────────────────┤
│  user | product | stock_transaction | expense           │
└─────────────────────────────────────────────────────────┘
```

### Request-Response Flow

```
1. User accesses application
   │
   ├─ Is authenticated?
   │   ├─ No  → Redirect to /login
   │   └─ Yes → Check role
   │
2. Check Role-Based Access Control
   │
   ├─ Route requires admin?
   │   ├─ User is admin  → Allow
   │   ├─ User is staff  → 403 Forbidden
   │   └─ Not logged in  → Redirect to login
   │
3. Execute Route Handler
   │
   ├─ Process request (GET/POST)
   ├─ Query/Modify database via SQLAlchemy
   ├─ Perform business logic calculations
   └─ Return rendered template
   │
4. Render Template
   │
   ├─ Load base.html (navigation)
   ├─ Check current_user.role
   ├─ Conditionally show admin-only elements
   └─ Return HTML to browser
```

---

## 2. Role-Based Access Control (RBAC)

### Access Matrix

| Feature | Admin | Staff | Anonymous |
|---------|-------|-------|-----------|
| Login | ✓ | ✓ | ✓ |
| View Dashboard | ✓ | ✓ | ✗ |
| View Inventory | ✓ | ✓ | ✗ |
| Add Product | ✓ | ✓ | ✗ |
| Edit Product | ✓ | ✓ | ✗ |
| Delete Product | ✓ | ✗ | ✗ |
| Record Stock Transaction | ✓ | ✓ | ✗ |
| Record Expense | ✓ | ✓ | ✗ |
| View Expense List | ✓ | ✓ | ✗ |
| View Financial Reports | ✓ | ✗ | ✗ |
| View Profit/Loss | ✓ | ✗ | ✗ |
| Manage Users | ✓ | ✗ | ✗ |

### Implementation: Decorator Pattern

```python
# Backend: enforced at route level
@app.route("/reports/financial")
@roles_required("admin")  # Returns 403 if not admin
def financial_reports():
    return render_template("reports.html")

# Frontend: enforced in templates
{% if current_user.role == 'admin' %}
    <a href="{{ url_for('reports.financial_summary') }}">Reports</a>
{% endif %}
```

**Defense in Depth**: Both backend AND frontend checks ensure staff cannot access financial data even if they craft URLs manually.

---

## 3. Database Design

### Entity-Relationship Diagram

```
user
├─ id (PK)
├─ username (UNIQUE)
├─ password_hash
├─ role ('admin' | 'staff')
├─ created_at
│
├─< stock_transaction (1:many)
│   ├─ id
│   ├─ product_id (FK)
│   ├─ quantity
│   ├─ unit_price
│   ├─ txn_type ('purchase' | 'sale')
│   ├─ timestamp
│   └─ [user_id references user]
│
└─< expense (1:many)
    ├─ id
    ├─ amount
    ├─ description
    ├─ date
    └─ [created_by references user]


product
├─ id (PK)
├─ name
├─ sku (UNIQUE, nullable)
├─ unit_price
├─ cost_price
├─ stock
├─ created_at
│
└─< stock_transaction (1:many)
    ├─ id
    ├─ change
    ├─ quantity
    ├─ unit_price
    ├─ txn_type
    ├─ timestamp
    └─ [product_id references product]
```

### Schema Details

**Numeric Precision**:
- Prices: `NUMERIC(12, 2)` = $99,999,999.99 max
- Sufficient for small/medium businesses

**Indexes**:
- `user.username` - Fast login lookups
- `product.sku` - Fast product searches
- `product.name` - Alphabetical sorting
- `stock_transaction.product_id` - Quick transaction history
- `stock_transaction.timestamp` - Time-range queries
- `stock_transaction.user_id` - Audit trail by user
- `expense.created_by` - Expense tracking by user

---

## 4. Financial Calculation Logic

### Revenue Calculation

```python
# In dashboard.py:
revenue = db.session.query(
    func.sum(StockTransaction.quantity * StockTransaction.unit_price)
).filter(StockTransaction.txn_type == "sale").scalar()

# Example:
# Sale 1: 5 units @ $100 = $500
# Sale 2: 3 units @ $150 = $450
# Total Revenue = $950
```

### Cost of Goods Sold (COGS)

```python
# SQL concept:
SELECT SUM(st.quantity * p.cost_price)
FROM stock_transaction st
JOIN product p ON st.product_id = p.id
WHERE st.txn_type = 'sale'

# Example:
# Sale 1: 5 units (cost $60 each) = 5 × $60 = $300
# Sale 2: 3 units (cost $80 each) = 3 × $80 = $240
# Total COGS = $540
```

### Profit Calculation

```
Revenue       = $950
- COGS        = $540
= Gross Profit = $410
- Expenses    = $100
= Net Profit  = $310
```

### Key Insight

**Why we need both `unit_price` and `cost_price`**:

```
Product A:
- Purchased at cost_price: $50
- Sold at unit_price: $100
- Profit per unit: $50

Sale Transaction records:
- quantity: 5
- unit_price: $100 (use for revenue)
- product.cost_price: $50 (use for COGS)

Revenue = 5 × $100 = $500
COGS = 5 × $50 = $250
Profit = $250
```

---

## 5. Module Descriptions

### auth.py - Authentication Module
**Responsibilities**:
- User login/logout
- User creation (admin only)
- User role management
- Password hashing

**Key Functions**:
- `login()` - Handle login form, verify credentials
- `create_user()` - Admin create new users
- `edit_user()` - Admin modify user role/password
- `delete_user()` - Admin delete users (prevent last admin deletion)

### products.py - Inventory Management
**Responsibilities**:
- Product CRUD operations
- Stock transaction recording
- Inventory audit trail
- Stock level validation

**Key Functions**:
- `list_products()` - Display all products
- `create_product()` - Add new product
- `edit_product()` - Modify product details (not stock)
- `update_stock()` - Record purchase/sale transactions
- `delete_product()` - Remove product (admin only)

**Stock Transaction Validation**:
```python
if txn_type == "sale":
    if product.stock < quantity:
        flash("Insufficient stock")  # Prevent overselling
    product.stock -= quantity
elif txn_type == "purchase":
    product.stock += quantity
```

### expenses.py - Expense Tracking
**Responsibilities**:
- Record operating expenses
- Categorize expenses (optional)
- Track expense history

**Key Functions**:
- `list_expenses()` - Show all expenses
- `create_expense()` - Record new expense

**Design Note**: All users can record expenses, but only admins see financial summaries that include expenses.

### dashboard.py - Dashboard & Metrics
**Responsibilities**:
- Calculate key metrics
- Enforce role-based metric visibility
- Provide quick overview

**Metrics Shown**:
- All users: Products count, stock units
- Admins: Revenue, COGS, Expenses, Profit

### reports.py - Financial Reports (Admin Only)
**Responsibilities**:
- Detailed financial analysis
- Transaction audit trails
- Expense breakdowns

**Key Reports**:
- `financial_summary()` - Revenue, COGS, profit, margins
- `transaction_details()` - All stock movements
- `expense_summary()` - Expense breakdown by category

### decorators.py - RBAC Enforcement
**Responsibilities**:
- Protect routes with role checks
- Return 403 Forbidden for unauthorized access

**Implementation**:
```python
@roles_required("admin")
def admin_only_route():
    # Only admins reach here
    pass

@roles_required("admin", "staff")
def both_can_access():
    # Admins and staff reach here
    pass
```

### models.py - Database Models
**Responsibilities**:
- Define data structure
- Enforce data relationships
- Provide ORM interface

**Models**:
1. **User** - Authentication and roles
2. **Product** - Inventory items
3. **StockTransaction** - Audit trail
4. **Expense** - Operating costs

---

## 6. Security Model

### Authentication Security

```
User Password:
  Input: "mypassword"
    ↓
  Hash with Werkzeug: pbkdf2:sha256:...{hashed}
    ↓
  Store in database: password_hash
  
On Login:
  Input: "mypassword"
    ↓
  Hash and compare with stored hash
    ↓
  Match? → Create session → Set secure cookie
  No match? → Reject login
```

### Session Management

```python
# Flask-Login handles:
- Creates session cookie on login
- Validates session on each request
- Auto-logout on session expiration
- Prevents CSRF attacks
```

### Authorization Security

```python
# Layer 1: Route Protection
@roles_required("admin")
def route():
    pass  # 403 if not admin

# Layer 2: Template Rendering
{% if current_user.role == 'admin' %}
    {{ sensitive_data }}
{% endif %}

# Layer 3: Database Query
revenue = get_revenue()  # Only calculated for admins

# Result: Even if someone bypasses Layer 1,
# they can't see data (no route), see UI (template), or calculate (logic)
```

### Data Integrity

1. **Stock Validation**: Prevents overselling
2. **Audit Trail**: Every transaction recorded with user
3. **Input Validation**: All numeric inputs checked
4. **SQL Injection Prevention**: SQLAlchemy parameterized queries

---

## 7. Deployment Architecture

### Development Environment

```
Developer's Computer
└── Flask Development Server
    ├── Debug mode enabled
    ├── Auto-reload on file changes
    ├── Hot reload templates
    └── SQLite database (local)
```

### Production Environment

```
Internet
    │ HTTPS
    ▼
Load Balancer
    │
    ├─ Instance 1 ─┐
    ├─ Instance 2 ─┤ Application Servers (Gunicorn WSGI)
    └─ Instance 3 ─┘
    
    └─ Database Server (PostgreSQL)
    
    └─ Backup System
```

### Environment-Specific Configuration

```python
# config.py
if os.environ.get('ENV') == 'production':
    SECRET_KEY = os.environ['SECRET_KEY']  # Must be set
    DATABASE_URL = os.environ['DATABASE_URL']  # PostgreSQL
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SQLALCHEMY_ECHO = False  # No SQL logging
else:
    SECRET_KEY = "dev-key"  # Auto-generated
    DATABASE_URL = "sqlite:///sepm.db"  # Local DB
    SESSION_COOKIE_SECURE = False
```

### Scalability Path

```
Stage 1: Small Business (< 5 users, < 1000 products)
- Single SQLite database
- Single application server
- Manual backups

Stage 2: Growing (< 20 users, < 10,000 products)
- PostgreSQL database
- Single application server
- Automated backups
- Add caching (Redis)

Stage 3: Enterprise (> 20 users, > 100,000 products)
- PostgreSQL with replication
- Multiple application servers (load balanced)
- Redis caching layer
- Read replicas for reporting
- Separate database user for read-only operations
```

---

## Key Design Decisions

### 1. Two-Tier Access Control
**Decision**: Enforce role checks at both backend (decorators) and frontend (templates)
**Reasoning**: Defense in depth - prevents accidental exposure if one layer fails

### 2. Separate Pricing Fields
**Decision**: Keep `unit_price` (sale) and `cost_price` (purchase) separate
**Reasoning**: Allows accurate profit calculation; can change selling price without affecting historical cost

### 3. Immutable Stock Audit Trail
**Decision**: Don't allow direct stock edits; all changes go through transactions
**Reasoning**: Maintains complete audit trail; can audit "who did what when"

### 4. SQLite by Default
**Decision**: Use SQLite for development, easy migration to PostgreSQL
**Reasoning**: Low barrier to entry; sufficient for small-medium businesses; schema-agnostic ORM

### 5. Session-Based Authentication
**Decision**: Use Flask-Login with session cookies, not JWT
**Reasoning**: Simpler for traditional web app; suitable for single-domain deployment; built-in CSRF protection

---

## Data Flow Examples

### Example 1: Recording a Sale

```
1. Staff clicks "Update Stock" on Product "Timber"
   
2. Form submitted:
   - txn_type: "sale"
   - quantity: 10
   - unit_price: $150
   
3. Backend validation:
   - stock >= quantity? (100 >= 10) ✓
   - unit_price >= 0? ✓
   
4. Database operations:
   - INSERT stock_transaction (product_id=1, txn_type='sale', quantity=10, unit_price=150, user_id=5)
   - UPDATE product SET stock = stock - 10 WHERE id = 1
   
5. Financial impact:
   - Revenue increases by: 10 × $150 = $1,500
   - COGS increases by: 10 × cost_price (from product record)
   - Dashboard recalculates profit on next access
   
6. Audit trail:
   - User 5 (Staff) recorded sale
   - Timestamp: 2024-01-21 14:30:00
   - Product: Timber
   - Quantity: 10 units
   - Price: $150/unit
```

### Example 2: Admin Viewing Financial Report

```
1. Admin clicks "Reports" → "Financial Summary"
   
2. Backend checks role:
   - current_user.role == 'admin'? ✓
   
3. Database calculations:
   - Revenue = SUM(quantity × unit_price) WHERE txn_type='sale'
   - COGS = SUM(quantity × product.cost_price) WHERE txn_type='sale'
   - Expenses = SUM(amount) FROM expenses
   - Profit = Revenue - COGS - Expenses
   
4. Template rendering:
   - Only shows financial data (protected by {% if current_user.role == 'admin' %})
   - Displays charts and metrics
   
5. Staff cannot see this page:
   - Even if they manually enter /reports/financial-summary
   - Route has @roles_required("admin")
   - Returns 403 Forbidden
```

---

## Testing Checklist

- [ ] Login with admin account
- [ ] Login with staff account
- [ ] Attempt staff access to /reports (should get 403)
- [ ] Record product purchase, verify stock increases
- [ ] Record product sale, verify stock decreases
- [ ] Try to sell more than available stock (should fail)
- [ ] Record expense
- [ ] Check dashboard metrics
- [ ] Admin: Verify financial data visible
- [ ] Staff: Verify financial data NOT visible
- [ ] Admin: Create new user, verify works
- [ ] Admin: Delete user, verify works

---

## Performance Considerations

### Database Indexes
Currently has indexes on:
- `user.username` - O(log n) login lookup
- `product.sku` - Fast product search
- `stock_transaction.product_id` - Fast audit trails
- `stock_transaction.timestamp` - Time-range queries

### Query Optimization
```python
# For large datasets, use:
- .limit() and .offset() for pagination
- .join() for efficient relationships
- .filter() with indexed columns
```

### Caching Opportunities
```python
# Future optimization: Cache these
- Dashboard metrics (expire every 5 minutes)
- Product list (expire on product edit)
- Revenue/COGS calculations (expire on transaction)
```

---

*This architectural document should be reviewed with each major change to the application structure or database schema.*
