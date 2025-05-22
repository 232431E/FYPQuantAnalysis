# backend/services/llm_service.py
import json
import re 
import os
import logging
import requests
import google.generativeai as genai
from typing import List, Dict, Optional, Any

logging.basicConfig(level=logging.INFO)

#perplexity has not been updated yet & not in use
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

def analyze_news_sentiment_gemini(news_articles: List[Dict[str, Any]], prompt: Optional[str] = None, llm_model: str = 'gemini-2.0-flash-lite') -> Dict[str, Optional[Any]]:
    """Analyzes news sentiment using Google Gemini API, with optional custom prompt."""
    print("[DEBUG - Service - Gemini] analyze_news_sentiment_gemini called with news articles count:", len(news_articles),"with articles", (news_articles), "prompt provided:", prompt is not None)
    empty_report = {
        "overall_news_summary": "No news or analysis available.",
        "brief_overall_sentiment": "Neutral (Score: 50/100) - No data for specific sentiment.",
        "reasons_for_sentiment": "No news articles were provided or analyzable.",
        "market_outlook": "Insufficient information for a market outlook.",
        "detailed_explanation": "No data to elaborate on market outlook.",
        "key_offerings": [],
        "financial_dates": []
    }
    if not news_articles:
        print("[DEBUG - Service - Gemini] No news articles to analyze, returning empty report.")
        return empty_report
    google_api_key = os.environ.get('GOOGLE_API_KEY')
    if not google_api_key:
        logging.warning("GOOGLE_API_KEY environment variable not set.")
        print("[DEBUG - Service - Gemini] GOOGLE_API_KEY not configured.")
        return {**empty_report, "overall_news_summary": "API Key Error", "brief_overall_sentiment": "Error (Score: 0/100) - API key missing.", "reasons_for_sentiment": "Gemini API key not configured.", "market_outlook": "Cannot analyze.", "detailed_explanation": "Cannot analyze.", "key_offerings": [],  "financial_dates": []}

    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel(llm_model)

    if prompt:
        print("[DEBUG - Service - Gemini] Custom prompt provided.")
        try:
            print("[DEBUG - Service - Gemini] Calling Gemini API with custom prompt...")
            response = model.generate_content([prompt])
            response.resolve()
            print("[DEBUG - Service - Gemini] Gemini API Response:", response.text if response and response.parts and response.parts[0].text else response)
            if response and response.parts and response.parts[0].text:
                raw_llm_response_text = response.parts[0].text.strip()
                print("[DEBUG - Service - Gemini] Gemini API Raw Response Text:", raw_llm_response_text)
                # Use regex to find the JSON block
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_llm_response_text, re.DOTALL)
                if json_match:
                    json_string = json_match.group(1)
                    print("[DEBUG - Service - Gemini] Extracted JSON string with regex:", json_string)
                else:
                    # Fallback if no ```json block is found, try to parse the whole response
                    # This handles cases where Gemini directly returns JSON without the code block markers
                    json_string = raw_llm_response_text
                    print("[DEBUG - Service - Gemini] No JSON block markers found, attempting to parse full response as JSON.")
                try:
                    llm_output = json.loads(json_string)
                    print("[DEBUG - Service - Gemini] Parsed JSON response:", llm_output)
                    # We already have the overall sentiment in the JSON response
                    brief_sentiment = llm_output.get("brief_overall_sentiment", "Neutral")
                    return {
                        "overall_news_summary": llm_output.get("overall_news_summary", empty_report["overall_news_summary"]),
                        "brief_overall_sentiment": llm_output.get("brief_overall_sentiment", empty_report["brief_overall_sentiment"]),
                        "reasons_for_sentiment": llm_output.get("reasons_for_sentiment", empty_report["reasons_for_sentiment"]),
                        "market_outlook": llm_output.get("market_outlook", empty_report["market_outlook"]),
                        "detailed_explanation": llm_output.get("detailed_explanation", empty_report["detailed_explanation"]),
                        "key_offerings": llm_output.get("key_offerings", empty_report["key_offerings"]),
                        "financial_dates": llm_output.get("financial_dates", empty_report["financial_dates"]) 
                    }
                except json.JSONDecodeError as e:
                    logging.warning(f"Could not decode Gemini response as JSON: {json_string[:200]}... Error: {e}") # Log truncated string for brevity
                    print(f"[DEBUG - Service - Gemini] Could not decode JSON response: {json_string[:200]}... Error: {e}")
                    # Fallback to text-based inference if JSON decoding fails
                    brief_sentiment = _infer_sentiment(raw_llm_response_text) # Use raw_llm_response_text for inference
                    return {
                        "overall_news_summary": "JSON Decoding Error",
                        "brief_overall_sentiment": f"{brief_sentiment} (Score: 0/100) - JSON format error.",
                        "reasons_for_sentiment": f"Failed to parse detailed sentiment due to JSON error: {e}. Raw response: {raw_llm_response_text}",
                        "market_outlook": "Analysis failed due to decoding error.",
                        "detailed_explanation": "Please check LLM output format. Expected JSON.",
                        "key_offerings": [],
                        "financial_dates": []
                    }
            else:
                logging.warning("Gemini API response was empty or did not contain text for custom prompt.")
                print("[DEBUG - Service - Gemini] Gemini API response empty for custom prompt.")
                return empty_report # Return empty report with new structure
        except Exception as e:
            logging.error(f"Error calling Gemini API with custom prompt: {e}", exc_info=True)
            print(f"[DEBUG - Service - Gemini] Error calling Gemini API with custom prompt: {e}")
            # Return error report with new structure
            return {**empty_report, "overall_news_summary": "API Call Error", "brief_overall_sentiment": f"Error (Score: 0/100) - API call failed.", "reasons_for_sentiment": f"Error during Gemini API call: {e}", "market_outlook": "Cannot analyze.", "detailed_explanation": "Cannot analyze.", "key_offerings": []}
    else:
        # Default prompt scenario (should not be used by the /sentiment route, as it uses a custom prompt)
        print("[DEBUG - Service - Gemini] No custom prompt provided. Using default (THIS SHOULD NOT HAPPEN FOR /sentiment ROUTE).")
        # This branch of code is likely not hit if your `llm_routes.py` always sends a custom prompt.
        # But for completeness, we update its return structure.
        text_to_analyze = " ".join([f"{article.get('title', '')}. {article.get('description', '')}" for article in news_articles])
        default_prompt = f"Analyze the sentiment of the following news: '{text_to_analyze}'. Provide a brief overall summary (e.g., positive, negative, mixed, neutral)."
        try:
            response = model.generate_content([default_prompt])
            response.resolve()
            raw_sentiment_response = response.text if response and response.parts and response.parts[0].text else None
            print("[DEBUG - Service - Gemini] Gemini API Response (default):", raw_sentiment_response)
            if raw_sentiment_response:
                llm_response_text = raw_sentiment_response.strip()
                brief_sentiment = _infer_sentiment(llm_response_text)
                return {
                    "overall_news_summary": "Default analysis based on provided news snippets.",
                    "brief_overall_sentiment": f"{brief_sentiment} (Score: 50/100) - Default brief analysis.",
                    "reasons_for_sentiment": f"No detailed reasons as a custom prompt was not used. Raw response: {raw_sentiment_response}",
                    "market_outlook": "Market outlook not detailed with default prompt.",
                    "detailed_explanation": "No detailed explanation with default prompt.",
                    "key_offerings": [], 
                    "financial_dates": []
                }
            else:
                logging.warning("Gemini API response was empty for default prompt.")
                return empty_report
        except Exception as e:
            logging.error(f"Error calling Gemini API with default prompt: {e}", exc_info=True)
            return {**empty_report, "overall_news_summary": "API Call Error (Default)", "brief_overall_sentiment": f"Error (Score: 0/100) - Default API call failed.", "reasons_for_sentiment": f"Error during Gemini API call: {e}", "market_outlook": "Cannot analyze.", "detailed_explanation": "Cannot analyze.", "key_offerings": [], "financial_dates": []}

