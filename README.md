# Smart Inventory Management System

A professional-grade, production-ready Flask-based inventory management system designed for timber businesses and similar enterprises. Built with role-based access control, comprehensive financial reporting, and a clean user interface.

## Project Overview

### Tech Stack
- **Backend**: Python Flask 2.3+
- **Frontend**: HTML5, CSS3, Jinja2 Templates
- **Database**: SQLite (design supports easy migration to PostgreSQL/MySQL)
- **Authentication**: Flask-Login (session-based)
- **ORM**: SQLAlchemy
- **Security**: Werkzeug password hashing, CSRF protection

### Key Features

#### 1. Role-Based Access Control (RBAC)
Two distinct user roles with enforced permissions:

**Admin (Business Owner)**
- Full system access
- Create, edit, delete products
- Manage user accounts
- View comprehensive financial reports
- Record and summarize expenses
- Access profit/loss calculations
- View transaction audit trails

**Staff (Employees)**
- Create and edit products
- Update inventory (purchases/sales)
- Record expenses
- View inventory and expense lists
- **Cannot** see financial data or reports
- **Cannot** manage users

#### 2. Inventory Management
- Complete product catalog with SKU tracking
- Dual pricing model:
  - **Unit Price**: Sale price (revenue calculation)
  - **Cost Price**: Purchase cost (COGS calculation)
- Real-time stock level tracking
- Purchase and sale transactions

#### 3. Financial Management
- **Revenue Tracking**: Automatic calculation from sales
- **COGS Calculation**: Cost of goods sold per transaction
- **Expense Tracking**: Categorized operating expenses
- **Profit/Loss Calculation**: Revenue - COGS - Expenses
- **Financial Reports**:
  - Summary dashboard with key metrics
  - Transaction detail audit trail
  - Expense breakdown and analysis
  - Profit margin calculations

#### 4. Audit Trail
- Complete transaction history for all inventory movements
- User attribution for all changes
- Timestamp tracking
- Expense recording with creator information

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone/Download Project

```bash
cd /path/to/project
```

### Step 2: Create Virtual Environment

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
# Create a Python shell
python3

# Then in Python shell:
from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()

# Exit Python shell
exit()
```

### Step 5: Create Initial Admin User

```bash
python3

# In Python shell:
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')  # Change this in production!
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    else:
        print("Admin user already exists")

exit()
```

### Step 6: Run the Application

```bash
python3 run.py
```

The application will be available at `http://localhost:5000`

**Default Login:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important**: Change the default password immediately in production!

---

## Project Structure

