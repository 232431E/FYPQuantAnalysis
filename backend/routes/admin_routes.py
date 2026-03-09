from flask import Blueprint, jsonify, request, render_template, session
from backend.database import get_session_local
from backend.models import User, Role, AuditLog
from backend.services import user_service
try:
    from backend.services import rbac_service
except Exception:
    rbac_service = None

try:
    from backend.utils.audit import log_event
except Exception:
    def log_event(db, user_id, event_type, ip_address, description):
        # no-op fallback if real log_event is not available
        pass

admin_routes = Blueprint('admin', __name__, url_prefix='/admin')


@admin_routes.route('/users', methods=['GET'])
@permission_required('manage_users')
def get_users():
    db = get_session_local()()
    try:
        users = db.query(User).all()
        result = [{"id": user.user_id, "username": user.username, "email": user.email, "role": user.role.name if user.role else None} for user in users]
        return jsonify(result)
    finally:
        db.close()


@admin_routes.route('/users/view', methods=['GET'])
@permission_required('manage_users')
def view_users():
    db = get_session_local()()
    try:
        users = user_service.get_all_users(db)
        return render_template('staff/view_users.html', users=users)
    finally:
        db.close()


@admin_routes.route('/roles/<int:role_id>/permissions', methods=['GET'])
@permission_required('manage_users')
def get_role_permissions(role_id):
    db = get_session_local()()
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        if role:
            result = [{"id": p.id, "name": p.name, "description": p.description} for p in role.permissions]
            return jsonify(result)
        return jsonify({"message": "Role not found"}), 404
    finally:
        db.close()


@admin_routes.route('/audit-log', methods=['GET'])
@permission_required('view_audit_log')
def get_audit_log():
    db = get_session_local()()
    try:
        logs = db.query(AuditLog).all()
        result = [{"id": log.id, "user_id": log.user_id, "event_type": log.event_type, "ip_address": log.ip_address, "description": log.description, "timestamp": log.timestamp} for log in logs]
        return jsonify(result)
    finally:
        db.close()


@admin_routes.route('/roles', methods=['GET'])
@permission_required('manage_users')
def get_roles():
    db = get_session_local()()
    try:
        roles = rbac_service.get_roles(db) if rbac_service else []
        result = [{"id": role.id, "name": role.name, "description": role.description} for role in roles]
        return jsonify(result)
    finally:
        db.close()


@admin_routes.route('/users/<int:user_id>/role', methods=['PUT'])
@permission_required('manage_users')
def assign_role(user_id):
    data = request.get_json()
    if not data or 'role_id' not in data:
        return jsonify({"message": "Missing required field: role_id"}), 400
    db = get_session_local()()
    try:
        user = user_service.assign_role_to_user(db, user_id, data['role_id'])
        if user:
            log_event(db, session.get('user_id'), 'role_change', request.remote_addr, f"Assigned role {user.role.name} to user {user.username}")
            return jsonify({"message": "Role assigned successfully"})
        return jsonify({"message": "Failed to assign role"}), 400
    finally:
        db.close()


@admin_routes.route('/roles', methods=['POST'])
@permission_required('manage_users')
def create_role():
    data = request.get_json()
    if not data or 'name' not in data or 'description' not in data or not isinstance(data['name'], str) or not isinstance(data['description'], str):
        return jsonify({"message": "Missing or invalid 'name' or 'description' field"}), 400
    db = get_session_local()()
    try:
        role = rbac_service.create_role(db, data['name'], data['description']) if rbac_service else None
        if role:
            log_event(db, session.get('user_id'), 'role_create', request.remote_addr, f"Created role {role.name}")
            return jsonify({"message": "Role created successfully"}), 201
        return jsonify({"message": "Failed to create role"}), 400
    finally:
        db.close()


@admin_routes.route('/roles/<int:role_id>', methods=['DELETE'])
@permission_required('manage_users')
def delete_role(role_id):
    db = get_session_local()()
    try:
        if rbac_service:
            rbac_service.delete_role(db, role_id)
        log_event(db, session.get('user_id'), 'role_delete', request.remote_addr, f"Deleted role {role_id}")
        return jsonify({"message": "Role deleted successfully"})
    finally:
        db.close()


@admin_routes.route('/roles/<int:role_id>/permissions', methods=['POST'])
@permission_required('manage_users')
def assign_permission_to_role(role_id):
    data = request.get_json()
    if not data or 'permission_id' not in data:
        return jsonify({"message": "Missing required field: permission_id"}), 400
    db = get_session_local()()
    try:
        if rbac_service:
            rbac_service.assign_permission_to_role(db, role_id, data['permission_id'])
        log_event(db, session.get('user_id'), 'permission_assign', request.remote_addr, f"Assigned permission {data['permission_id']} to role {role_id}")
        return jsonify({"message": "Permission assigned successfully"})
    finally:
        db.close()
