import requests
import urllib.parse
import streamlit as st

# --- PASTE YOUR WOLFRAM|ALPHA APP ID HERE ---
APP_ID = "QPR44GJTHA" # Your App ID

def solve_with_wolfram(query_string: str):
    """
    Queries the Wolfram Alpha Full Results API directly using requests for robust error handling.
    """
    # Base URL for the Full Results API
    base_url = "http://api.wolframalpha.com/v2/query"
    
    # URL-encode the input string to handle special characters like +, ^, etc.
    encoded_input = urllib.parse.quote_plus(query_string)
    
    # Construct the full request URL
    request_url = f"{base_url}?appid={APP_ID}&input={encoded_input}&output=json"
    
    try:
        # Make the GET request
        response = requests.get(request_url)
        # Raise an exception for bad status codes (like 401 Unauthorized or 403 Forbidden)
        response.raise_for_status()
        
        data = response.json()
        
        query_result = data.get("queryresult", {})
        
        # Check if Wolfram|Alpha understood the query
        if not query_result.get("success", False):
            st.error("Wolfram|Alpha could not interpret the expression. Please check the OCR details and try writing more clearly.")
            return None
            
        return query_result.get("pods",)

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 403:
            st.error("Wolfram|Alpha API Error: Forbidden. Please check if your App ID is correct and active.")
        else:
            st.error(f"An HTTP Error occurred: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        st.error(f"A network error occurred: {req_err}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None