def analyze_news_sentiment(news_articles: List[Dict[str, Any]], llm_provider: str = 'default', llm_model: str = 'default', prompt: Optional[str] = None) -> Dict[str, Optional[Any]]:
    """Main function to analyze news sentiment, choosing the LLM provider and handling optional prompt."""
    print(f"[DEBUG - Service] analyze_news_sentiment called with provider: {llm_provider}, model: {llm_model}, prompt provided: {prompt is not None}")
    
    # Define a consistent empty report structure for all initial fallbacks
    empty_report = {
        "overall_news_summary": "No news or analysis available.",
        "brief_overall_sentiment": "Neutral (Score: 50/100) - No data for specific sentiment.",
        "reasons_for_sentiment": "No news articles were provided or analyzable.",
        "market_outlook": "Insufficient information for a market outlook.",
        "detailed_explanation": "No data to elaborate on market outlook.",
        "key_offerings": []
    }

    if llm_provider.lower() == 'perplexity':
        # You would need to update analyze_news_sentiment_perplexity to return the new structure too
        # For now, let's assume it returns a compatible dict or handle its output
        print("[DEBUG - Service] Using Perplexity provider (ensure its output matches the new structure).")
        return analyze_news_sentiment_perplexity(news_articles, llm_model) # Placeholder, adjust this function
    elif llm_provider.lower() == 'gemini':
        print("[DEBUG - Service] Using Gemini provider.")
        return analyze_news_sentiment_gemini(news_articles, prompt, llm_model)
    else:
        logging.warning(f"LLM provider '{llm_provider}' not recognized. Using placeholder sentiment analysis.")
        # Return a consistent error report with the new structure
        return {**empty_report, 
                "overall_news_summary": "Provider Not Recognized",
                "brief_overall_sentiment": "Neutral (Score: 0/100) - Provider not recognized.", 
                "reasons_for_sentiment": "Specify 'perplexity' or 'gemini' as llm_provider.",
                "market_outlook": "Cannot analyze.",
                "detailed_explanation": "Cannot analyze.",
                "key_offerings": []}
    
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