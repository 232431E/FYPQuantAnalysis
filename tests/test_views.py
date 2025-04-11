"""# tests/test_views.py
import unittest
from backend.database import db
from backend.models.data_model import FinancialData

class TestViews(unittest.TestCase):
    # tests/test_views.py
    def setUp(self):
        #Set up a test database session
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Insert test financial data
        company = Company(company_name="Test Company", ticker_symbol="TEST", exchange="NASDAQ", industry="Technology")
        db.session.add(company)
        db.session.commit()

        add_financial_data(
            company_id=company.company_id,
            date="2023-10-01",
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000000,
            roi=0.05,
            eps=2.5,
            pe_ratio=20.0,
            revenue=5000000.0,
            debt_to_equity=1.5,
            cash_flow=100000.0
        )

    def tearDown(self):
        #Clean up after each test
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_weekly_view(self):
        #Test the weekly_financial_data view
        result = db.session.execute(
            SELECT * FROM weekly_financial_data WHERE company_id = 1
        ).fetchone()
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result['avg_open'], 100.0)
        self.assertAlmostEqual(result['avg_close'], 102.0)
        self.assertEqual(result['total_volume'], 1000000)

if __name__ == '__main__':
    unittest.main()"""