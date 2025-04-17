from flask import Blueprint

visualisation_routes_bp = Blueprint('visualization', __name__, url_prefix='/visualization')

# Add your visualization-related routes here
# Example:
# @visualisation_routes_bp.route('/chart/<ticker>')
# def show_chart(ticker):
#     return f"Chart for {ticker}"