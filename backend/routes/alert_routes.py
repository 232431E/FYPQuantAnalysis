from flask import Blueprint

alert_routes_bp = Blueprint('alert', __name__, url_prefix='/alert')

# Add your alert-related routes here
# Example:
# @alert_routes_bp.route('/create', methods=['POST'])
# def create_alert():
#     return "Alert Created"