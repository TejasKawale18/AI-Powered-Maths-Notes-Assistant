from google.cloud import vision
from google.api_core.client_options import ClientOptions
from PIL import Image
import io
import streamlit as st

# --- PASTE YOUR API KEY HERE ---
# This key is now correctly defined.
API_KEY = "AIzaSyAh8NZbdmHX8sCQCxlSeIPC-HLy2ZssVW8" 

def recognize_with_google_vision(image_data):
    """
    Recognizes handwriting from an image using the Google Cloud Vision API with an API Key.
    """
    try:
        # --- CORRECTED LOGIC ---
        # This now correctly checks for the default placeholder, not your actual key.
        if not API_KEY or API_KEY == "YOUR_API_KEY":
            st.error("API Key not set! Please add your key to the google_vision_ocr.py file.")
            return None

        # --- CORRECTED LOGIC ---
        # This should use the variable API_KEY, not the hardcoded string.
        client_options = ClientOptions(api_key=API_KEY)
        client = vision.ImageAnnotatorClient(client_options=client_options)

        # Convert the numpy image array from the canvas to bytes
        pil_img = Image.fromarray(image_data)
        buf = io.BytesIO()
        pil_img.save(buf, format='PNG')
        content = buf.getvalue()

        image = vision.Image(content=content)

        # Perform handwriting detection
        response = client.document_text_detection(image=image)
        
        if response.error.message:
            raise Exception(f'{response.error.message}')

        if response.full_text_annotation:
            return response.full_text_annotation.text.replace('\n', ' ').strip()
        else:
            return ""
            
    except Exception as e:
        st.error(f"An error occurred with the Google Vision API: {e}")
        return None