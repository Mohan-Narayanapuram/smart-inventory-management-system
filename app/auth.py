from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from .models import User
from . import db
from .decorators import roles_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    """Root route: redirect to dashboard if authenticated, else to login"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    User login page.
    
    Required fields:
    - username: unique username
    - password: user's password
    
    On successful login, user is redirected to dashboard.
    On failure, error message is displayed.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required", "danger")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("dashboard.index"))

        flash("Invalid username or password", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout the current user"""
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/users")
@roles_required("admin")
def list_users():
    """
    Admin-only endpoint: List all users.
    
    Displays username, role, and creation date for each user.
    Admins can edit or delete users from this view.
    """
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("users/list.html", users=users)


@auth_bp.route("/users/create", methods=["GET", "POST"])
@roles_required("admin")
def create_user():
    """
    Admin-only endpoint: Create a new user.
    
    Required fields:
    - username: unique username (minimum 3 characters)
    - password: password (minimum 6 characters)
    - role: 'admin' or 'staff'
    
    On successful creation, admin is redirected to user list.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "staff")

        # Validation
        if not username or not password:
            flash("Username and password are required", "danger")
            return render_template("users/create.html")

        if len(username) < 3:
            flash("Username must be at least 3 characters", "warning")
            return render_template("users/create.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters", "warning")
            return render_template("users/create.html")

        if role not in ["admin", "staff"]:
            flash("Invalid role selected", "danger")
            return render_template("users/create.html")

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash(f"User '{username}' already exists", "warning")
            return render_template("users/create.html")

        # Create user
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash(f"User '{username}' created successfully as {role}", "success")
        return redirect(url_for("auth.list_users"))

    return render_template("users/create.html")


@auth_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@roles_required("admin")
def edit_user(user_id):
    """
    Admin-only endpoint: Edit an existing user.
    
    Can change:
    - Role: admin or staff
    - Password: optional, only if admin wants to reset it
    
    Cannot change:
    - Username: for audit trail integrity
    """
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        role = request.form.get("role", user.role)
        new_password = request.form.get("password", "").strip()

        # Validate role
        if role not in ["admin", "staff"]:
            flash("Invalid role selected", "danger")
            return render_template("users/edit.html", user=user)

        user.role = role

        # Update password if provided
        if new_password:
            if len(new_password) < 6:
                flash("Password must be at least 6 characters", "warning")
                return render_template("users/edit.html", user=user)
            user.set_password(new_password)
            flash(f"User password updated", "success")
        else:
            flash(f"User '{user.username}' role updated to {role}", "success")

        db.session.commit()
        return redirect(url_for("auth.list_users"))

    return render_template("users/edit.html", user=user)


@auth_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@roles_required("admin")
def delete_user(user_id):
    """
    Admin-only endpoint: Delete a user.
    
    Warning: This action deletes the user record.
    The user's transactions and expenses will remain for audit trail.
    """
    user = User.query.get_or_404(user_id)

    # Prevent deleting the last admin
    admin_count = User.query.filter_by(role="admin").count()
    if user.role == "admin" and admin_count == 1:
        flash("Cannot delete the last admin user", "danger")
        return redirect(url_for("auth.list_users"))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    flash(f"User '{username}' has been deleted", "success")
    return redirect(url_for("auth.list_users"))
