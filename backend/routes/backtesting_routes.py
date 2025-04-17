from flask import Blueprint

backtesting_routes_bp = Blueprint('backtesting', __name__, url_prefix='/backtesting')

# Add your backtesting-related routes here
# Example:
# @backtesting_routes_bp.route('/run', methods=['POST'])
# def run_backtest():
#     return "Backtest Running"