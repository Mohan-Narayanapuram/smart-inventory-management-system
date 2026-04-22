"""
Seed Script: Populates the database with realistic sample data
Run with: python seed_data.py
"""

from app import create_app, db
from app.models import User, Product, StockTransaction, Expense
from datetime import datetime, timedelta
import random

app = create_app()

def seed():
    with app.app_context():
        print("🗑️  Clearing existing data...")
        StockTransaction.query.delete()
        Expense.query.delete()
        Product.query.delete()
        User.query.filter(User.username != 'admin').delete()
        db.session.commit()

        # ── USERS ──────────────────────────────────────────────
        print("👥 Creating users...")

        # Check if admin exists, create if not
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)

        employees = []
        employee_data = [
            ('john_smith',   'staff'),
            ('sarah_jones',  'staff'),
            ('mike_wilson',  'staff'),
            ('emily_brown',  'staff'),
            ('raj_kumar',    'staff'),
            ('priya_das',    'staff'),
        ]
        for uname, role in employee_data:
            u = User.query.filter_by(username=uname).first()
            if not u:
                u = User(username=uname, role=role)
                u.set_password('employee123')
                db.session.add(u)
            employees.append(u)

        db.session.flush()  # get IDs

        admin = User.query.filter_by(username='admin').first()
        employees = User.query.filter_by(role='staff').all()

        # ── PRODUCTS ───────────────────────────────────────────
        print("📦 Creating products...")

        products_data = [
            # (name, sku, description, unit_price, cost_price, stock)
            # Cement
            ("Cement 53 Grade",    "CEM-53",  "High strength OPC 53 grade cement",      380,  320,  450),
            ("Cement 43 Grade",    "CEM-43",  "Standard OPC 43 grade cement",            350,  300,  320),
            ("White Cement",       "CEM-WH",  "Decorative white cement for finishing",   520,  440,   80),
            ("Rapid Hardening Cement","CEM-RH","Sets quickly for urgent work",           420,  360,  110),
            # Steel
            ("Steel Rods 8mm",     "STL-8",   "TMT steel rods 8mm diameter",             65,   55, 1200),
            ("Steel Rods 12mm",    "STL-12",  "TMT steel rods 12mm diameter",            68,   58,  800),
            ("Steel Rods 16mm",    "STL-16",  "TMT steel rods 16mm diameter",            72,   61,  600),
            ("Steel Rods 20mm",    "STL-20",  "TMT steel rods 20mm diameter",            78,   66,  400),
            ("Steel Plates 6mm",   "STL-P6",  "Mild steel flat plates 6mm",             145,  120,  180),
            ("Steel Angles 50x50", "STL-A50", "Equal angles 50x50x5mm",                 110,   92,  260),
            # Timber
            ("Teak Wood Plank",    "TIM-TK",  "Premium teak wood, 1 inch thick",        1450, 1200,  150),
            ("Pine Wood Plank",    "TIM-PN",  "Softwood pine planks for shuttering",    1000,  850,  200),
            ("Plywood 18mm",       "TIM-PL18","Commercial grade plywood 8x4 ft",         980,  820,  120),
            ("Plywood 12mm",       "TIM-PL12","Commercial grade plywood 8x4 ft",         760,  640,  140),
            ("Blockboard 19mm",    "TIM-BB",  "Blockboard for furniture and doors",      870,  730,   90),
            # Bricks & Blocks
            ("Red Clay Bricks",    "BRK-RD",  "Standard red clay bricks per 1000",     7500, 6200,   45),
            ("Fly Ash Bricks",     "BRK-FA",  "Eco-friendly fly ash bricks per 1000",  5800, 4800,   60),
            ("AAC Blocks 200mm",   "BLK-AAC", "Autoclaved aerated concrete blocks",     4200, 3500,   35),
            # Sand & Aggregates
            ("River Sand (ton)",   "SND-RV",  "Clean river sand for construction",      1800, 1500,   80),
            ("M-Sand (ton)",       "SND-MS",  "Manufactured sand, well graded",         1400, 1150,  100),
            ("20mm Aggregate (ton)","AGG-20", "Coarse aggregate 20mm size",             1600, 1320,   70),
            ("10mm Aggregate (ton)","AGG-10", "Fine aggregate 10mm size",               1700, 1400,   65),
            # Paints
            ("Asian Paints Exterior 20L","PNT-EXT","Weather resistant exterior paint", 4800, 4000,   55),
            ("Asian Paints Interior 20L","PNT-INT","Premium interior emulsion",         3600, 3000,   70),
            ("Primer 20L",         "PNT-PR",  "Wall primer for better adhesion",        1800, 1500,   90),
            # Hardware
            ("GI Pipes 1 inch",    "HRD-GP1", "Galvanized iron pipes 1 inch dia",        320,  265,  200),
            ("CPVC Pipes 1 inch",  "HRD-CP1", "CPVC pipes for hot/cold water",           280,  230,  240),
            ("Door Hinges (pair)", "HRD-DH",  "Heavy duty door hinges stainless",        180,  145,  500),
            ("Binding Wire (kg)",  "HRD-BW",  "Annealed black binding wire",              85,   70,  350),
            ("Nails Assorted (kg)","HRD-NL",  "Mixed size iron nails",                    95,   78,  300),
        ]

        products = []
        for name, sku, desc, up, cp, stock in products_data:
            p = Product(
                name=name, sku=sku, description=desc,
                unit_price=up, cost_price=cp, stock=stock
            )
            db.session.add(p)
            products.append(p)

        db.session.flush()
        products = Product.query.all()

        # ── STOCK TRANSACTIONS ─────────────────────────────────
        print("🔄 Creating stock transactions...")

        all_users = [admin] + employees
        now = datetime.utcnow()

        transactions = []

        # Generate ~120 transactions over the last 90 days
        for i in range(120):
            product = random.choice(products)
            days_ago = random.randint(0, 90)
            txn_time = now - timedelta(days=days_ago, hours=random.randint(0, 12))
            user = random.choice(all_users)

            # 60% sales, 40% purchases
            txn_type = 'sale' if random.random() < 0.6 else 'purchase'

            if txn_type == 'sale':
                qty = random.randint(1, 30)
                price = float(product.unit_price)
            else:
                qty = random.randint(10, 100)
                price = float(product.cost_price)

            change = qty if txn_type == 'purchase' else -qty

            txn = StockTransaction(
                product_id=product.id,
                change=change,
                txn_type=txn_type,
                quantity=qty,
                unit_price=price,
                timestamp=txn_time,
                user_id=user.id,
            )
            db.session.add(txn)

        # ── EXPENSES ──────────────────────────────────────────
        print("💸 Creating expenses...")

        expense_data = [
            # (description, amount_range, frequency_per_month)
            ("Transportation",  (3000,  8000),  6),
            ("Salaries",        (40000, 55000), 1),
            ("Utilities",       (2000,  4000),  2),
            ("Maintenance",     (1500,  5000),  3),
            ("Office Supplies", (500,   2000),  2),
            ("Security",        (3000,  4000),  1),
            ("Loading/Unloading",(1000, 3000),  4),
            ("Vehicle Fuel",    (2000,  5000),  4),
            ("Printing",        (300,   800),   2),
            ("Miscellaneous",   (500,   2500),  3),
        ]

        for months_ago in range(0, 4):  # last 4 months
            for desc, (min_amt, max_amt), freq in expense_data:
                for _ in range(freq):
                    exp_date = now - timedelta(days=months_ago * 30 + random.randint(0, 28))
                    amount = round(random.uniform(min_amt, max_amt), 2)
                    exp = Expense(
                        amount=amount,
                        description=desc,
                        date=exp_date,
                        created_by=random.choice(all_users).id,
                    )
                    db.session.add(exp)

        db.session.commit()

        # ── SUMMARY ────────────────────────────────────────────
        print("\n✅ Seed complete!")
        print(f"   Users:        {User.query.count()}")
        print(f"   Products:     {Product.query.count()}")
        print(f"   Transactions: {StockTransaction.query.count()}")
        print(f"   Expenses:     {Expense.query.count()}")
        print("\n🔑 Login credentials:")
        print("   Admin    → username: admin       password: admin123")
        print("   Employee → username: john_smith  password: employee123")

if __name__ == '__main__':
    seed()