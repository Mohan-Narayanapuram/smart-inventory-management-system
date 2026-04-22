"""
Decorators Module: Role-based access control decorators

Provides decorators for protecting routes based on user roles:
- Admin: Full system access
- Staff: Limited access to inventory and expense features
"""

from functools import wraps
from flask import abort
from flask_login import current_user, login_required


def roles_required(*allowed_roles):
    """
    Decorator to enforce role-based access control.
    
    Usage:
        @routes_required("admin")
        def admin_only_view():
            ...
        
        @routes_required("admin", "staff")
        def both_can_access():
            ...
    
    Args:
        *allowed_roles: Variable length argument list of allowed roles
                       (e.g., 'admin', 'staff')
    
    Returns:
        Decorated function that checks user role before executing
        
    Behavior:
    - Requires user to be logged in (via @login_required)
    - Returns 403 Forbidden if user's role not in allowed_roles
    - Executes wrapped function if role check passes
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator
