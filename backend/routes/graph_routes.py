# backend/routes/graph_routes.py
from flask import Blueprint, jsonify, request
from backend.database import get_db
from sqlalchemy.orm import Session

graph_routes_bp = Blueprint('graph', __name__, url_prefix='/api/graph')

def fetch_graph_data(db: Session, company_id: int, timeframe: str):
    if timeframe == 'weekly':
        view_name = 'weekly_financial_data'
        date_column = 'week'
    elif timeframe == 'monthly':
        view_name = 'monthly_financial_data'
        date_column = 'month'
    elif timeframe == 'yearly':
        view_name = 'yearly_financial_data'
        date_column = 'year'
    else:
        return None, "Invalid timeframe"

    query = f"""
        SELECT {date_column} AS date, avg_close AS close, total_volume AS volume
        FROM {view_name}
        WHERE company_id = :company_id
        ORDER BY {date_column} ASC
    """
    result = db.execute(query, {'company_id': company_id}).fetchall()
    data = [dict(row) for row in result]
    return data, None

@graph_routes_bp.route('/company/<int:company_id>/<string:timeframe>')
def get_company_graph_data(company_id, timeframe):
    db = get_db()
    data, error = fetch_graph_data(db, company_id, timeframe)
    db.close()
    if error:
        return jsonify({'error': error}), 400
    return jsonify(data), 200