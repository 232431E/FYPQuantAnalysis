from flask import Blueprint

llm_routes_bp = Blueprint('llm', __name__, url_prefix='/llm')

# Add your LLM-related routes here
# Example:
# @llm_routes_bp.route('/generate')
# def generate_text():
#     return "LLM Generation"