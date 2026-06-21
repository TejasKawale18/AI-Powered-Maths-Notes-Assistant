from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# Import functions and helpers from our solver module
from gemini_text_solver import solve_math_image_with_gemini, get_chat_response, decode_base64_image

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('premium.html')

@app.route('/solve', methods=['POST'])
def solve_math():
    try:
        data = request.json
        image_b64 = data['image']
        image = decode_base64_image(image_b64)

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

        # Safely grab inputs, strip whitespace from text
        user_message = data.get('message', '').strip()
        image_b64 = data.get('image', None)
        audio_b64 = data.get('audio', None)

        # Require at least one input
        if not user_message and not image_b64 and not audio_b64:
            return jsonify({"error": "Please provide a text message, an image, or a voice note."})

        ai_response = get_chat_response(user_message, image_b64, audio_b64)

        return jsonify({
            "response": ai_response
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)