# backend/services/llm_service.py
import os
import logging
import requests
import google.generativeai as genai
from typing import List, Dict, Optional, Any

logging.basicConfig(level=logging.INFO)

def analyze_news_sentiment_perplexity(news_articles: List[Dict[str, Any]], llm_model: str = 'pplx-7b-chat') -> Dict[str, Optional[str]]:
    """Analyzes news sentiment using Perplexity API."""
    print("analyze_news_sentiment_perplexity called with:", news_articles)
    if not news_articles:
        return {"brief": "No news to analyze.", "sentiment": "Neutral"}

    perplexity_api_key = os.environ.get('PERPLEXITY_API_KEY')
    if not perplexity_api_key:
        logging.warning("PERPLEXITY_API_KEY environment variable not set.")
        return {"brief": "Perplexity API key not configured.", "sentiment": "Neutral"}

    text_to_analyze = " ".join([f"{article.get('title', '')}. {article.get('description', '')}" for article in news_articles])
    perplexity_endpoint = 'https://api.perplexity.ai/chat/completions'
    headers = {
        'Authorization': f'Bearer {perplexity_api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': llm_model,
        'messages': [
            {'role': 'user', 'content': f"Analyze the sentiment of the following news: '{text_to_analyze}'. Provide a brief overall summary (e.g., positive, negative, mixed, neutral)."}
        ]
    }
    try:
        response = requests.post(perplexity_endpoint, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        if result and result.get('choices') and result['choices'][0].get('message'):
            sentiment_summary = result['choices'][0]['message']['content'].strip()
            overall_sentiment = _infer_sentiment(sentiment_summary)
            return {"brief": sentiment_summary, "sentiment": overall_sentiment}
        else:
            logging.warning(f"Perplexity API response issue: {result}")
            return {"brief": "Error in Perplexity API response.", "sentiment": "Neutral"}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Perplexity API: {e}")
        return {"brief": f"Perplexity API error: {e}", "sentiment": "Neutral"}

def analyze_news_sentiment_gemini(news_articles: List[Dict[str, Any]], llm_model: str = 'gemini-pro') -> Dict[str, Optional[str]]:
    """Analyzes news sentiment using Google Gemini API."""
    print("analyze_news_sentiment_gemini called with:", news_articles)
    if not news_articles:
        return {"brief": "No news to analyze.", "sentiment": "Neutral"}

    google_api_key = os.environ.get('GOOGLE_API_KEY')
    if not google_api_key:
        logging.warning("GOOGLE_API_KEY environment variable not set.")
        return {"brief": "Gemini API key not configured.", "sentiment": "Neutral"}

    text_to_analyze = " ".join([f"{article.get('title', '')}. {article.get('description', '')}" for article in news_articles])
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel(llm_model)
    prompt = f"Analyze the sentiment of the following news: '{text_to_analyze}'. Provide a brief overall summary (e.g., positive, negative, mixed, neutral)."

    try:
        response = model.generate_content([prompt])
        if response and response.parts:
            sentiment_summary = response.parts[0].text.strip()
            overall_sentiment = _infer_sentiment(sentiment_summary)
            return {"brief": sentiment_summary, "sentiment": overall_sentiment}
        else:
            logging.warning("Gemini API response was empty or did not contain text.")
            return {"brief": "Gemini API response was empty or did not contain text.", "sentiment": "Neutral"}
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return {"brief": f"Gemini API error: {e}", "sentiment": "Neutral"}

def analyze_news_sentiment(news_articles: List[Dict[str, Any]], llm_provider: str = 'default', llm_model: str = 'default') -> Dict[str, Optional[str]]:
    """Main function to analyze news sentiment, choosing the LLM provider."""
    if llm_provider.lower() == 'perplexity':
        return analyze_news_sentiment_perplexity(news_articles, llm_model)
    elif llm_provider.lower() == 'gemini':
        return analyze_news_sentiment_gemini(news_articles, llm_model)
    else:
        logging.warning(f"LLM provider '{llm_provider}' not recognized. Using placeholder sentiment analysis.")
        return {"brief": "Placeholder sentiment analysis: Specify 'perplexity' or 'gemini' as llm_provider.", "sentiment": "Neutral"}

def _infer_sentiment(text: str) -> str:
    lower_text = text.lower()
    if 'mixed' in lower_text or 'uncertain' in lower_text or 'cautious' in lower_text:
        return "Mixed"
    elif any(word in lower_text for word in ['positive', 'bullish', 'optimistic', 'strong', 'good']):
        return "Positive"
    elif any(word in lower_text for word in ['negative', 'bearish', 'pessimistic', 'weak', 'bad', 'loss']):
        return "Negative"
    else:
        return "Neutral"