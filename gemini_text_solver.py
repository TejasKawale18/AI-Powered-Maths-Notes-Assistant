from google import genai
import os

# --- Initialize Client ---
# The client automatically picks up the API key from the GEMINI_API_KEY environment variable.
# It's best practice not to hardcode the API key in the file.
try:
    # Attempt to initialize the client using the environment variable
    client = genai.Client()
except Exception as e:
    print(f"Gemini client initialization failed. Is GEMINI_API_KEY set? Error: {e}")
    client = None

# We use the Pro model for its superior reasoning and step-by-step formatting
MODEL_NAME = "gemini-2.5-flash" 

def solve_math_text_with_gemini(math_expression: str) -> str:
    """
    Sends a cleaned math expression string to Gemini for a step-by-step solution.
    """
    if client is None:
        return "❌ ERROR: Gemini API Client not initialized. Please set GEMINI_API_KEY environment variable."

    if not math_expression:
        return "⚠️ Received an empty math expression."

    # This system instruction guides the model to act as a math tutor and format the output clearly
    system_instruction = (
        "You are an expert math solver and tutor. The user will provide a mathematical "
        "expression. Your task is to: 1. Acknowledge the problem. 2. Solve the problem "
        "step-by-step, showing all necessary calculations and reasoning, following the "
        "correct order of operations (PEMDAS/BODMAS). 3. Provide the final, numerical "
        "simplified answer. You MUST format your entire response using clear markdown "
        "headings and lists for readability."
    )

    prompt = f"Solve the following math problem step-by-step: {math_expression}"
    
    try:
        # Call the Gemini API
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={'system_instruction': system_instruction}
        )
        
        # The .text attribute contains the model's markdown-formatted response
        return response.text

    except Exception as e:
        return f"❌ Gemini API Execution Error: {e}"