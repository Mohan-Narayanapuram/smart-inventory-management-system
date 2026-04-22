# Smart Inventory Management System - API Routes Reference

## 🗺️ Complete Route Map

### Authentication Routes

| Method | Route | Access | Function | Description |
|--------|-------|--------|----------|-------------|
| GET/POST | `/login` | Public | `auth.login()` | User login page |
| GET | `/logout` | Authenticated | `auth.logout()` | User logout |
| GET | `/` | Any | `auth.index()` | Root redirect to dashboard |

---

### Dashboard Routes

| Method | Route | Access | Function | Description |
|--------|-------|--------|----------|-------------|
| GET | `/dashboard/` | Authenticated | `dashboard.index()` | Main dashboard with metrics |

**Metrics Shown**:
- All users: total_products, total_stock_units
- Admins only: revenue, cogs, expenses, profit

---

### Product Routes (Inventory Management)

| Method | Route | Access | Function | Description |
|--------|-------|--------|----------|-------------|
| GET | `/products/` | Authenticated | `products.list_products()` | List all products |
| GET/POST | `/products/create` | Admin + Staff | `products.create_product()` | Create new product |
| GET/POST | `/products/<id>/edit` | Admin + Staff | `products.edit_product()` | Edit product details |
| POST | `/products/<id>/delete` | Admin Only | `products.delete_product()` | Delete product |
| GET/POST | `/products/<id>/stock` | Admin + Staff | `products.update_stock()` | Record purchase/sale |

**Notes**:
- `<id>` is the product ID (integer)
- Stock updates recorded in `stock_transaction` table
- Admin only for deletion (staff can create/edit)

---

### Expense Routes

| Method | Route | Access | Function | Description |
|--------|-------|--------|----------|-------------|
| GET | `/expenses/` | Authenticated | `expenses.list_expenses()` | View all expenses |
| GET/POST | `/expenses/create` | Admin + Staff | `expenses.create_expense()` | Record new expense |

**Notes**:
- Both users can record expenses
- Admin can see expenses in financial summaries
- Staff cannot see summary/analysis

---

### Financial Reports Routes (Admin Only)

| Method | Route | Access | Function | Description |
|--------|-------|--------|----------|-------------|
| GET | `/reports/financial-summary` | Admin Only | `reports.financial_summary()` | Financial overview |
| GET | `/reports/transaction-details` | Admin Only | `reports.transaction_details()` | Transaction audit trail |
| GET | `/reports/expense-summary` | Admin Only | `reports.expense_summary()` | Expense analysis |

**Data Displayed**:
- **financial-summary**: Revenue, COGS, Expenses, Profit, Margins
- **transaction-details**: All purchase/sale transactions with dates and users
- **expense-summary**: Expenses by category, totals, averages

---

### User Management Routes (Admin Only)

| Method | Route | Access | Function | Description |
|--------|-------|--------|----------|-------------|
| GET | `/users` | Admin Only | `auth.list_users()` | List all users |
| GET/POST | `/users/create` | Admin Only | `auth.create_user()` | Create new user |
| GET/POST | `/users/<id>/edit` | Admin Only | `auth.edit_user()` | Edit user role/password |
| POST | `/users/<id>/delete` | Admin Only | `auth.delete_user()` | Delete user |

**Notes**:
- `<id>` is the user ID (integer)
- Cannot delete the last admin user
- Cannot change username (audit trail)

---

## 🔐 Access Control Matrix

### Public Routes
- `/login` (GET/POST)
- `/` (redirects to login if not authenticated)

### Authenticated Routes (Any logged-in user)
- `/dashboard/`
- `/products/`
- `/expenses/`

### Admin + Staff Routes
- `/products/create` (GET/POST)
- `/products/<id>/edit` (GET/POST)
- `/products/<id>/stock` (GET/POST)
- `/expenses/create` (GET/POST)
- `/logout` (GET)

### Admin Only Routes
- `/products/<id>/delete` (POST)
- `/reports/financial-summary` (GET)
- `/reports/transaction-details` (GET)
- `/reports/expense-summary` (GET)
- `/users` (GET)
- `/users/create` (GET/POST)
- `/users/<id>/edit` (GET/POST)
- `/users/<id>/delete` (POST)

---

## 📊 Request/Response Examples

### Example 1: Create Product

**Request**:
```
POST /products/create
Content-Type: application/x-www-form-urlencoded

name=Timber Board&sku=TB-001&description=Premium timber&unit_price=100.00&cost_price=60.00&stock=50
```

**Response** (Success):
```html
302 Found
Location: /products/
Flash: "Product 'Timber Board' created successfully"
```

**Response** (Failure - duplicate SKU):
```html
200 OK
Flash: "SKU 'TB-001' already in use"
(Form re-rendered with error)
```

### Example 2: Record Stock Transaction

**Request**:
```
POST /products/1/stock
Content-Type: application/x-www-form-urlencoded

txn_type=sale&quantity=5&unit_price=100.00
```

