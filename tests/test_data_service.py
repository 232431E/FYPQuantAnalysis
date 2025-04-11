# tests/test_database.py
import unittest
from backend.app import create_app, db
from backend.models.data_model import Company, FinancialData

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up the test app and database."""
        self.app = create_app(config_class='TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_company(self):
        """Test creating a company record."""
        company = Company(company_name="Test Company", ticker_symbol="TEST", exchange="NASDAQ", industry="Technology")
        db.session.add(company)
        db.session.commit()
        self.assertEqual(company.company_name, "Test Company")

    def test_add_financial_data(self):
        """Test adding financial data for a company."""
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

        result = FinancialData.query.filter_by(company_id=company.company_id).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.close, 102.0)

if __name__ == '__main__':
    unittest.main()