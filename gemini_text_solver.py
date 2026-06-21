from google import genai
from google.genai import types
import os
import base64
import io
from PIL import Image

# --- Client & Model ---
_client = None
MODEL_NAME = "gemini-2.5-flash"
chat_session = None


def get_client():
    """Lazy-initialize the Gemini client on first use."""
    global _client
    if _client is None:
        _client = genai.Client()
    return _client

# --- Shared Constants ---
MATH_SYSTEM_PROMPT = (
    "You are an expert AI Math Assistant. Explain concepts clearly and step-by-step. "
    "Format output in Markdown. Use LaTeX for math.\n\n"
    "CRITICAL RULES FOR READING HANDWRITTEN MATH:\n"
    "1. A small dot '.' between two digits is ALWAYS a DECIMAL POINT, not multiplication. "
    "   Example: '4.2' means 'four point two' (4.2), NOT '4 multiplied by 2'.\n"
    "2. Multiplication is typically written as '×', '·' (centered dot), or implied by adjacency "
    "   (e.g., '2x'). A dot sitting on the baseline between digits is a DECIMAL.\n"
    "3. When you see something like '4.2 / 7.3', it means the decimal number 4.2 divided by "
    "   the decimal number 7.3.\n"
    "4. NEVER interpret a decimal point as multiplication.\n\n"
    "Always provide the final calculated answer as a clear decimal value at the very end "
    "of your response."
)

SOLVE_PROMPT = (
    "Read this handwritten math expression VERY carefully.\n\n"
    "CRITICAL — DECIMAL vs MULTIPLICATION:\n"
    "- A small dot '.' on the baseline between two digits is a DECIMAL POINT.\n"
    "  Example: '4.2' means four-point-two (4.2), NOT 4 times 2.\n"
    "- Multiplication is shown by '×', a CENTERED dot '·', or by adjacency.\n"
    "- If you see 'a.b' where a and b are digits and the dot is small and low, "
    "  it is ALWAYS a decimal: a.b (e.g., 4.2, 7.3, 3.14).\n\n"
    "STEP 1: Write 'DETECTED: [expression]' using EXACT decimal notation as written. "
    "Use '/' for division, '+' for addition, '-' for subtraction, '×' for multiplication. "
    "Use '.' ONLY for decimal points.\n\n"
    "STEP 2: Solve it step-by-step.\n\n"
    "STEP 3: Provide the final answer as a decimal value.\n\n"
    "VALIDATION: Before responding, re-check — did you accidentally interpret any "
    "decimal point as multiplication? If so, correct it."
)

CHAT_IMAGE_PROMPT = (
    "Read this math expression carefully. "
    "CRITICAL: A dot between digits is a DECIMAL POINT (e.g., 4.2 means four-point-two), "
    "NOT multiplication. Solve it step-by-step, and include the final answer as a decimal value."
)


# --- Helpers ---
def strip_base64_header(b64_string: str) -> str:
    """Remove the 'data:...;base64,' prefix from a base64 data URI if present."""
    if "," in b64_string:
        return b64_string.split(",", 1)[1]
    return b64_string


def decode_base64_image(b64_string: str) -> Image.Image:
    """Decode a base64 string (with or without data URI header) into a PIL RGB Image."""
    raw = strip_base64_header(b64_string)
    img_bytes = base64.b64decode(raw)
    return Image.open(io.BytesIO(img_bytes)).convert('RGB')


# --- Chat Session ---
def init_chat_session():
    global chat_session
    chat_session = get_client().chats.create(
        model=MODEL_NAME,
        config={'system_instruction': MATH_SYSTEM_PROMPT}
    )
    return True


def get_chat_response(user_message: str, image_b64: str = None, audio_b64: str = None) -> str:
    global chat_session
    if chat_session is None:
        init_chat_session()

    contents = []

    # Default prompt when only an image is sent with no text
    if not user_message and image_b64 and not audio_b64:
        user_message = CHAT_IMAGE_PROMPT

    if user_message:
        contents.append(user_message)

    if image_b64:
        contents.append(decode_base64_image(image_b64))

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


# --- Whiteboard Solver ---
def solve_math_image_with_gemini(pil_image) -> tuple:
    response = get_client().models.generate_content(
        model=MODEL_NAME,
        contents=[SOLVE_PROMPT, pil_image],
        config=types.GenerateContentConfig(
            system_instruction=MATH_SYSTEM_PROMPT
        )
    )
    full_text = response.text
    detected, solution = "Complex Expression", full_text
    if "DETECTED:" in full_text:
        parts = full_text.split("DETECTED:", 1)[1].split('\n', 1)
        detected = parts[0].strip()
        solution = parts[1].strip() if len(parts) > 1 else full_text
    return detected, solution