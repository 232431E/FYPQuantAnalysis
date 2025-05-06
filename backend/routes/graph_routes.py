# backend/routes/graph_routes.py
from flask import Blueprint, jsonify, request
from backend.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta

graph_routes_bp = Blueprint('graph', __name__, url_prefix='/api/graph')

def fetch_graph_data(db: Session, company_id: int, timeframe: str):
    print(f"[DEBUG] fetch_graph_data: company_id={company_id}, timeframe={timeframe}")
    where_clause = ""
    date_column = "date"  # Assuming your daily data table has a 'date' column

    today = datetime.now()

    if timeframe == 'weekly':
        seven_days_ago = today - timedelta(days=7)
        where_clause = f"AND date >= '{seven_days_ago.strftime('%Y-%m-%d')}'"
    elif timeframe == 'monthly':
        thirty_days_ago = today - timedelta(days=30)  # Approximate month
        where_clause = f"AND date >= '{thirty_days_ago.strftime('%Y-%m-%d')}'"
    elif timeframe == 'yearly':
        one_year_ago = today - timedelta(days=365)
        where_clause = f"AND date >= '{one_year_ago.strftime('%Y-%m-%d')}'"
    elif timeframe == 'max':
        pass  # No date filtering for max
    else:
        print(f"[DEBUG] fetch_graph_data: Invalid timeframe: {timeframe}")
        return None, "Invalid timeframe"

    query = text(f"""
        SELECT date, close, volume
        FROM financial_data
        WHERE company_id = :company_id
        {where_clause}
        ORDER BY date ASC
    """)
    print(f"[DEBUG] fetch_graph_data: Executing query: {query} with company_id={company_id}")
    try:
        result = db.execute(query, params={'company_id': company_id}).fetchall()
        data = []
        for row in result:
            data_point = {
                'date': row[0],  # Assuming 'date' is the first column
                'close': row[1], # Assuming 'close' is the second column
                'volume': row[2] # Assuming 'volume' is the third column
            }
            data.append(data_point)
        print(f"[DEBUG] fetch_graph_data: Retrieved {len(data)} data points for {timeframe}")
        return data, None
    except Exception as e:
        error_message = f"Error executing query: {e}"
        print(f"[ERROR] fetch_graph_data: {error_message}")
        return None, error_message

@graph_routes_bp.route('/company/<int:company_id>/<string:timeframe>')
def get_company_graph_data(company_id, timeframe):
    print(f"[DEBUG] get_company_graph_data: company_id={company_id}, timeframe={timeframe}")
    db = get_db()
    data, error = fetch_graph_data(db, company_id, timeframe)
    db.close()
    if error:
        print(f"[DEBUG] get_company_graph_data: Returning error: {error}")
        return jsonify({'error': error}), 400
    print(f"[DEBUG] get_company_graph_data: Returning {len(data)} data points")
    return jsonify(data), 200