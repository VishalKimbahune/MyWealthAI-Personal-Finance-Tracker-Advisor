from flask import Blueprint, request, jsonify
from app.models import User, Transaction
import jwt
import os

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

def get_user_from_token():
    """Extract user from JWT token"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return User.objects(id=payload['user_id']).first()
    except:
        return None

def require_admin(f):
    """Decorator to require admin privileges"""
    def decorated_function(*args, **kwargs):
        user = get_user_from_token()
        if not user or not user.is_admin:
            return jsonify({'error': 'Unauthorized: admin access required'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    """List all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        paginated = User.objects.paginate(page=page, per_page=per_page)

        return jsonify({
            'users': [u.to_dict() for u in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>', methods=['GET'])
@require_admin
def get_user_details(user_id):
    """Get detailed user information (admin only)"""
    try:
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        tx_count = Transaction.objects(user_id=user_id).count()

        expenses = Transaction.objects(user_id=user_id, type='expense').sum('amount')
        income = Transaction.objects(user_id=user_id, type='income').sum('amount')

        return jsonify({
            'user': user.to_dict(),
            'transaction_count': tx_count,
            'total_expense': round(float(expenses), 2),
            'total_income': round(float(income), 2),
            'balance': round(float(income - expenses), 2)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@require_admin
def reset_user_password(user_id):
    """Reset a user's password to a new one (admin only)"""
    try:
        data = request.get_json()
        new_password = data.get('password')

        if not new_password:
            return jsonify({'error': 'Password is required'}), 400

        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.set_password(new_password)
        user.save()

        return jsonify({
            'message': f'Password reset for {user.email}',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@require_admin
def toggle_admin(user_id):
    """Toggle admin status for a user (admin only)"""
    try:
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.is_admin = not user.is_admin
        user.save()

        return jsonify({
            'message': f'Admin status set to {user.is_admin} for {user.email}',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """Delete a user and all their data (admin only)"""
    try:
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        email = user.email
        # Delete user's transactions first
        Transaction.objects(user_id=user_id).delete()
        user.delete()

        return jsonify({'message': f'User {email} deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@require_admin
def admin_stats():
    """Get admin dashboard statistics"""
    try:
        total_users = User.objects.count()
        admin_count = User.objects(is_admin=True).count()
        total_transactions = Transaction.objects.count()

        total_expenses = Transaction.objects(type='expense').sum('amount')
        total_income = Transaction.objects(type='income').sum('amount')

        return jsonify({
            'total_users': total_users,
            'admin_count': admin_count,
            'total_transactions': total_transactions,
            'total_expenses': round(float(total_expenses), 2),
            'total_income': round(float(total_income), 2),
            'system_balance': round(float(total_income - total_expenses), 2)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
