# Smart Inventory Management System

## Overview

The Smart Inventory Management System is a web-based application designed for medium-scale businesses such as timber, steel, and cement dealers. It provides an integrated platform to manage inventory, track expenses, monitor sales, and calculate profits efficiently.

This project was developed as part of the Software Engineering and Product Management (SEPM) course and is also designed as a deployable solution for a real timber business.

---

## Key Features

### Inventory Management

* Add, edit, and delete products
* Real-time stock tracking
* Dual pricing system (buying and selling price)

### Stock Management

* Record purchase and sale transactions
* Automatic stock updates
* Prevent overselling with validation
* Full audit trail of stock changes

### Expense Management

* Record daily business expenses
* Maintain expense history
* Track expense entries with user attribution

### Financial Management

* Revenue, cost, and profit calculation
* Profit and loss tracking
* Expense aggregation
* Admin-only financial visibility

### Role-Based Access Control

**Admin**

* Full system access
* Financial reports and profit insights
* User management

**Staff**

* Inventory and stock operations
* Expense recording
* Restricted from financial data

---

## Technology Stack

* Backend: Python Flask
* Database: SQLite (SQLAlchemy ORM)
* Frontend: HTML, CSS, Jinja2
* Authentication: Session-based
* Architecture: Modular Flask Blueprints

---

## Project Structure

```
SEPM/
├── app/
│   ├── auth.py
│   ├── dashboard.py
│   ├── products.py
│   ├── expenses.py
│   ├── reports.py
│   ├── models.py
│   ├── decorators.py
│   ├── templates/
│   └── static/
├── run.py
├── config.py
├── init_db.py
├── requirements.txt
```

---

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-inventory-management-system.git
cd smart-inventory-management-system
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python init_db.py
```

### 5. Run Application

```bash
python run.py
```

---

## Default Credentials

* Username: admin
* Password: admin123

---

## SEPM Alignment

This project follows core Software Engineering and Product Management principles:

* Real-world problem identification (timber business use case)
* Role-based system design
* Modular architecture using Flask Blueprints
* Clear separation of concerns
* Agile-inspired development approach
* Scalable and maintainable design

---

## Future Enhancements

* Cloud deployment (AWS / Render)
* PostgreSQL integration
* Mobile application support
* GST and invoice generation
* Advanced analytics and forecasting

---

## Authors

* D. Pujith Ram Reddy
* Illa Varun Anjith
* Mohan Narayanapuram 

---

## License

This project is developed for academic and practical use.
