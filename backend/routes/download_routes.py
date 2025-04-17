from flask import Blueprint

download_routes_bp = Blueprint('download', __name__, url_prefix='/download')

# Add your download-related routes here
# Example:
# @download_routes_bp.route('/data/<ticker>')
# def download_data(ticker):
#     return f"Download data for {ticker}"