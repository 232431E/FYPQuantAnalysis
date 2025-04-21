# backend/tests/test_data_service_sentiment.py
import sys
import os

import requests

# Get the absolute path to the parent directory of 'backend'
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from backend.services import data_service
fetch_latest_news = data_service.fetch_latest_news

# Import everything else from llm_service
from backend.services import llm_service
analyze_news_sentiment = llm_service.analyze_news_sentiment
analyze_news_sentiment_perplexity = llm_service.analyze_news_sentiment_perplexity
analyze_news_sentiment_gemini = llm_service.analyze_news_sentiment_gemini
_infer_sentiment = llm_service._infer_sentiment

class TestNewsSentimentAnalysis(unittest.TestCase):

    def setUp(self):
        self.mock_news_articles_positive = [
            {"title": "Company Announces Record Profits", "description": "Shares soar after positive earnings report."},
            {"title": "New Product Launch a Success", "description": "Customer reviews are overwhelmingly positive."},
        ]
        self.mock_news_articles_negative = [
            {"title": "Stock Plummets on Unexpected Losses", "description": "Investors worried about company's future."},
            {"title": "Product Recall Issued Due to Safety Concerns", "description": "Company faces potential lawsuits."},
        ]
        self.mock_news_articles_neutral = [
            {"title": "Company to Hold Annual General Meeting", "description": "Shareholders will vote on key proposals."},
            {"title": "Analyst Issues Market Update", "description": "Provides overview of current economic conditions."},
        ]
        self.mock_news_articles_mixed = [
            {"title": "Company Reports Strong Growth but Warns of Future Challenges", "description": "Revenue up, but supply chain issues persist."},
            {"title": "New Acquisition Faces Regulatory Scrutiny but Promises Long-Term Benefits", "description": "Deal under review, potential for market expansion."},
        ]
        self.mock_news_articles_empty = []

    @patch('os.environ.get')
    @patch('requests.post')
    def test_analyze_news_sentiment_perplexity(self, mock_post, mock_environ_get):
        # Configure environment to use Perplexity
        mock_environ_get.side_effect = lambda key: "YOUR_PERPLEXITY_API_KEY" if key == 'PERPLEXITY_API_KEY' else None

        # Mock a positive Perplexity response with a paragraph
        mock_response_positive = MagicMock()
        mock_response_positive.json.return_value = {
            "choices": [{"message": {"content": "The company announced record profits today, leading to a very bullish outlook for the stock. Investors are optimistic about future performance."}}]
        }
        mock_response_positive.raise_for_status.return_value = None
        mock_post.return_value = mock_response_positive

        result_positive = analyze_news_sentiment_perplexity(self.mock_news_articles_positive, llm_model='pplx-7b-chat')
        self.assertEqual(result_positive['sentiment'], "Positive")

        # Mock a negative Perplexity response with a paragraph
        mock_response_negative = MagicMock()
        mock_response_negative.json.return_value = {
            "choices": [{"message": {"content": "Shares plummeted today following an unexpected announcement of significant losses. Analysts have expressed a bearish sentiment, and the company faces potential lawsuits."}}]
        }
        mock_response_negative.raise_for_status.return_value = None
        mock_post.return_value = mock_response_negative

        result_negative = analyze_news_sentiment_perplexity(self.mock_news_articles_negative, llm_model='pplx-7b-chat')
        self.assertEqual(result_negative['sentiment'], "Negative")

        # Mock a neutral Perplexity response with a paragraph
        mock_response_neutral = MagicMock()
        mock_response_neutral.json.return_value = {
            "choices": [{"message": {"content": "The company will hold its annual general meeting next week. Shareholders are expected to vote on several key proposals and hear updates from the management team."}}]
        }
        mock_response_neutral.raise_for_status.return_value = None
        mock_post.return_value = mock_response_neutral

        result_neutral = analyze_news_sentiment_perplexity(self.mock_news_articles_neutral, llm_model='pplx-7b-chat')
        self.assertEqual(result_neutral['sentiment'], "Neutral")

        # Mock a mixed Perplexity response with a paragraph
        mock_response_mixed = MagicMock()
        mock_response_mixed.json.return_value = {
            "choices": [{"message": {"content": "While the company reported strong revenue growth, they also cautioned about persistent supply chain issues in the coming quarters. This has led to a mixed reaction from investors."}}]
        }
        mock_response_mixed.raise_for_status.return_value = None
        mock_post.return_value = mock_response_mixed

        result_mixed = analyze_news_sentiment_perplexity(self.mock_news_articles_mixed, llm_model='pplx-7b-chat')
        self.assertEqual(result_mixed['sentiment'], "Mixed")

        # Test with empty news articles (direct call)
        result_empty = analyze_news_sentiment_perplexity([], llm_model='pplx-7b-chat')
        self.assertEqual(result_empty['brief'], "No news to analyze.")
        self.assertEqual(result_empty['sentiment'], "Neutral")

        # Test API key not configured
        mock_environ_get.side_effect = lambda key: None
        result_no_key = analyze_news_sentiment_perplexity(self.mock_news_articles_positive, llm_model='pplx-7b-chat')
        self.assertEqual(result_no_key['brief'], "Perplexity API key not configured.")
        self.assertEqual(result_no_key['sentiment'], "Neutral")

        # Test API error
        mock_environ_get.side_effect = lambda key: "YOUR_PERPLEXITY_API_KEY" if key == 'PERPLEXITY_API_KEY' else None
        mock_post.side_effect = requests.exceptions.RequestException("API error")
        result_error = analyze_news_sentiment_perplexity(self.mock_news_articles_positive, llm_model='pplx-7b-chat')
        self.assertEqual(result_error['brief'], "Perplexity API error: API error")
        self.assertEqual(result_error['sentiment'], "Neutral")

        # Test malformed API response
        mock_post.side_effect = None
        mock_response_malformed = MagicMock()
        mock_response_malformed.json.return_value = {}
        mock_response_malformed.raise_for_status.return_value = None
        mock_post.return_value = mock_response_malformed
        result_malformed = analyze_news_sentiment_perplexity(self.mock_news_articles_positive, llm_model='pplx-7b-chat')
        self.assertEqual(result_malformed['brief'], "Error in Perplexity API response.")
        self.assertEqual(result_malformed['sentiment'], "Neutral")

    @patch('os.environ.get')
    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_analyze_news_sentiment_gemini(self, mock_generate_content, mock_environ_get):
        # Configure environment to use Gemini
        mock_environ_get.side_effect = lambda key: "YOUR_GOOGLE_API_KEY" if key == 'GOOGLE_API_KEY' else None

        # Mock a positive Gemini response with a paragraph
        mock_response_positive = MagicMock()
        mock_response_positive.parts = [MagicMock(text="The market reacted positively to the news of the successful product launch. Analysts are optimistic about the company's future prospects and potential for further growth.")]
        mock_generate_content.return_value = mock_response_positive

        result_positive = analyze_news_sentiment_gemini(self.mock_news_articles_positive, llm_model='gemini-pro')
        self.assertEqual(result_positive['sentiment'], "Positive")

        # Mock a negative Gemini response with a paragraph
        mock_response_negative = MagicMock()
        mock_response_negative.parts = [MagicMock(text="Concerns are mounting as the company announced a significant product recall due to safety issues. This has created a negative sentiment among consumers and investors alike.")]
        mock_generate_content.return_value = mock_response_negative

        result_negative = analyze_news_sentiment_gemini(self.mock_news_articles_negative, llm_model='gemini-pro')
        self.assertEqual(result_negative['sentiment'], "Negative")

        # Mock a neutral Gemini response with a paragraph
        mock_response_neutral = MagicMock()
        mock_response_neutral.parts = [MagicMock(text="The company is scheduled to present at an upcoming industry conference. Details of their presentation agenda have been released to the public.")]
        mock_generate_content.return_value = mock_response_neutral

        result_neutral = analyze_news_sentiment_gemini(self.mock_news_articles_neutral, llm_model='gemini-pro')
        self.assertEqual(result_neutral['sentiment'], "Neutral")

        # Mock a mixed Gemini response with a paragraph
        mock_response_mixed = MagicMock()
        mock_response_mixed.parts = [MagicMock(text="While the latest earnings report showed a substantial increase in revenue, the company also cited potential headwinds related to global economic uncertainty, leading to a mixed outlook.")]
        mock_generate_content.return_value = mock_response_mixed

        result_mixed = analyze_news_sentiment_gemini(self.mock_news_articles_mixed, llm_model='gemini-pro')
        self.assertEqual(result_mixed['sentiment'], "Mixed")

        # Test with empty news articles (direct call)
        result_empty = analyze_news_sentiment_gemini([], llm_model='gemini-pro')
        self.assertEqual(result_empty['brief'], "No news to analyze.")
        self.assertEqual(result_empty['sentiment'], "Neutral")

        # Test API key not configured
        mock_environ_get.side_effect = lambda key: None
        result_no_key = analyze_news_sentiment_gemini(self.mock_news_articles_positive, llm_model='gemini-pro')
        self.assertEqual(result_no_key['brief'], "Gemini API key not configured.")
        self.assertEqual(result_no_key['sentiment'], "Neutral")

        # Test API error
        mock_environ_get.side_effect = lambda key: "YOUR_GOOGLE_API_KEY" if key == 'GOOGLE_API_KEY' else None
        mock_generate_content.side_effect = Exception("API error")
        result_error = analyze_news_sentiment_gemini(self.mock_news_articles_positive, llm_model='gemini-pro')
        self.assertEqual(result_error['brief'], "Gemini API error: API error")
        self.assertEqual(result_error['sentiment'], "Neutral")

        # Test empty API response
        mock_generate_content.side_effect = None
        mock_generate_content.return_value = MagicMock(parts=[])
        result_no_response = analyze_news_sentiment_gemini(self.mock_news_articles_positive, llm_model='gemini-pro')
        self.assertEqual(result_no_response['brief'], "Gemini API response was empty or did not contain text.")
        self.assertEqual(result_no_response['sentiment'], "Neutral")
        
    @patch('os.environ.get')
    def test_analyze_news_sentiment_placeholder(self, mock_environ_get):
        # Configure environment so neither Perplexity nor Gemini API keys are set
        mock_environ_get.return_value = None

        result = analyze_news_sentiment(self.mock_news_articles_positive)
        self.assertEqual(result['sentiment'], "Neutral")
        self.assertEqual(result['brief'], "Placeholder sentiment analysis: Specify 'perplexity' or 'gemini' as llm_provider.")

    @patch('os.environ.get')
    @patch('requests.post')
    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_analyze_news_sentiment_main_function(self, mock_generate_content, mock_post, mock_environ_get):
        # Test calling Perplexity through the main function
        mock_environ_get.side_effect = lambda key: "YOUR_PERPLEXITY_API_KEY" if key == 'PERPLEXITY_API_KEY' else None
        mock_response_perplexity = MagicMock()
        mock_response_perplexity.json.return_value = {"choices": [{"message": {"content": "Positive vibes!"}}]}
        mock_response_perplexity.raise_for_status.return_value = None
        mock_post.return_value = mock_response_perplexity
        result_perplexity = analyze_news_sentiment(self.mock_news_articles_positive, llm_provider='perplexity')
        self.assertEqual(result_perplexity['sentiment'], "Positive")

        # Test calling Gemini through the main function
        mock_environ_get.side_effect = lambda key: "YOUR_GOOGLE_API_KEY" if key == 'GOOGLE_API_KEY' else None
        mock_response_gemini = MagicMock()
        mock_response_gemini.parts = [MagicMock(text="Very positive news.")]
        mock_generate_content.return_value = mock_response_gemini
        result_gemini = analyze_news_sentiment(self.mock_news_articles_positive, llm_provider='gemini')
        self.assertEqual(result_gemini['sentiment'], "Positive")

        # Test with an unrecognized provider
        mock_environ_get.return_value = None
        result_unrecognized = analyze_news_sentiment(self.mock_news_articles_positive, llm_provider='openai')
        self.assertEqual(result_unrecognized['sentiment'], "Neutral")
        self.assertEqual(result_unrecognized['brief'], "Placeholder sentiment analysis: Specify 'perplexity' or 'gemini' as llm_provider.")

if __name__ == '__main__':
    unittest.main()