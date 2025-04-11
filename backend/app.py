from flask import Flask, render_template, session
from backend.routes.data_routes import data_routes_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

app.register_blueprint(data_routes_bp)

@app.route('/dashboard')
def dashboard():
    # For testing, let's assume a company ID is in the session
    session['username'] = 'TestUser'
    session['selected_company_id'] = 1  # Replace with actual logic to get selected company
    return render_template('user/dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)