**Response** (Success):
```html
302 Found
Location: /products/
Flash: "Sale of 5 units recorded. New stock: 45"
```

**Response** (Failure - insufficient stock):
```html
302 Found
Location: /products/1/stock
Flash: "Insufficient stock. Available: 45, Requested: 50"
```

### Example 3: View Financial Report

**Request**:
```
GET /reports/financial-summary
```

**Response** (Admin):
```html
200 OK
(Reports page with financial data displayed)
```

**Response** (Staff):
```html
403 Forbidden
(Access denied - admin only)
```

---

## 🛠️ Common Tasks & Routes

### Task: View Inventory
```
GET /products/
```

### Task: Add New Product
```
GET /products/create          (show form)
POST /products/create         (submit form)
```

### Task: Sell Items
```
GET /products/                (view products)
GET /products/<id>/stock      (show transaction form)
POST /products/<id>/stock     (submit sale - txn_type=sale)
```

### Task: Buy Inventory
```
GET /products/<id>/stock      (show transaction form)
POST /products/<id>/stock     (submit purchase - txn_type=purchase)
```

### Task: Record Expense
```
GET /expenses/create          (show form)
POST /expenses/create         (submit)
```

### Task: View Financial Data (Admin)
```
GET /reports/financial-summary
GET /reports/transaction-details
GET /reports/expense-summary
```

### Task: Create Staff User (Admin)
```
GET /users/create             (show form)
POST /users/create            (submit)
```

---

## 🔄 URL Parameters

### Product ID
```
/products/<product_id>/edit
/products/<product_id>/delete
/products/<product_id>/stock

Example: /products/5/stock (edit product ID 5)
```

### User ID
```
/users/<user_id>/edit
/users/<user_id>/delete

Example: /users/3/edit (edit user ID 3)
```

---

## 📱 Form Fields

### Create Product Form
```
Required:
- name (string, max 150 chars)
- unit_price (decimal, >= 0)
- cost_price (decimal, >= 0)

Optional:
- sku (string, max 80, unique)
- description (text)
- stock (integer, >= 0)
```

### Create Expense Form
```
Required:
- amount (decimal, > 0)

Optional:
- description (text)
- date (datetime-local)
```

### Stock Transaction Form
```
Required:
- txn_type (purchase | sale)
- quantity (integer, > 0)
- unit_price (decimal, >= 0)
```

### Create User Form (Admin)
```
Required:
- username (string, min 3, max 80, unique)
- password (string, min 6)
- role (admin | staff)
```

### Edit User Form (Admin)
```
Optional:
- password (string, min 6, only if changing)
- role (admin | staff)

Fixed:
- username (cannot change)
```

---

## 🎯 Status Codes

| Code | Meaning | Common Routes |
|------|---------|---------------|
| 200 | OK | GET requests, form display |
| 302 | Redirect | POST success, login redirect |
| 403 | Forbidden | Admin routes accessed by staff |
| 404 | Not Found | Invalid product/user ID |
| 400 | Bad Request | Invalid form data |

---

## 🔍 Query Examples

### List All Products
```
GET /products/
Response: HTML page with all products
```

### Edit Specific Product
```
GET /products/5/edit
Response: Form pre-filled with product data
```

### Check Stock Levels
```
GET /products/
Response: Inventory list with current stock
```

### View All Expenses
```
GET /expenses/
Response: Expense list with dates, amounts, descriptions
```

### Admin: View All Users
```
GET /users
Response: User list with roles and creation dates
```

### Admin: Financial Summary
```
GET /reports/financial-summary
Response: Revenue, COGS, Expenses, Profit calculations
```

---

## 🔐 Error Handling

### Missing Login
```
Request: GET /dashboard/
Response: 302 Redirect to /login
```

### Insufficient Permissions
```
Request: GET /reports/ (as staff)
Response: 403 Forbidden
```

### Invalid Product
```
Request: GET /products/999/edit (no product with ID 999)
Response: 404 Not Found
```

### Form Validation Error
```
Request: POST /products/create (missing name)
Response: 200 OK (form re-rendered with error message)
Flash: "Product name is required"
```

---

## 📌 Important Notes

1. **All routes require authentication** except login (`/login` and `/`)
2. **Admin-only routes** return 403 Forbidden if accessed by staff
3. **POST routes** redirect on success, re-render form on error
4. **Stock validation** prevents selling more than available
5. **User creation** only by admin, no public signup
6. **Financial data** completely hidden from staff users

---

## 🚀 Quick Navigation

**For Users**:
- Start at `/` → redirects to `/login` → login → `/dashboard/`

**For Inventory**:
- `/products/` → list
- `/products/create` → add new
- `/products/<id>/edit` → modify
- `/products/<id>/stock` → buy/sell

**For Expenses**:
- `/expenses/` → view
- `/expenses/create` → record

**For Admin**:
- `/users` → manage
- `/users/create` → add staff
- `/reports/financial-summary` → view finances

---

*See README.md and ARCHITECTURE.md for detailed documentation.*
