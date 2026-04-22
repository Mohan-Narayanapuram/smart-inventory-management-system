# Smart Inventory Management System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Navigate to Project Directory
```bash
cd /Users/mohannarayanapuram/Desktop/SEPM
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python3 init_db.py
```

You should see:
```
============================================================
Smart Inventory Management System - Database Initialization
============================================================

1. Creating database tables...
   ✓ Database tables created successfully

2. Checking for default admin user...
   Creating default admin user...
   ✓ Default admin user created successfully
     Username: admin
     Password: admin123

...
```

### Step 5: Start the Application
```bash
python3 run.py
```

You should see:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 6: Open in Browser
Go to: **http://localhost:5000**

---

## 📝 First Login

Use these credentials:
- **Username**: admin
- **Password**: admin123

---

## ✅ Verify Everything Works

After login, you should see:
1. Dashboard with metrics
2. Navigation menu at top
3. Links to Inventory, Expenses, Reports, Users

Try these actions:
1. Click **Inventory** → **Add New Product**
2. Create a test product (e.g., "Test Timber", Price: $100, Cost: $60)
3. Click **Expenses** → **Record New Expense**
4. Record a test expense ($500 for utilities)
5. Click **Dashboard** to see updated metrics

---

## 🔐 Change Default Password

1. Click **Users** in navigation
2. Click **Edit** next to admin user
3. Enter new password and click **Update User**

---

## 📚 Next Steps

- Read **README.md** for comprehensive documentation
- Review **Database Schema** section in README.md
- Explore **API Routes** documentation
- Check **Usage Examples** for common tasks

---

## 🆘 Troubleshooting

### Port Already in Use
If port 5000 is busy:
```bash
python3 run.py --port 5001
```

### Database Issues
Delete `sepm.db` and run:
```bash
python3 init_db.py
```

### Module Not Found
Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

---

## 📂 Project Structure Overview

```
SEPM/
├── app/                 # Application code
│   ├── models.py       # Database models (User, Product, etc.)
│   ├── auth.py         # Login and user management
│   ├── products.py     # Inventory management
│   ├── expenses.py     # Expense tracking
│   ├── dashboard.py    # Main dashboard
│   ├── reports.py      # Financial reports
│   └── templates/      # HTML files
├── config.py           # Settings
├── run.py             # Start application here
├── init_db.py         # Initialize database
├── requirements.txt   # Python packages
└── README.md          # Full documentation
```

---

## 💡 Tips

- **For Development**: Run with `python3 run.py` (debug mode enabled)
- **For Production**: See deployment section in README.md
- **Create Users**: Only Admin can create new users
- **View Reports**: Only Admin can access Reports section
- **Password Security**: Minimum 6 characters, stored with hashing

---

## 📞 Support

See **README.md** for comprehensive documentation on:
- Database schema
- API routes
- Financial calculations
- Security considerations
- Deployment guide

---

Happy managing! 🎉
