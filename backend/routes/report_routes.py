from flask import Blueprint

report_routes_bp = Blueprint('report', __name__, url_prefix='/report')

# Add your report-related routes here
# Example:
# @report_routes_bp.route('/')
# def reports_home():
#     return "Report Home"