```
SEPM/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── auth.py                  # Authentication & user management
│   ├── dashboard.py             # Main dashboard with metrics
│   ├── products.py              # Inventory management
│   ├── expenses.py              # Expense tracking
│   ├── reports.py               # Financial reports (admin-only)
│   ├── models.py                # SQLAlchemy database models
│   ├── decorators.py            # Role-based access control decorators
│   ├── templates/               # HTML templates
│   │   ├── base.html            # Base template with navigation
│   │   ├── login.html           # Login page
│   │   ├── dashboard.html       # Dashboard
│   │   ├── reports.html         # Financial summary
│   │   ├── transaction_details.html
│   │   ├── expense_summary.html
│   │   ├── products/
│   │   │   ├── list.html        # Product inventory list
│   │   │   ├── form.html        # Create/edit product form
│   │   │   └── stock.html       # Stock transaction form
│   │   ├── expenses/
│   │   │   ├── list.html        # Expense list
│   │   │   └── form.html        # Record expense form
│   │   └── users/
│   │       ├── list.html        # User list (admin only)
│   │       ├── create.html      # Create user form (admin only)
│   │       └── edit.html        # Edit user form (admin only)
│   └── static/
│       └── css/
│           └── style.css        # Main stylesheet
├── config.py                    # Application configuration
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── sepm.db                      # SQLite database (auto-created)
└── README.md                    # This file
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE user (
  id INTEGER PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  password_hash VARCHAR(128) NOT NULL,
  role VARCHAR(20) NOT NULL,  -- 'admin' or 'staff'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Products Table
```sql
CREATE TABLE product (
  id INTEGER PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  sku VARCHAR(80) UNIQUE,
  description TEXT,
  unit_price NUMERIC(12,2) DEFAULT 0.0,    -- Sale price
  cost_price NUMERIC(12,2) DEFAULT 0.0,    -- Purchase cost
  stock INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Stock Transactions Table
```sql
CREATE TABLE stock_transaction (
  id INTEGER PRIMARY KEY,
  product_id INTEGER NOT NULL,
  change INTEGER NOT NULL,
  txn_type VARCHAR(20) NOT NULL,  -- 'purchase' or 'sale'
  quantity INTEGER NOT NULL,
  unit_price NUMERIC(12,2) NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (product_id) REFERENCES product(id),
  FOREIGN KEY (user_id) REFERENCES user(id)
);
```

### Expenses Table
```sql
CREATE TABLE expense (
  id INTEGER PRIMARY KEY,
  amount NUMERIC(12,2) NOT NULL,
  description TEXT,
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_by INTEGER NOT NULL,
  FOREIGN KEY (created_by) REFERENCES user(id)
);
```

---

## Financial Calculations

### Revenue
```
Revenue = SUM(quantity * unit_price) for all SALE transactions
```

### Cost of Goods Sold (COGS)
```
COGS = SUM(quantity * product.cost_price) for all SALE transactions
```

### Gross Profit
```
Gross Profit = Revenue - COGS
```

### Net Profit
```
Net Profit = Revenue - COGS - Operating Expenses
```

### Gross Margin %
```
Gross Margin % = ((Revenue - COGS) / Revenue) * 100
```

### Net Profit Margin %
```
Net Profit Margin % = (Net Profit / Revenue) * 100
```

---

## API Routes

### Authentication
- `GET/POST /login` - User login
- `GET /logout` - User logout
- `GET /` - Root redirect to dashboard

### Dashboard
- `GET /dashboard/` - Main dashboard with metrics

### Products (Inventory)
- `GET /products/` - List all products
- `GET/POST /products/create` - Create new product
- `GET/POST /products/<id>/edit` - Edit product
- `POST /products/<id>/delete` - Delete product (admin only)
- `GET/POST /products/<id>/stock` - Record stock transaction

### Expenses
- `GET /expenses/` - List all expenses
- `GET/POST /expenses/create` - Record new expense

### Reports (Admin Only)
- `GET /reports/financial-summary` - Financial overview
- `GET /reports/transaction-details` - Detailed transaction audit trail
- `GET /reports/expense-summary` - Expense breakdown and analysis

### User Management (Admin Only)
- `GET /users` - List all users
- `GET/POST /users/create` - Create new user
- `GET/POST /users/<id>/edit` - Edit user role/password
- `POST /users/<id>/delete` - Delete user

---

## Usage Examples

### 1. Creating a Product

1. Login as Admin or Staff
2. Navigate to **Inventory** → **Add New Product**
3. Fill in:
   - Product Name (required)
   - SKU (optional, must be unique)
   - Unit Price: $50 (what customers pay)
   - Cost Price: $30 (what you paid)
   - Initial Stock: 100 units
4. Click "Create Product"

### 2. Recording a Sale

1. Navigate to **Inventory** → Click product name
2. Click **Update Stock**
3. Select **Sale (Decrease Stock)**
4. Enter:
   - Quantity: 5 units
   - Sale Price: $50 (will be recorded)
5. Submit
- System calculates:
  - Revenue: 5 × $50 = $250
  - COGS: 5 × $30 = $150
  - Gross Profit: $100

### 3. Recording an Expense

1. Navigate to **Expenses** → **Record New Expense**
2. Fill in:
   - Amount: $500
   - Description: "Monthly rent"
   - Date: (auto-filled)
3. Submit
- This amount is subtracted from profit calculations

### 4. Viewing Financial Reports (Admin Only)

1. Login as Admin
2. Navigate to **Reports**
3. View:
   - Revenue, COGS, Expenses, Profit
   - Profit margins
   - Total units sold
   - Detailed transaction audit trail

---

## Security Considerations

### Implemented Security Measures
1. **Password Hashing**: Werkzeug password hashing (PBKDF2)
2. **Session Management**: Flask-Login with secure cookies
3. **CSRF Protection**: Built-in Flask protection (enable if needed)
4. **Role-Based Access Control**: Enforced at route level
5. **Audit Trail**: All transactions recorded with timestamps and user info
6. **SQL Injection Prevention**: SQLAlchemy parameterized queries

### Production Deployment Checklist
- [ ] Change `SECRET_KEY` in `config.py` or set `SECRET_KEY` environment variable
- [ ] Set `SQLALCHEMY_TRACK_MODIFICATIONS = False`
- [ ] Use PostgreSQL or MySQL instead of SQLite
- [ ] Enable HTTPS/SSL
- [ ] Set `SESSION_COOKIE_SECURE = True` for HTTPS only
- [ ] Use environment variables for sensitive data
- [ ] Set up proper logging
- [ ] Regular database backups
- [ ] Implement rate limiting on login
- [ ] Use strong password requirements

---

## Deployment Guide

### Option 1: Heroku

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DATABASE_URL="postgresql://..."

# Deploy
git push heroku main

# Create database
heroku run python3 << EOF
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    db.create_all()
    admin = User(username='admin', role='admin')
    admin.set_password('change-this')
    db.session.add(admin)
    db.session.commit()
EOF
```

### Option 2: AWS EC2

```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# Clone project
git clone your-repo

# Create virtual environment and install
cd project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure Nginx as reverse proxy (see Nginx config guide)

# Use Gunicorn as WSGI server
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:8000 run:app
```

### Option 3: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

---

## Performance Optimization

### For Large Datasets
1. Add database indexes (done for `username`, `sku`, `product_id`, `created_at`)
2. Implement pagination for product/expense lists
3. Add caching for dashboard metrics
4. Use connection pooling for database

### Current Performance
- **Small business** (< 10,000 products, < 100,000 transactions): SQLite sufficient
- **Medium business**: Consider PostgreSQL
- **Large enterprise**: PostgreSQL + Redis caching

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution**: 
```bash
pip install -r requirements.txt
```

### Issue: "database.db is locked"
**Solution**: SQLite file is being accessed by another process. For production, migrate to PostgreSQL.

### Issue: "Login redirects to blank page"
**Solution**: Clear browser cookies or use incognito mode

### Issue: Staff can see financial data
**Solution**: Check that `current_user.role == 'admin'` is enforced in dashboard.html template

---

## Future Enhancements

### Sprint 2 Improvements
- [ ] Advanced product filtering and search
- [ ] Batch upload products via CSV
- [ ] Product variants (sizes, colors)
- [ ] Inventory alerts for low stock

### Sprint 3 Enhancements
- [ ] Budget tracking and forecasting
- [ ] Multi-currency support
- [ ] Recurring expense templates
- [ ] Detailed profit center analysis

### Sprint 4+ Features
- [ ] Mobile app (React Native)
- [ ] API for third-party integrations
- [ ] Advanced analytics and dashboards
- [ ] Integration with accounting software (QuickBooks)
- [ ] Barcode/QR code scanning
- [ ] Multi-location support
- [ ] Supplier management

---

## Contributing

For team development:

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Commit: `git commit -m "Add feature description"`
4. Push: `git push origin feature/your-feature`
5. Create pull request for review

---

## License

This project is proprietary and confidential. Intended for use by authorized team members only.

---

## Support & Documentation

### Getting Help
- Review the [Usage Examples](#usage-examples) section
- Check database schema documentation
- Review inline code comments (extensively documented)

### Key Files to Understand
- `app/models.py`: Database structure and relationships
- `app/decorators.py`: Role-based access control logic
- `app/dashboard.py`: Financial calculation logic
- `config.py`: Configuration and settings

---

## Project Information

**Created**: January 2025
**Framework**: Flask 2.3+
**Database**: SQLite (production-ready with migration path)
**Team**: SEPM Course Project

**Agile Sprints**:
- Sprint 1: Authentication & Roles ✓
- Sprint 2: Product & Stock Management ✓
- Sprint 3: Expense & Finance Module ✓
- Sprint 4: Dashboard & Reports ✓

---

*For questions or issues, contact the development team.*
