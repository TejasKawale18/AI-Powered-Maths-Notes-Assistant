from google import genai
from google.genai import types
import os
import base64
import io
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()
MODEL_NAME = "gemini-2.5-flash" 
chat_session = None

def init_chat_session():
    global chat_session
    system_instruction = (
        "You are an expert AI Math Assistant. Explain concepts clearly and step-by-step. "
        "Format output in Markdown. Use LaTeX for math."
    )
    chat_session = client.chats.create(model=MODEL_NAME, config={'system_instruction': system_instruction})
    return True

def get_chat_response(user_message: str, image_b64: str = None, audio_b64: str = None) -> str:
    global chat_session
    if chat_session is None: init_chat_session()

    contents = []

    # --- THE UPDATED FIX ---
    # Only inject the default prompt if it's an IMAGE with no text.
    # If there is audio, the audio IS the message, so we let Gemini listen to it directly!
    if not user_message:
        if image_b64 and not audio_b64:
            user_message = "Please analyze the attached image and solve the math problems in it step-by-step."
    # -----------------------

    if user_message: 
        contents.append(user_message)
    
    if image_b64:
        if "," in image_b64: image_b64 = image_b64.split(",", 1)[1]
        img_bytes = base64.b64decode(image_b64)
        contents.append(Image.open(io.BytesIO(img_bytes)).convert('RGB'))

    if audio_b64:
        mime_type = "audio/webm"
        if "," in audio_b64:
            mime_header, b64_data = audio_b64.split(",", 1)
            mime_type = mime_header.split(":")[1].split(";")[0]
            audio_bytes = base64.b64decode(b64_data)
        else:
            audio_bytes = base64.b64decode(audio_b64)
        contents.append(types.Part.from_bytes(data=audio_bytes, mime_type=mime_type))

    response = chat_session.send_message(contents)
    return response.text

def solve_math_image_with_gemini(pil_image) -> tuple:
    prompt = "Read this math. Write 'DETECTED: [expression]' then solve step-by-step."
    response = client.models.generate_content(model=MODEL_NAME, contents=[prompt, pil_image])
    full_text = response.text
    detected, solution = "Complex Expression", full_text
    if "DETECTED:" in full_text:
        parts = full_text.split("DETECTED:", 1)[1].split('\n', 1)
        detected = parts[0].strip()
        solution = parts[1].strip() if len(parts) > 1 else full_text
    return detected, solution