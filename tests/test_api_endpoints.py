"""# tests/test_api_endpoints.py
import unittest
from backend.app import create_app, db
from backend.models.data_model import Company, FinancialData
import json

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        #Set up the test app and database.
        self.app = create_app(config_class='TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Add test data
        company = Company(company_name="Test Company", ticker_symbol="TEST", exchange="NASDAQ", industry="Technology")
        db.session.add(company)
        db.session.commit()

        financial_data = FinancialData(
            company_id=company.company_id,
            date="2023-10-01",
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000000
        )
        db.session.add(financial_data)
        db.session.commit()

    def tearDown(self):
        #Clean up after each test.
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_company_financials(self):
        #Test the /api/companies/<company_id>/financials endpoint
        response = self.client.get('/api/companies/1/financials?period=daily')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        if data:
            self.assertIn('date', data[0])
            self.assertEqual(data[0]['close'], 102.0)

if __name__ == '__main__':
    unittest.main()"""