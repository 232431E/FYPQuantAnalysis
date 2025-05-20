# backend/services/llm_service.py
import json
import re 
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

def analyze_news_sentiment_gemini(news_articles: List[Dict[str, Any]], prompt: Optional[str] = None, llm_model: str = 'gemini-2.0-flash-lite') -> Dict[str, Optional[Any]]:
    """Analyzes news sentiment using Google Gemini API, with optional custom prompt."""
    print("[DEBUG - Service - Gemini] analyze_news_sentiment_gemini called with:", news_articles, "prompt:", prompt)
    if not news_articles:
        print("[DEBUG - Service - Gemini] No news articles to analyze.")
        return {"brief_overall_sentiment": "Neutral", "market_outlook": "No news to analyze.", "detailed_explanation": "No news available.", "detailed_sentiment": "No news available."}

    google_api_key = os.environ.get('GOOGLE_API_KEY')
    if not google_api_key:
        logging.warning("GOOGLE_API_KEY environment variable not set.")
        print("[DEBUG - Service - Gemini] GOOGLE_API_KEY not configured.")
        return {"error": "Gemini API key not configured."}

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
                        "overall_news_summary": llm_output.get("overall_news_summary"),
                        "brief_overall_sentiment": llm_output.get("brief_overall_sentiment"),
                        "detailed_sentiment": llm_output.get("brief_overall_sentiment"), # Still using brief as detailed here for now
                        "market_outlook": llm_output.get("market_outlook"),
                        "detailed_explanation": llm_output.get("detailed_explanation")
                    }
                except json.JSONDecodeError as e:
                    logging.warning(f"Could not decode Gemini response as JSON: {json_string[:200]}... Error: {e}") # Log truncated string for brevity
                    print(f"[DEBUG - Service - Gemini] Could not decode JSON response: {json_string[:200]}... Error: {e}")
                    # Fallback to text-based inference if JSON decoding fails
                    brief_sentiment = _infer_sentiment(raw_llm_response_text) # Use raw_llm_response_text for inference
                    return {
                        "brief_overall_sentiment": brief_sentiment,
                        "market_outlook": "Analysis failed due to decoding error.",
                        "detailed_explanation": f"Could not decode JSON response. Raw: {raw_llm_response_text}",
                        "detailed_sentiment": f"Error during analysis: {e}"
                    }
            else:
                logging.warning("Gemini API response was empty or did not contain text for custom prompt.")
                print("[DEBUG - Service - Gemini] Gemini API response empty for custom prompt.")
                return {"brief_overall_sentiment": "Neutral", "market_outlook": "Empty response from LLM.", "detailed_explanation": "Empty response from LLM.", "detailed_sentiment": "Empty response from LLM."}
        except Exception as e:
            logging.error(f"Error calling Gemini API with custom prompt: {e}")
            print(f"[DEBUG - Service - Gemini] Error calling Gemini API with custom prompt: {e}")
            return {"error": str(e)}
    else:
        print("[DEBUG - Service - Gemini] No custom prompt provided. Using default.")
        text_to_analyze = " ".join([f"{article.get('title', '')}. {article.get('description', '')}" for article in news_articles])
        default_prompt = f"Analyze the sentiment of the following news: '{text_to_analyze}'. Provide a brief overall summary (e.g., positive, negative, mixed, neutral)."
        try:
            print("[DEBUG - Service - Gemini] Calling Gemini API with default prompt...")
            response = model.generate_content([default_prompt])
            response.resolve()
            raw_sentiment_response = response.text if response and response.parts and response.parts[0].text else None # Capture the raw text
            print("[DEBUG - Service - Gemini] Gemini API Response (default):", raw_sentiment_response)
            if raw_sentiment_response:
                llm_response_text = raw_sentiment_response.strip()
                brief_sentiment = _infer_sentiment(llm_response_text)
                return {
                    "overall_news_summary": "based on provided news",
                    "brief_overall_sentiment": brief_sentiment,
                    "detailed_sentiment": raw_sentiment_response, # Include the detailed sentiment breakdown
                    "market_outlook": "Market outlook will be based on the detailed report.",
                    "detailed_explanation": f"Overall sentiment derived from the news: {llm_response_text}"
                }
            else:
                logging.warning("Gemini API response was empty or did not contain text for default prompt.")
                print("[DEBUG - Service - Gemini] Gemini API response empty for default prompt.")
                return {"brief_overall_sentiment": "Neutral", "market_outlook": "Empty response from LLM.", "detailed_explanation": "Empty response from LLM.", "detailed_sentiment": "Empty response from LLM."}
        except Exception as e:
            logging.error(f"Error calling Gemini API with default prompt: {e}")
            print(f"[DEBUG - Service - Gemini] Error calling Gemini API with default prompt: {e}")
            return {"error": str(e)}

def analyze_news_sentiment(news_articles: List[Dict[str, Any]], llm_provider: str = 'default', llm_model: str = 'default', prompt: Optional[str] = None) -> Dict[str, Optional[Any]]:
    """Main function to analyze news sentiment, choosing the LLM provider and handling optional prompt."""
    print(f"[DEBUG - Service] analyze_news_sentiment called with provider: {llm_provider}, model: {llm_model}, prompt provided: {prompt is not None}")
    if llm_provider.lower() == 'perplexity':
        return analyze_news_sentiment_perplexity(news_articles, llm_model)
    elif llm_provider.lower() == 'gemini':
        return analyze_news_sentiment_gemini(news_articles, prompt, llm_model)
    else:
        logging.warning(f"LLM provider '{llm_provider}' not recognized. Using placeholder sentiment analysis.")
        return {"brief_overall_sentiment": "Neutral", "market_outlook": "Provider not specified.", "detailed_explanation": "Specify 'perplexity' or 'gemini' as llm_provider.", "detailed_sentiment": "Provider not specified."}

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