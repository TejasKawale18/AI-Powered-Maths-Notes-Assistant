from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from PIL import Image
import io
import base64

load_dotenv()

# Import BOTH functions from our solver file
from gemini_text_solver import solve_math_image_with_gemini, get_chat_response

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('premium.html')

@app.route('/solve', methods=['POST'])
def solve_math():
    try:
        data = request.json
        image_b64 = data['image'].split(',')[1] 
        
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        detected_expr, solution = solve_math_image_with_gemini(image)

        return jsonify({
            "cleaned_expr": detected_expr,
            "solution": solution
        })

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        
        # Ensure we safely grab the text, and remove empty spaces
        user_message = data.get('message', '').strip()
        image_b64 = data.get('image', None)
        audio_b64 = data.get('audio', None)
        
        # Only throw an error if ALL THREE are completely empty
        if not user_message and not image_b64 and not audio_b64:
            return jsonify({"error": "Please provide a text message, an image, or a voice note."})

        # Send the data to Gemini
        ai_response = get_chat_response(user_message, image_b64, audio_b64)

        return jsonify({
            "response": ai_response
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)